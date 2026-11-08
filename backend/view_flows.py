"""Simulation view timing and receipts. No ad assignment or A/B testing engine."""
import uuid
from datetime import datetime, timezone, timedelta
from typing import Literal
from fastapi import Depends, HTTPException
from pydantic import BaseModel, Field

class StartView(BaseModel):
    campaign_id: str | None = Field(default=None, max_length=100)
    variant_index: int = Field(default=0, ge=0, le=2)
    duration_seconds: int = Field(default=5, ge=2, le=15)
    response_seconds: int = Field(default=6, ge=2, le=30)
    display_mode: Literal['wait_time_only','persist_until_5s'] = 'persist_until_5s'
    kind: Literal['ad','insight'] = 'ad'
    platform: Literal['ChatGPT','Claude','Gemini','DeepSeek','Grok'] = 'ChatGPT'
    country: str = Field(default='United States of America', min_length=2, max_length=80)
    slot: int = Field(default=1, ge=1, le=50)

class FinishView(BaseModel):
    id: str

class CancelView(FinishView):
    reason: Literal['below_threshold','dismissed','window_blurred','navigation'] = 'dismissed'

def receipt(charge, status, amount, watched):
    return {'id':charge['id'], 'at':datetime.now(timezone.utc).isoformat(), 'title':charge['title'],
            'campaign_id':charge.get('campaign_id'), 'variant':chr(65+charge['variant_index']),
            'kind':charge['kind'], 'status':status, 'amount_mills':amount,
            'watched_seconds':round(watched,1), 'required_seconds':charge['required_seconds'],
            'slot':charge['slot'], 'platform':charge['platform'], 'country':charge['country'],
            'clicked':charge.get('clicked',False), 'bid':charge['bid'], 'topic':charge['topic'], 'sample':False}

def install_view_routes(api, db, owner, state_for, State):
    @api.post('/charges/start')
    async def start_view(payload: StartView | None = None, session=Depends(owner)):
        p=payload or StartView()
        campaign=None
        if p.campaign_id:
            campaign=await db.campaigns.find_one({'owner':session['token'],'id':p.campaign_id},{'_id':0,'owner':0})
            if not campaign:
                raise HTTPException(404,'Campaign not found.')
        duration=campaign.get('duration_seconds',5) if campaign else p.duration_seconds
        bid=campaign['bid'] if campaign else .02
        title=campaign['variants'][p.variant_index]['headline'] if campaign else 'Your next big idea deserves a better workflow.'
        charge={**p.model_dump(), 'id':str(uuid.uuid4()),'started_at':datetime.now(timezone.utc).isoformat(),
                'required_seconds':duration,'bid':bid,'credit_mills':round(bid*550),'title':title,
                'topic':campaign['topics'][0] if campaign else 'AI / ML','clicked':False}
        if p.kind=='insight':
            charge['title']='The hidden memory cost of every token.'
        await db.sessions.update_one({'token':session['token']},{'$set':{'charge':charge}})
        return charge

    @api.post('/charges/complete', response_model=State)
    async def complete_view(payload: FinishView, session=Depends(owner)):
        c=session.get('charge')
        if not c or c['id']!=payload.id:
            raise HTTPException(409,'View incomplete or already credited.')
        required=c.get('required_seconds',5)
        if c['kind']=='ad' and c['display_mode']=='wait_time_only' and c['response_seconds']<required:
            raise HTTPException(409,'AI response ended before the required viewing duration.')
        threshold=c['response_seconds'] if c['kind']=='insight' else required
        cutoff=(datetime.now(timezone.utc)-timedelta(seconds=threshold)).isoformat()
        amount=c['credit_mills'] if c['kind']=='ad' else 0
        event=receipt(c,'credited' if c['kind']=='ad' else 'insight',amount,threshold)
        update={'$unset':{'charge':''},'$push':{'profile.events':{'$each':[event],'$slice':-500}},
                '$inc':{'profile.balance_mills':amount,'profile.views':1 if c['kind']=='ad' else 0,'profile.seconds':threshold}}
        result=await db.sessions.update_one({'token':session['token'],'charge.id':payload.id,'charge.started_at':{'$lte':cutoff}},update)
        if not result.modified_count:
            raise HTTPException(409,'View incomplete or already credited.')
        if session.get('referred_by') and c['kind']=='ad':
            await db.sessions.update_one({'token':session['referred_by'],'profile.referrals.id':session['referral_id']},{'$inc':{'profile.referrals.$.verified_mills':round(c['bid']*1000)}})
        result_state=await state_for(session['token'])
        result_state.credited_mills=amount
        return result_state

    @api.post('/charges/cancel', response_model=State)
    async def cancel_view(payload: CancelView, session=Depends(owner)):
        c=session.get('charge')
        if not c or c['id']!=payload.id:
            return await state_for(session['token'])
        elapsed=(datetime.now(timezone.utc)-datetime.fromisoformat(c['started_at'])).total_seconds()
        watched=min(elapsed,c['response_seconds'] if payload.reason=='below_threshold' else c['required_seconds'])
        event=receipt(c,payload.reason,0,watched)
        await db.sessions.update_one({'token':session['token'],'charge.id':payload.id},{'$unset':{'charge':''},'$push':{'profile.events':{'$each':[event],'$slice':-500}}})
        return await state_for(session['token'])

    @api.post('/charges/{view_id}/click', response_model=State)
    async def click_view(view_id: str, session=Depends(owner)):
        await db.sessions.update_one({'token':session['token'],'charge.id':view_id},{'$set':{'charge.clicked':True}})
        await db.sessions.update_one({'token':session['token'],'profile.events.id':view_id},{'$set':{'profile.events.$.clicked':True}})
        return await state_for(session['token'])