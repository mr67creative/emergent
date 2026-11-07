# MeanTime private sandbox APIs: earnings, insights, rewards, studio and moderation.
import os
import time
import uuid
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import pytest
import requests
from dotenv import load_dotenv

load_dotenv('/app/frontend/.env')
BASE = os.environ['REACT_APP_BACKEND_URL'].rstrip('/') + '/api'
TOKENS = []

@pytest.fixture
def sandbox():
    s = requests.Session()
    r = s.post(BASE + '/session', timeout=20)
    assert r.status_code == 200 and isinstance(r.json()['token'], str)
    token = r.json()['token']
    TOKENS.append(token)
    s.headers['X-Demo-Token'] = token
    return s

@pytest.fixture(scope='session', autouse=True)
def cleanup():
    yield
    # Remove only sessions and records created by this test run, never seeded data.
    from pymongo import MongoClient
    load_dotenv('/app/backend/.env')
    c = MongoClient(os.environ['MONGO_URL'])
    db = c[os.environ['DB_NAME']]
    for token in TOKENS:
        db.sessions.delete_one({'token': token})
        for collection in ['campaigns', 'submissions']:
            db[collection].delete_many({'owner': token})
    c.close()

def state(s):
    r = s.get(BASE + '/state', timeout=20)
    assert r.status_code == 200
    return r.json()

def campaign():
    return {'name':'TEST_campaign', 'variants':[{'headline':f'TEST_variant_{n}', 'description':'A test description', 'cta':'TEST_go'} for n in range(3)], 'topics':['AI / ML'], 'bid':.02, 'budget':100, 'url':'https://example.org', 'status':'draft'}

def test_health():
    r = requests.get(BASE + '/', timeout=20)
    assert r.status_code == 200 and r.json() == {'name':'MeanTime','mode':'simulation'}

def test_session_defaults_and_headers(sandbox):
    p = state(sandbox)['profile']
    assert p['balance_mills'] == 14850 and p['views'] == 342
    assert state(sandbox)['simulation'] is True
    assert requests.get(BASE+'/state', timeout=20).status_code == 422
    r = requests.get(BASE+'/state', headers={'X-Demo-Token':'invalid'}, timeout=20)
    assert r.status_code == 401 and 'Session expired' in r.json()['detail']

def test_charge_timing_duplicate_and_values(sandbox):
    before = state(sandbox)['profile']
    r = sandbox.post(BASE+'/charges/start', timeout=20)
    assert r.status_code == 200 and r.json()['id']
    charge = {'id':r.json()['id']}
    early = sandbox.post(BASE+'/charges/complete', json=charge, timeout=20)
    assert early.status_code == 409 and 'incomplete' in early.json()['detail']
    time.sleep(5.1)
    r = sandbox.post(BASE+'/charges/complete',json=charge, timeout=20)
    assert r.status_code == 200
    p = state(sandbox)['profile']
    assert (p['balance_mills'],p['views'],p['seconds']) == (14861,343,before['seconds']+5)
    assert sandbox.post(BASE+'/charges/complete',json=charge, timeout=20).status_code == 409

def test_replaced_charge_cannot_complete(sandbox):
    old = sandbox.post(BASE+'/charges/start',timeout=20).json()['id']
    new = sandbox.post(BASE+'/charges/start',timeout=20).json()['id']
    time.sleep(5.1)
    assert old != new
    assert sandbox.post(BASE+'/charges/complete',json={'id':old},timeout=20).status_code == 409
    assert state(sandbox)['profile']['balance_mills'] == 14850

def test_withdraw_persistence_minimum(sandbox):
    r = sandbox.post(BASE+'/withdraw',timeout=20)
    assert r.status_code == 200
    p = state(sandbox)['profile']
    assert p['balance_mills'] == 0 and p['transactions'][0]['amount_mills'] == 14850
    assert p['transactions'][0]['status'] == 'Simulated'
    r = sandbox.post(BASE+'/withdraw',timeout=20)
    assert r.status_code == 400 and '$5.00' in r.json()['detail']

def test_interests_persist_and_validate(sandbox):
    r = sandbox.post(BASE+'/interests',json={'topic':'Finance'},timeout=20)
    assert r.status_code == 200 and 'Finance' in state(sandbox)['profile']['interests']
    sandbox.post(BASE+'/interests',json={'topic':'Finance'},timeout=20)
    assert 'Finance' not in state(sandbox)['profile']['interests']
    assert sandbox.post(BASE+'/interests',json={'topic':'invalid'},timeout=20).status_code == 400

def test_insight_actions_persist_idempotent(sandbox):
    for action in ['bookmark','upvote','read','source']:
        r = sandbox.post(BASE+'/insights/kv-cache/action',json={'action':action},timeout=20)
        assert r.status_code == 200
    p = state(sandbox)['profile']
    for field in ['bookmarks','upvotes','reads','source_clicks']:
        assert 'kv-cache' in p[field]
    sandbox.post(BASE+'/insights/kv-cache/action',json={'action':'read'},timeout=20)
    assert state(sandbox)['profile']['discovered']['AI / ML'] == 12
    assert sandbox.post(BASE+'/insights/invalid/action',json={'action':'read'},timeout=20).status_code == 404

