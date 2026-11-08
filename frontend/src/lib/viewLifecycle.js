const STORAGE_KEY='meantime-pending-views';
const endpoint=`${process.env.REACT_APP_BACKEND_URL}/api/charges/cancel`;
const read=()=>{try{return JSON.parse(sessionStorage.getItem(STORAGE_KEY)||'[]');}catch{return [];}};
const write=items=>{try{sessionStorage.setItem(STORAGE_KEY,JSON.stringify(items.slice(-20)));}catch{}};
export function rememberView(id,token=localStorage.getItem('meantime-demo-token')){
 if(!id||!token)return;
 const pending=read();if(!pending.some(v=>v.id===id&&v.token===token))write([...pending,{id,token}]);
}
export function forgetView(id){if(id)write(read().filter(v=>v.id!==id));}
export async function cancelOnExit(id,token=localStorage.getItem('meantime-demo-token')){
 if(!id||!token)return null;
 rememberView(id,token);
 try{
  const response=await fetch(endpoint,{method:'POST',headers:{'Content-Type':'application/json','X-Demo-Token':token},body:JSON.stringify({id,reason:'navigation'}),keepalive:true});
  if(!response.ok)return null;
  const data=await response.json();forgetView(id);return data;
 }catch{return null;}
}
export async function recoverInterruptedViews(token){
 for(const pending of read().filter(v=>v.token===token))await cancelOnExit(pending.id,token);
}