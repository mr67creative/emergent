import {useCallback,useEffect,useRef,useState} from 'react';
import {useStore} from '../../lib/store';
import {rememberView,forgetView,cancelOnExit} from '../../lib/viewLifecycle';
import {demoResponse} from '../../lib/chatResponses';
const empty={phase:'idle',elapsed:0,aiDone:false,paid:0,result:null,prompt:'',response:null};

export function useChatFlow({campaign,variantIndex=0,settings,platform,responseSeconds=6,country='United States of America',previewOnly=false,onActivity}){
 const {state,action,replaceState}=useStore();
 const [flow,setFlow]=useState(empty),session=useRef(null),timer=useRef(null),alive=useRef(true),activity=useRef(onActivity);
 useEffect(()=>{activity.current=onActivity;},[onActivity]);
 const patch=useCallback(values=>{if(alive.current)setFlow(f=>({...f,...values}));},[]);
 const cancel=useCallback(async(reason='dismissed')=>{
  const s=session.current;if(!s||s.settled)return;
  s.settled=true;s.cancelReason=reason;patch({result:reason,paid:0});
  if(s.remote&&s.id){try{await action('/charges/cancel',{id:s.id,reason});s.confirmed=true;forgetView(s.id);}catch{}}
 },[action,patch]);
 const exit=useCallback(()=>{
  const s=session.current;if(!s?.remote||s.confirmed)return;
  s.cancelReason='navigation';s.settled=true;
  // An unresolved start is canceled only after its actual server ID is known.
  if(s.id)cancelOnExit(s.id,s.token).then(data=>{if(data?.profile){s.confirmed=true;replaceState(data);}});
 },[replaceState]);
 useEffect(()=>{
  alive.current=true;
  const hidden=()=>{if(document.hidden&&session.current&&!session.current.settled)cancel('window_blurred');};
  document.addEventListener('visibilitychange',hidden);window.addEventListener('pagehide',exit);
  return()=>{alive.current=false;clearInterval(timer.current);activity.current?.(false);document.removeEventListener('visibilitychange',hidden);window.removeEventListener('pagehide',exit);exit();};
 },[cancel,exit]);

 const start=async prompt=>{
  if(session.current?.running||!prompt.trim()||!state)return;
  const duration=campaign?.duration_seconds||5,active=settings.enabled&&settings.platforms.includes(platform),kind=settings.mode==='insights'?'insight':'ad';
  const s={id:null,token:localStorage.getItem('meantime-demo-token'),remote:active&&!previewOnly,running:true,settled:false,confirmed:false,busy:false,kind,duration,display:settings.display_mode||'persist_until_5s',responseSeconds,active};
  session.current=s;setFlow({...empty,phase:'starting',prompt,response:demoResponse(prompt),duration,kind,active});activity.current?.(true);
  try{
   if(s.remote){
    const data=await action('/charges/start',{campaign_id:campaign?.id||null,variant_index:variantIndex,duration_seconds:duration,response_seconds:responseSeconds,display_mode:s.display,kind,platform,country,slot:1});
    s.id=data.id;s.duration=data.required_seconds;rememberView(s.id,s.token);
    if(s.cancelReason||!alive.current){const result=await cancelOnExit(s.id,s.token);if(result?.profile)replaceState(result);return;}
   }
   if(!alive.current)return;
   const began=performance.now();patch({phase:'thinking',duration:s.duration});
   timer.current=setInterval(async()=>{
    const elapsed=(performance.now()-began)/1000,aiDone=elapsed>=s.responseSeconds;patch({elapsed,aiDone});
    if(!s.settled&&!s.busy){
     const short=s.kind==='ad'&&s.display==='wait_time_only'&&aiDone&&s.responseSeconds<s.duration;
     const reached=s.kind==='insight'?aiDone:elapsed>=s.duration;
     if(short){s.busy=true;await cancel('below_threshold');s.busy=false;}
     else if(reached){
      s.busy=true;
      try{let paid=0;if(s.remote){const result=await action('/charges/complete',{id:s.id});paid=result.credited_mills;s.confirmed=true;forgetView(s.id);}s.settled=true;patch({paid,result:!s.active?'paused':previewOnly?'preview':s.kind==='insight'?'insight':'credited'});}
      catch{await cancel('dismissed');patch({result:'error'});}
      s.busy=false;
     }
    }
    if(aiDone&&!s.active&&!s.settled){s.settled=true;patch({result:'paused'});}
    if(aiDone&&s.settled&&!s.busy){s.running=false;clearInterval(timer.current);patch({phase:'complete'});activity.current?.(false);}
   },80);
  }catch{s.running=false;patch({phase:'idle',result:'error'});activity.current?.(false);}
 };
 const click=()=>{const s=session.current;if(s?.remote&&s.id)action(`/charges/${s.id}/click`).catch(()=>{});};
 const reset=()=>{if(session.current?.running)return;session.current=null;setFlow(empty);};
 return {flow,start,cancel,click,reset,running:['starting','thinking'].includes(flow.phase)};
}