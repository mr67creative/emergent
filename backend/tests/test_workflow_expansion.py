# Workflow expansion: manual campaign views, exact-once receipts, cancellation, destinations.
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
import threading
import pytest
import requests
from test_meantime import BASE, sandbox, cleanup, state as raw_state, campaign

def state(s):
    data=raw_state(s)
    data['profile']['events']=[e for e in data['profile']['events'] if not e.get('sample')]
    return data

def start(s, **kwargs):
    r=s.post(BASE+'/charges/start',json=kwargs,timeout=20)
    assert r.status_code==200, r.text
    c=r.json()
    assert isinstance(c['id'],str)
    if not kwargs.get('campaign_id'):
        assert c['required_seconds']==kwargs.get('duration_seconds',5)
    return c

def finish(s,c):
    return s.post(BASE+'/charges/complete',json={'id':c['id']},timeout=20)

def saved_campaign(s,duration=8):
    cid='TEST_'+str(uuid.uuid4()); data=campaign()
    data.update(duration_seconds=duration,countries=['India','United States of America'],bid=.04)
    r=s.put(BASE+'/campaigns/'+cid,json=data,timeout=20)
    assert r.status_code==200
    assert next(c for c in state(s)['campaigns'] if c['id']==cid)['duration_seconds']==duration
    return cid,data

def test_default_threshold_and_exact_once(sandbox):
    before=state(sandbox)['profile']; c=start(sandbox)
    assert c['required_seconds']==5 and c['credit_mills']==11
    r=finish(sandbox,c); assert r.status_code==409 and 'incomplete' in r.json()['detail']
    time.sleep(5.1); r=finish(sandbox,c)
    assert r.status_code==200 and r.json()['credited_mills']==11
    p=state(sandbox)['profile']
    assert (p['balance_mills'],p['views'])==(before['balance_mills']+11,before['views']+1)
    assert len(p['events'])==1 and p['events'][0]['required_seconds']==5
    assert finish(sandbox,c).status_code==409 and len(state(sandbox)['profile']['events'])==1

@pytest.mark.parametrize('duration',[2,15])
def test_duration_boundaries(sandbox,duration):
    c=start(sandbox,duration_seconds=duration,response_seconds=2)
    assert finish(sandbox,c).status_code==409
    time.sleep(duration+.1); r=finish(sandbox,c)
    assert r.status_code==200 and r.json()['credited_mills']==11
    e=state(sandbox)['profile']['events'][0]
    assert e['watched_seconds']==duration and e['status']=='credited'

def test_selected_campaign_not_forged_and_persistence(sandbox):
    cid,data=saved_campaign(sandbox)
    c=start(sandbox,campaign_id=cid,variant_index=2,duration_seconds=2,response_seconds=3)
    assert (c['required_seconds'],c['bid'],c['credit_mills'],c['title'])==(8,.04,22,'TEST_variant_2')
    time.sleep(3.1); assert finish(sandbox,c).status_code==409
    time.sleep(5); r=finish(sandbox,c)
    assert r.status_code==200 and r.json()['credited_mills']==22
    e=state(sandbox)['profile']['events'][0]
    assert e['variant']=='C' and e['campaign_id']==cid and e['bid']==.04 and e['required_seconds']==8
    data.update(duration_seconds=15,countries=['France']); sandbox.put(BASE+'/campaigns/'+cid,json=data,timeout=20)
    got=next(c for c in state(sandbox)['campaigns'] if c['id']==cid)
    assert got['duration_seconds']==15 and got['countries']==['France']
    sandbox.delete(BASE+'/campaigns/'+cid,timeout=20)
    assert not any(c['id']==cid for c in state(sandbox)['campaigns'])