def test_concurrent_read_only_once(sandbox):
    token = sandbox.headers['X-Demo-Token']
    def read(_):
        return requests.post(BASE+'/insights/postgres/action', headers={'X-Demo-Token':token},json={'action':'read'},timeout=20)
    with ThreadPoolExecutor(max_workers=12) as pool:
        results = list(pool.map(read,range(12)))
    assert all(r.status_code == 200 for r in results)
    assert state(sandbox)['profile']['discovered']['Systems'] == 56

def test_reward_claim_shipping_and_lock(sandbox):
    assert sandbox.post(BASE+'/rewards/tee/claim',timeout=20).status_code == 400
    assert sandbox.post(BASE+'/rewards/invalid/claim',timeout=20).status_code == 404
    assert sandbox.post(BASE+'/rewards/stickers/claim',timeout=20).status_code == 200
    for _ in range(3):
        assert sandbox.post(BASE+'/rewards/stickers/advance',timeout=20).status_code == 200
    assert state(sandbox)['profile']['claims']['stickers']['step'] == 3
    sandbox.post(BASE+'/rewards/stickers/claim',timeout=20)
    assert state(sandbox)['profile']['claims']['stickers']['step'] == 3

def test_boost_integer_remainder(sandbox):
    assert sandbox.post(BASE+'/rewards/boost/claim',timeout=20).status_code == 200
    for _ in range(2):
        cid = sandbox.post(BASE+'/charges/start',timeout=20).json()['id']
        time.sleep(5.1)
        assert sandbox.post(BASE+'/charges/complete',json={'id':cid},timeout=20).status_code == 200
    p = state(sandbox)['profile']
    assert p['balance_mills'] == 14873 and p['boost_base_mills'] == 22 and p['boost_remainder_micros'] == 100

def test_campaign_crud_isolation(sandbox):
    cid = 'TEST_'+str(uuid.uuid4())
    data = campaign()
    assert sandbox.put(BASE+'/campaigns/'+cid,json=data,timeout=20).status_code == 200
    assert state(sandbox)['campaigns'][0]['name'] == 'TEST_campaign'
    other = requests.Session()
    token = other.post(BASE+'/session',timeout=20).json()['token']; TOKENS.append(token)
    other.headers['X-Demo-Token'] = token
    assert state(other)['campaigns'] == []
    other.delete(BASE+'/campaigns/'+cid,timeout=20)
    assert state(sandbox)['campaigns'][0]['id'] == cid
    data['budget'] = 250
    sandbox.put(BASE+'/campaigns/'+cid,json=data,timeout=20)
    assert state(sandbox)['campaigns'][0]['budget'] == 250
    sandbox.delete(BASE+'/campaigns/'+cid,timeout=20)
    assert state(sandbox)['campaigns'] == []

def test_campaign_validation(sandbox):
    for key,value in [('url','invalid'),('bid',.051),('budget',1001),('variants',[{'headline':'x'*71,'description':'a','cta':'b'}]*3)]:
        data = campaign(); data[key] = value
        r = sandbox.put(BASE+'/campaigns/TEST_invalid',json=data,timeout=20)
        assert r.status_code == 422 and isinstance(r.json()['detail'],list)
    assert state(sandbox)['campaigns'] == []

def test_campaign_review_status(sandbox):
    data = campaign(); data['status'] = 'pending'
    sandbox.put(BASE+'/campaigns/TEST_review',json=data,timeout=20)
    assert any(r['id']=='TEST_review' for r in state(sandbox)['reviews'])
    r = sandbox.post(BASE+'/reviews/TEST_review',json={'decision':'approved'},timeout=20)
    assert r.status_code == 200 and state(sandbox)['campaigns'][0]['status'] == 'approved'

def test_submission_validation_publish(sandbox):
    data = {'title':'TEST_insight','body':'TEST_An informative technical insight that exceeds forty characters.', 'topic':'Systems','source':'https://example.org/docs'}
    for key,value in [('title','tiny'),('body','short'),('source','invalid')]:
        bad = dict(data);bad[key]=value
        assert sandbox.post(BASE+'/insights/submit',json=bad,timeout=20).status_code == 422
    r = sandbox.post(BASE+'/insights/submit',json=data,timeout=20)
    assert r.status_code == 200
    submission = state(sandbox)['submissions'][0]; sid = submission['id']
    assert submission['status']=='pending' and not any(i['id']==sid for i in state(sandbox)['insights'])
    sandbox.post(BASE+'/reviews/'+sid,json={'decision':'approved'},timeout=20)
    published = next(i for i in state(sandbox)['insights'] if i['id']==sid)
    assert published['title'] == data['title'] and published['source']==data['source']

def test_review_high_risk_and_empty(sandbox):
    r = sandbox.post(BASE+'/reviews/seed-4',json={'decision':'approved'},timeout=20)
    assert r.status_code == 400 and 'High-risk' in r.json()['detail']
    for rid in ['seed-1','seed-2','seed-3','seed-4']:
        assert sandbox.post(BASE+'/reviews/'+rid,json={'decision':'rejected'},timeout=20).status_code == 200
    assert state(sandbox)['reviews'] == []
    assert sandbox.post(BASE+'/reviews/seed-1',json={'decision':'rejected'},timeout=20).status_code == 404