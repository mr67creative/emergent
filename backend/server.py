import os
import secrets
import uuid
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from fastapi import FastAPI, APIRouter, Depends, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field, HttpUrl, ConfigDict, model_validator
from view_flows import install_view_routes
from pymongo import ReturnDocument
from sample_data import INSIGHTS, REVIEWS, new_profile, feature_defaults

load_dotenv(Path(__file__).parent / '.env')
client = AsyncIOMotorClient(os.environ['MONGO_URL'])
db = client[os.environ['DB_NAME']]
app = FastAPI(title='MeanTime Simulation API')
api = APIRouter(prefix='/api')
app.add_middleware(CORSMiddleware, allow_origins=os.environ['CORS_ORIGINS'].split(','), allow_methods=['GET','POST','PUT','DELETE'], allow_headers=['Content-Type','X-Demo-Token'])

class State(BaseModel):
    profile: dict
    insights: list[dict]
    campaigns: list[dict]
    submissions: list[dict]
    reviews: list[dict]
    simulation: bool = True
    credited_mills: int = 0

class Session(BaseModel):
    token: str

async def owner(x_demo_token: str = Header(...)):
    document = await db.sessions.find_one({'token': x_demo_token}, {'_id': 0})
    if not document:
        raise HTTPException(401, 'Session expired. Reload to reconnect.')
    for key, value in feature_defaults().items():
        if key not in document['profile']:
            await db.sessions.update_one({'token': x_demo_token, f'profile.{key}': {'$exists': False}}, {'$set': {f'profile.{key}': value}})
    for key,value in {'placement':'under_prompt','display_mode':'persist_until_5s'}.items():
        await db.sessions.update_one({'token':x_demo_token, f'profile.extension.{key}':{'$exists':False}}, {'$set':{f'profile.extension.{key}':value}})
    document = await db.sessions.find_one({'token': x_demo_token}, {'_id': 0})
    return document

async def state_for(token):
    session = await db.sessions.find_one({'token': token}, {'_id': 0, 'token': 0})
    campaigns = await db.campaigns.find({'owner': token}, {'_id': 0, 'owner': 0}).to_list(100)
    submissions = await db.submissions.find({'owner': token}, {'_id': 0, 'owner': 0}).to_list(100)
    reviewed = session['profile']['reviewed']
    reviews = [r for r in REVIEWS if r['id'] not in reviewed]
    for c in campaigns:
        if c['status'] == 'pending':
            reviews.append({'id': c['id'], 'kind': 'ad', 'brand': c['name'], **c['variants'][0], 'risk': 22, 'fraud': 12, 'copy': 38, 'url_safety': 99})
    for s in submissions:
        if s['status'] == 'pending':
            reviews.append({'id': s['id'], 'kind': 'insight', 'brand': 'Your brand', 'headline': s['title'], 'description': s['body'], 'cta': 'Read insight', 'risk': 18, 'fraud': 8, 'copy': 12, 'url_safety': 99})
    published = [{'id': s['id'], 'title': s['title'], 'topic': s['topic'], 'seconds': 60, 'body': s['body'], 'source': s['source'], 'author': 'Your brand', 'likes': 0, 'visual': 'systems'} for s in submissions if s['status'] == 'approved']
    session['profile']['claims'] = {k:v for k,v in session['profile']['claims'].items() if k != 'boost'}
    return State(profile=session['profile'], insights=INSIGHTS + published, campaigns=campaigns, submissions=submissions, reviews=reviews)

@api.get('/')
async def health():
    return {'name': 'MeanTime', 'mode': 'simulation'}

class JoinSession(BaseModel):
    referral_code: str | None = Field(default=None, max_length=32)

@api.post('/session', response_model=Session)
async def create_session(payload: JoinSession | None = None):
    token = secrets.token_urlsafe(32)
    doc = {'token': token, 'profile': new_profile(), 'created_at': datetime.now(timezone.utc).isoformat()}
    if payload and payload.referral_code:
        referrer = await db.sessions.find_one({'profile.referral_code':payload.referral_code}, {'_id':0, 'token':1})
        if referrer:
            referral_id = str(uuid.uuid4())
            doc.update(referred_by=referrer['token'], referral_id=referral_id)
            await db.sessions.update_one({'token':referrer['token']}, {'$push':{'profile.referrals':{'id':referral_id,'name':'New member','verified_mills':0,'claimed':False,'sample':False}}})
    await db.sessions.insert_one(doc)
    return Session(token=token)

