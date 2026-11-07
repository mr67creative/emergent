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
from pydantic import BaseModel, Field, HttpUrl, ConfigDict
from pymongo import ReturnDocument
from sample_data import INSIGHTS, REVIEWS, new_profile

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
    return State(profile=session['profile'], insights=INSIGHTS + published, campaigns=campaigns, submissions=submissions, reviews=reviews)

@api.get('/')
async def health():
    return {'name': 'MeanTime', 'mode': 'simulation'}

@api.post('/session', response_model=Session)
async def create_session():
    token = secrets.token_urlsafe(32)
    await db.sessions.insert_one({'token': token, 'profile': new_profile(), 'created_at': datetime.now(timezone.utc).isoformat()})
    return Session(token=token)

@api.get('/state', response_model=State)
async def get_state(session=Depends(owner)):
    return await state_for(session['token'])

@api.post('/charges/start')
async def start_charge(session=Depends(owner)):
    charge = {'id': str(uuid.uuid4()), 'started_at': datetime.now(timezone.utc).isoformat()}
    await db.sessions.update_one({'token': session['token']}, {'$set': {'charge': charge}})
    return charge

class ChargeComplete(BaseModel):
    id: str

@api.post('/charges/complete', response_model=State)
async def complete_charge(payload: ChargeComplete, session=Depends(owner)):
    cutoff = (datetime.now(timezone.utc) - timedelta(seconds=5)).isoformat()
    profile = session['profile']
    increment = {'profile.balance_mills': 11, 'profile.views': 1, 'profile.seconds': 5}
    update = {'$inc': increment, '$unset': {'charge': ''}}
    if 'boost' in profile['claims'] and profile.get('boost_base_mills', 0) < 30000:
        eligible = min(11, 30000 - profile.get('boost_base_mills', 0))
        micros = profile.get('boost_remainder_micros', 0) + eligible * 50
        increment['profile.balance_mills'] += micros // 1000
        increment['profile.boost_base_mills'] = eligible
        update['$set'] = {'profile.boost_remainder_micros': micros % 1000}
    result = await db.sessions.update_one({'token': session['token'], 'charge.id': payload.id, 'charge.started_at': {'$lte': cutoff}}, update)
    if not result.modified_count:
        raise HTTPException(409, 'Charge incomplete or already credited.')
    result_state = await state_for(session['token'])
    result_state.credited_mills = increment['profile.balance_mills']
    return result_state

@api.post('/withdraw', response_model=State)
async def withdraw(session=Depends(owner)):
    amount = session['profile']['balance_mills']
    if amount < 5000:
        raise HTTPException(400, 'Minimum balance is $5.00.')
    transaction = {'id': str(uuid.uuid4()), 'amount_mills': amount, 'date': datetime.now(timezone.utc).isoformat(), 'status': 'Simulated'}
    result = await db.sessions.update_one({'token': session['token'], 'profile.balance_mills': amount}, {'$inc': {'profile.balance_mills': -amount}, '$push': {'profile.transactions': transaction}})
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

MILESTONES = {'stickers':100,'boost':250,'tee':500,'hoodie':1000,'desk':2500}
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

app.include_router(api)

@app.on_event('startup')
async def indexes():
    await db.sessions.create_index('token', unique=True)
    for collection in ['campaigns', 'submissions']:
        await db[collection].create_index([('owner',1),('id',1)], unique=True)

@app.on_event('shutdown')
async def shutdown():
    client.close()