def test_early_wait_only_never_pays(sandbox):
    cid,_=saved_campaign(sandbox)
    before=state(sandbox)['profile']; c=start(sandbox,campaign_id=cid,response_seconds=3,display_mode='wait_time_only')
    time.sleep(8.1); r=finish(sandbox,c)
    assert r.status_code==409 and 'AI response ended' in r.json()['detail']
    r=sandbox.post(BASE+'/charges/cancel',json={'id':c['id'],'reason':'below_threshold'},timeout=20)
    assert r.status_code==200
    p=state(sandbox)['profile']; e=p['events'][0]
    assert p['balance_mills']==before['balance_mills'] and p['views']==before['views']
    assert e['amount_mills']==0 and e['watched_seconds']==3 and e['status']=='below_threshold'

def test_wait_only_long_response_pays(sandbox):
    c=start(sandbox,duration_seconds=2,response_seconds=3,display_mode='wait_time_only')
    time.sleep(2.1); r=finish(sandbox,c)
    assert r.status_code==200 and r.json()['credited_mills']==11
    assert state(sandbox)['profile']['events'][0]['status']=='credited'

def test_insight_zero_money_response_threshold(sandbox):
    before=state(sandbox)['profile']; c=start(sandbox,kind='insight',duration_seconds=2,response_seconds=3)
    time.sleep(2.1); assert finish(sandbox,c).status_code==409
    time.sleep(1.1); r=finish(sandbox,c)
    assert r.status_code==200 and r.json()['credited_mills']==0
    p=state(sandbox)['profile']
    assert p['balance_mills']==before['balance_mills'] and p['views']==before['views'] and p['seconds']==before['seconds']+3
    assert p['events'][0]['kind']=='insight' and p['events'][0]['status']=='insight'

def test_cancellation_reasons_and_clicks(sandbox):
    before=state(sandbox)['profile']
    for reason in ['dismissed','window_blurred','navigation']:
        c=start(sandbox,duration_seconds=2)
        r=sandbox.post(BASE+f"/charges/{c['id']}/click",timeout=20)
        assert r.status_code==200
        r=sandbox.post(BASE+'/charges/cancel',json={'id':c['id'],'reason':reason},timeout=20)
        assert r.status_code==200
        assert finish(sandbox,c).status_code==409
        sandbox.post(BASE+'/charges/cancel',json={'id':c['id'],'reason':reason},timeout=20)
    p=state(sandbox)['profile']
    assert len(p['events'])==3 and all(e['clicked'] and e['amount_mills']==0 for e in p['events'])
    assert p['balance_mills']==before['balance_mills'] and p['views']==before['views']
    assert {e['status'] for e in p['events']}=={'dismissed','window_blurred','navigation'}

def test_parallel_complete_exact_once(sandbox):
    c=start(sandbox,duration_seconds=2); time.sleep(2.1)
    token=sandbox.headers['X-Demo-Token']; barrier=threading.Barrier(6)
    def call(_):
        barrier.wait()
        return requests.post(BASE+'/charges/complete',headers={'X-Demo-Token':token},json={'id':c['id']},timeout=20)
    with ThreadPoolExecutor(max_workers=6) as pool: results=list(pool.map(call,range(6)))
    assert sorted(r.status_code for r in results)==[200,409,409,409,409,409]
    p=state(sandbox)['profile']; assert len(p['events'])==1 and p['balance_mills']==14861 and p['views']==343

def test_parallel_complete_cancel_race(sandbox):
    before=state(sandbox)['profile']; token=sandbox.headers['X-Demo-Token']
    for _ in range(3):
        c=start(sandbox,duration_seconds=2); time.sleep(2.1); barrier=threading.Barrier(2)
        def call(endpoint):
            barrier.wait(); payload={'id':c['id']}
            if endpoint=='cancel': payload['reason']='dismissed'
            return endpoint,requests.post(BASE+'/charges/'+endpoint,headers={'X-Demo-Token':token},json=payload,timeout=20)
        with ThreadPoolExecutor(max_workers=2) as pool: results=dict(pool.map(call,['complete','cancel']))
        assert results['cancel'].status_code==200 and results['complete'].status_code in [200,409]
        events=[e for e in state(sandbox)['profile']['events'] if e['id']==c['id']]
        assert len(events)==1 and events[0]['status'] in ['credited','dismissed']
    p=state(sandbox)['profile']; paid=sum(e['status']=='credited' for e in p['events'])
    assert p['balance_mills']==before['balance_mills']+11*paid and p['views']==before['views']+paid