@api.get('/state', response_model=State)
async def get_state(session=Depends(owner)):
    return await state_for(session['token'])

class Withdrawal(BaseModel):
    amount_mills: int | None = Field(default=None, ge=5000)

@api.post('/withdraw', response_model=State)
async def withdraw(payload: Withdrawal | None = None, session=Depends(owner)):
    balance = session['profile']['balance_mills']
    amount = payload.amount_mills if payload and payload.amount_mills is not None else balance
    if amount < 5000:
        raise HTTPException(400, 'Minimum balance is $5.00.')
    if amount > balance:
        raise HTTPException(400, 'Amount exceeds your available balance.')
    transaction = {'id': str(uuid.uuid4()), 'kind':'payout', 'method':session['profile']['payout_method'], 'amount_mills': amount, 'date': datetime.now(timezone.utc).isoformat(), 'status': 'Simulated'}
    result = await db.sessions.update_one({'token': session['token'], 'profile.balance_mills': {'$gte':amount}}, {'$inc': {'profile.balance_mills': -amount}, '$push': {'profile.transactions': transaction}})
    if not result.modified_count:
        raise HTTPException(409, 'Balance changed. Please try again.')
    return await state_for(session['token'])

TOPICS = ['AI / ML','Programming','Hardware','Cybersecurity','Science','Finance','Systems','Math','Startups']
class Interest(BaseModel):
    topic: str
    discovered: bool = False

@api.post('/interests', response_model=State)
async def toggle_interest(payload: Interest, session=Depends(owner)):
    if payload.topic not in TOPICS:
        raise HTTPException(400, 'Unknown topic.')
    if payload.discovered:
        update = {'$unset': {f'profile.discovered.{payload.topic}': ''}}
    else:
        op = '$pull' if payload.topic in session['profile']['interests'] else '$addToSet'
        update = {op: {'profile.interests': payload.topic}}
    await db.sessions.update_one({'token': session['token']}, update)
    return await state_for(session['token'])

@api.post('/interests/reset', response_model=State)
async def reset_discovered(session=Depends(owner)):
    await db.sessions.update_one({'token': session['token']}, {'$set': {'profile.discovered': {}}})
    return await state_for(session['token'])

class InsightAction(BaseModel):
    action: Literal['bookmark','upvote','read','source']

@api.post('/insights/{insight_id}/action', response_model=State)
async def insight_action(insight_id: str, payload: InsightAction, session=Depends(owner)):
    insight = next((i for i in INSIGHTS if i['id'] == insight_id), None)
    if not insight:
        custom = await db.submissions.find_one({'id': insight_id, 'owner': session['token'], 'status': 'approved'}, {'_id': 0, 'owner': 0})
        if not custom:
            raise HTTPException(404, 'Insight not found.')
        insight = custom
    key = {'bookmark': 'bookmarks', 'upvote': 'upvotes', 'read': 'reads', 'source': 'source_clicks'}[payload.action]
    field = f'profile.{key}'
    existing = insight_id in session['profile'][key]
    if payload.action in ['read', 'source'] and existing:
        return await state_for(session['token'])
    update = {('$pull' if existing else '$addToSet'): {field: insight_id}}
    if payload.action == 'read':
        update['$inc'] = {f"profile.discovered.{insight['topic']}": 12}
    predicate = {'token': session['token']}
    if payload.action in ['read', 'source']:
        predicate[field] = {'$ne': insight_id}
    await db.sessions.update_one(predicate, update)
    return await state_for(session['token'])

MILESTONES = {'stickers':100,'tee':500,'hoodie':1000,'desk':2500}
@api.post('/rewards/{reward_id}/claim', response_model=State)
async def claim_reward(reward_id: str, session=Depends(owner)):
    if reward_id not in MILESTONES:
        raise HTTPException(404, 'Reward not found.')
    if session['profile']['views'] < MILESTONES[reward_id]:
        raise HTTPException(400, 'Milestone not reached yet.')
    await db.sessions.update_one({'token':session['token'], f'profile.claims.{reward_id}': {'$exists':False}}, {'$set': {f'profile.claims.{reward_id}': {'step':1, 'date':datetime.now(timezone.utc).isoformat()}}})
    return await state_for(session['token'])