def test_view_validation(sandbox):
    for key,value in [('duration_seconds',1),('duration_seconds',16),('response_seconds',1),('response_seconds',31),('variant_index',-1),('variant_index',3),('display_mode','bad'),('kind','bad'),('platform','bad'),('slot',0),('country','')]:
        r=sandbox.post(BASE+'/charges/start',json={key:value},timeout=20)
        assert r.status_code==422 and isinstance(r.json()['detail'],list), r.text
    r=sandbox.post(BASE+'/charges/start',json={'campaign_id':'TEST_missing'},timeout=20)
    assert r.status_code==404 and 'not found' in r.json()['detail']
    assert state(sandbox)['profile']['events']==[]

def test_campaign_duration_validation_defaults(sandbox):
    cid='TEST_'+str(uuid.uuid4()); data=campaign()
    for value in [1,16,5.5]:
        r=sandbox.put(BASE+'/campaigns/'+cid,json={**data,'duration_seconds':value},timeout=20)
        assert r.status_code==422 and isinstance(r.json()['detail'],list)
    sandbox.put(BASE+'/campaigns/'+cid,json=data,timeout=20)
    c=next(c for c in state(sandbox)['campaigns'] if c['id']==cid)
    assert c['duration_seconds']==5 and c['countries']==[]

def test_extension_extended_settings(sandbox):
    for placement,mode in [('above_composer','wait_time_only'),('under_prompt','persist_until_5s')]:
        settings={'enabled':False,'mode':'insights','platforms':['Grok'],'placement':placement,'display_mode':mode}
        r=sandbox.put(BASE+'/extension/settings',json=settings,timeout=20)
        assert r.status_code==200 and state(sandbox)['profile']['extension']==settings
    r=sandbox.put(BASE+'/extension/settings',json={**settings,'placement':'bad'},timeout=20)
    assert r.status_code==422 and isinstance(r.json()['detail'],list)

def test_bank_wallet_destinations_private(sandbox):
    for data in [dict(method='demo-bank',label='TEST_bank',holder='TEST_Holder',bank='TEST_Bank',last4='1234'),dict(method='demo-wallet',label='TEST_wallet',address='TEST_wallet@example.org')]:
        r=sandbox.put(BASE+'/payouts/destination',json=data,timeout=20)
        assert r.status_code==200
        p=state(sandbox)['profile']; dest=p['payout_destinations'][data['method']]
        assert p['payout_method']==data['method'] and all(dest[k]==v for k,v in data.items() if k!='method')
    from test_meantime import TOKENS
    other=requests.Session(); token=other.post(BASE+'/session',timeout=20).json()['token']; TOKENS.append(token); other.headers['X-Demo-Token']=token
    assert 'TEST_bank' not in str(state(other)['profile']['payout_destinations'])
    assert 'TEST_wallet' not in str(state(other)['profile']['payout_destinations'])

def test_destination_validation(sandbox):
    bank=dict(method='demo-bank',label='TEST_bank',holder='TEST_Holder',bank='TEST_Bank',last4='1234')
    for key,value in [('holder',''),('bank',''),('last4','abcd'),('last4','12345'),('label','x')]:
        r=sandbox.put(BASE+'/payouts/destination',json={**bank,key:value},timeout=20)
        assert r.status_code==422 and isinstance(r.json()['detail'],list)
    r=sandbox.put(BASE+'/payouts/destination',json=dict(method='demo-wallet',label='TEST_wallet',address=''),timeout=20)
    assert r.status_code==422 and isinstance(r.json()['detail'],list)