@api.post('/rewards/{reward_id}/advance', response_model=State)
async def advance_reward(reward_id: str, session=Depends(owner)):
    if reward_id not in MILESTONES or reward_id not in session['profile']['claims']:
        raise HTTPException(400, 'Claim this reward first.')
    await db.sessions.update_one({'token': session['token'], f'profile.claims.{reward_id}.step': {'$lt':3}}, {'$inc': {f'profile.claims.{reward_id}.step':1}})
    return await state_for(session['token'])

class Variant(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    headline: str = Field(min_length=1, max_length=70)
    description: str = Field(min_length=1, max_length=140)
    cta: str = Field(min_length=1, max_length=20)

class Campaign(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    name: str = Field(min_length=1, max_length=70)
    variants: list[Variant] = Field(min_length=3, max_length=3)
    topics: list[Literal['AI / ML','DevTools','Cloud','Hardware','Science','Finance']] = Field(min_length=1, max_length=6)
    bid: float = Field(ge=0.010, le=0.050)
    budget: int = Field(ge=10, le=1000)
    url: HttpUrl
    status: Literal['draft','pending'] = 'draft'
    duration_seconds: int = Field(default=5, ge=2, le=15)
    countries: list[str] = Field(default_factory=list, max_length=30)

@api.put('/campaigns/{campaign_id}', response_model=State)
async def save_campaign(campaign_id: str, payload: Campaign, session=Depends(owner)):
    if len(campaign_id) > 100:
        raise HTTPException(400, 'Invalid campaign ID.')
    data = payload.model_dump(mode='json')
    data.update(id=campaign_id, owner=session['token'], updated_at=datetime.now(timezone.utc).isoformat())
    await db.campaigns.update_one({'id':campaign_id, 'owner': session['token']}, {'$set': data}, upsert=True)
    return await state_for(session['token'])

@api.delete('/campaigns/{campaign_id}', response_model=State)
async def delete_campaign(campaign_id: str, session=Depends(owner)):
    await db.campaigns.delete_one({'id':campaign_id, 'owner':session['token']})
    return await state_for(session['token'])

class Submission(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    title: str = Field(min_length=5, max_length=100)
    body: str = Field(min_length=40, max_length=5000)
    topic: Literal['AI / ML','Systems','Hardware','Math','Startups','Programming']
    source: HttpUrl

@api.post('/insights/submit', response_model=State)
async def submit_insight(payload: Submission, session=Depends(owner)):
    data = payload.model_dump(mode='json')
    data.update(id=str(uuid.uuid4()), owner=session['token'], status='pending', created_at=datetime.now(timezone.utc).isoformat())
    await db.submissions.insert_one(data)
    return await state_for(session['token'])

class Decision(BaseModel):
    decision: Literal['approved','rejected']

@api.post('/reviews/{review_id}', response_model=State)
async def review(review_id: str, payload: Decision, session=Depends(owner)):
    current = await state_for(session['token'])
    item = next((r for r in current.reviews if r['id'] == review_id), None)
    if not item:
        raise HTTPException(404, 'Review already resolved.')
    if item['risk'] >= 85 and payload.decision == 'approved':
        raise HTTPException(400, 'High-risk creative cannot be approved.')
    await db.sessions.update_one({'token':session['token']}, {'$addToSet': {'profile.reviewed':review_id}, '$push': {'profile.decisions': {'id':review_id, 'decision':payload.decision}}})
    for collection in ['campaigns','submissions']:
        await db[collection].update_one({'id':review_id, 'owner':session['token']}, {'$set': {'status':payload.decision}})
    return await state_for(session['token'])

class PayoutMethod(BaseModel):
    method: Literal['demo-bank','demo-wallet']

@api.put('/payouts/settings', response_model=State)
async def payout_settings(payload: PayoutMethod, session=Depends(owner)):
    await db.sessions.update_one({'token':session['token']}, {'$set':{'profile.payout_method':payload.method}})
    return await state_for(session['token'])

class ExtensionSettings(BaseModel):
    enabled: bool
    mode: Literal['ads','insights']
    platforms: list[Literal['ChatGPT','Claude','Gemini','DeepSeek','Grok']] = Field(max_length=5)
    placement: Literal['under_prompt','above_composer'] = 'under_prompt'
    display_mode: Literal['wait_time_only','persist_until_5s'] = 'persist_until_5s'

@api.put('/extension/settings', response_model=State)
async def extension_settings(payload: ExtensionSettings, session=Depends(owner)):
    await db.sessions.update_one({'token':session['token']}, {'$set':{'profile.extension':payload.model_dump()}})
    return await state_for(session['token'])

@api.post('/referrals/{referral_id}/activity', response_model=State)
async def referral_activity(referral_id: str, session=Depends(owner)):
    ref = next((r for r in session['profile']['referrals'] if r['id']==referral_id), None)
    if not ref:
        raise HTTPException(404, 'Referral not found.')
    if not ref.get('sample'):
        raise HTTPException(400, 'This referral updates from actual simulator activity.')
    await db.sessions.update_one({'token':session['token'], 'profile.referrals':{'$elemMatch':{'id':referral_id,'verified_mills':{'$lt':3900}}}}, {'$inc':{'profile.referrals.$.verified_mills':350}})
    return await state_for(session['token'])

@api.post('/referrals/{referral_id}/claim', response_model=State)
async def referral_claim(referral_id: str, session=Depends(owner)):
    ref = next((r for r in session['profile']['referrals'] if r['id']==referral_id), None)
    if not ref:
        raise HTTPException(404, 'Referral not found.')
    if ref['verified_mills'] < 3900:
        raise HTTPException(400, 'This referral has not qualified yet.')
    transaction = {'id':str(uuid.uuid4()),'kind':'referral','amount_mills':1000,'date':datetime.now(timezone.utc).isoformat(),'status':'Simulated'}
    result = await db.sessions.update_one({'token':session['token'], 'profile.referrals':{'$elemMatch':{'id':referral_id,'verified_mills':{'$gte':3900},'claimed':False}}}, {'$set':{'profile.referrals.$.claimed':True}, '$inc':{'profile.balance_mills':1000,'profile.referral_earned_mills':1000}, '$push':{'profile.transactions':transaction}})
    if not result.modified_count:
        raise HTTPException(409, 'Referral reward already claimed.')
    return await state_for(session['token'])

class DestinationDetails(BaseModel):
    model_config=ConfigDict(str_strip_whitespace=True)
    method: Literal['demo-bank','demo-wallet']
    label: str = Field(min_length=2,max_length=50)
    holder: str = Field(default='',max_length=80)
    bank: str = Field(default='',max_length=80)
    last4: str = Field(default='',max_length=4)
    address: str = Field(default='',max_length=120)

    @model_validator(mode='after')
    def validate_details(self):
        if self.method=='demo-bank' and (not self.holder or not self.bank or len(self.last4)!=4 or not self.last4.isdigit()):
            raise ValueError('Enter the account holder, bank name, and last four digits only.')
        if self.method=='demo-wallet' and not self.address:
            raise ValueError('Enter a demo wallet address or email.')
        return self

@api.put('/payouts/destination', response_model=State)
async def save_destination(payload: DestinationDetails, session=Depends(owner)):
    details=payload.model_dump(exclude={'method'})
    await db.sessions.update_one({'token':session['token']},{'$set':{f'profile.payout_destinations.{payload.method}':details,'profile.payout_method':payload.method}})
    return await state_for(session['token'])

install_view_routes(api,db,owner,state_for,State)
app.include_router(api)

@app.on_event('startup')
async def indexes():
    await db.sessions.create_index('token', unique=True)
    await db.sessions.create_index('profile.referral_code', unique=True, sparse=True)
    for collection in ['campaigns', 'submissions']:
        await db[collection].create_index([('owner',1),('id',1)], unique=True)

@app.on_event('shutdown')
async def shutdown():
    client.close()