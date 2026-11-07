import {useState,useEffect,useRef} from 'react';
import {ArrowUp,Zap,Sparkles,ArrowUpRight,BrainCircuit,BookOpen,RotateCcw} from 'lucide-react';
import {toast} from 'sonner';
import {ExtensionAdFrame} from './ExtensionAdFrame';
import {BrandMark} from './Brand';
import {ThunderField} from './ThunderField';
import {useStore,money} from '../lib/store';
import {platforms,defaultCreative} from '../lib/content';
export const ChargeExperience=({simulator=false})=>{
 const {state,action}=useStore();const [mode,setMode]=useState('ad'),[platform,setPlatform]=useState('ChatGPT'),[prompt,setPrompt]=useState('Help me build something extraordinary.');
 const [running,setRunning]=useState(false),[progress,setProgress]=useState(64),[dismissed,setDismissed]=useState(false),[earned,setEarned]=useState(0),[done,setDone]=useState(false);
 const timer=useRef(null),pending=useRef(false),alive=useRef(true);
 const extension=state?.profile.extension;const enabled=!simulator||(extension?.enabled&&extension?.platforms.includes(platform));
 const campaign=simulator?state?.campaigns.find(c=>c.status==='approved'):null;
 useEffect(()=>{if(simulator&&extension)setMode(extension.mode==='insights'?'insight':'ad');},[simulator,extension?.mode]);
 useEffect(()=>{alive.current=true;return()=>{alive.current=false;clearInterval(timer.current);};},[]);
 const cancel=()=>{clearInterval(timer.current);setRunning(false);setProgress(0);pending.current=false;};
 useEffect(()=>{const hide=()=>{if(document.hidden){clearInterval(timer.current);setRunning(false);setProgress(0);pending.current=false;}};document.addEventListener('visibilitychange',hide);return()=>document.removeEventListener('visibilitychange',hide);},[]);
 const start=async()=>{if(pending.current||!enabled||!prompt.trim()||!state)return;pending.current=true;setRunning(true);setProgress(0);setDone(false);setDismissed(false);
  try{const charge=await action('/charges/start');if(!alive.current){pending.current=false;return;}const begun=Date.now();
   timer.current=setInterval(async()=>{const p=Math.min(100,(Date.now()-begun)/50);setProgress(p);if(p<100)return;clearInterval(timer.current);try{if(mode==='ad'&&!document.hidden){const result=await action('/charges/complete',{id:charge.id});if(alive.current){setEarned(e=>e+result.credited_mills);toast.success(`+${money(result.credited_mills,3)} added to your demo vault`);}}if(alive.current){setDone(true);setRunning(false);}}catch{if(alive.current)setRunning(false);}pending.current=false;},50);
  }catch{setRunning(false);pending.current=false;}
 };
 return <div className={`charge-experience thunder-experience ${running?'charging':''} ${simulator?'simulator-experience':''}`} id="the-charge"><ThunderField running={running}/>
 {simulator&&<div className="platform-switcher">{platforms.map(p=><button key={p} data-testid={`sim-platform-${p}`} className={platform===p?'selected':''} onClick={()=>{cancel();setPlatform(p);}}>{p}</button>)}</div>}
 <div className="charge-columns"><div className="prompt-section"><div className="technical-label"><span>01</span>THE PROMPT</div><div className="prompt-window"><div className="prompt-title"><BrainCircuit size={17}/><span>{platform}</span><span className="window-dots">•••</span></div><textarea aria-label="AI prompt" data-testid="charge-prompt-input" value={prompt} onChange={e=>setPrompt(e.target.value)} maxLength={300}/><div className="prompt-bottom"><span>{!enabled?'Extension paused':running?'Thinking…':done?'Answer ready':'A little ambition.'}</span><button title="Send Prompt" aria-label="Send Prompt" data-testid="send-prompt-button" disabled={running||!state||!enabled||!prompt.trim()} onClick={start}><ArrowUp size={17}/></button></div></div></div>
 <div className="charge-center"><div className="technical-label"><Zap size={12}/>THE MEANTIME</div><div className="ad-stage">{dismissed?<button className="button secondary" data-testid="restore-ad" onClick={()=>setDismissed(false)}><RotateCcw size={14}/>Restore preview</button>:mode==='ad'?<ExtensionAdFrame id="hero-ad" label={simulator} creative={campaign?.variants[0]||defaultCreative} progress={progress} onClose={()=>{cancel();setDismissed(true);}} onCta={()=>campaign?window.open(campaign.url,'_blank','noopener,noreferrer'):toast.info('Sample creative · Linear')}/>:<div className="insight-mini" data-testid="charge-insight"><BookOpen size={19}/><div><strong>The hidden memory cost of every token.</strong><span>KV caches grow with every word. <a data-testid="charge-insight-link" href="/insights">Go deeper<ArrowUpRight size={11}/></a></span></div></div>}</div><div className="charge-caption" data-testid="charge-caption">{running?'ATTENTION → VALUE':done?mode==='ad'?'A little time. A little more yours.':'A little wiser.':'Five seconds. Nothing wasted.'}</div></div>
 <div className="vault-section"><div className="technical-label"><span>02</span>YOUR VAULT</div><div className="vault-core"><div className="vault-orbit"/><div className="vault-orbit orbit-two"/><BrandMark/><span className="vault-add mono" data-testid="charge-earned">+{money(earned,3)}</span></div><span className="vault-total mono" data-testid="charge-vault-total">{money(state?.profile.balance_mills??14850,3)}</span></div></div>
 <div className="charge-mode-switch"><button className={mode==='ad'?'selected':''} data-testid="ad-mode-button" onClick={()=>setMode('ad')} disabled={running||(simulator&&extension?.mode==='insights')}><Zap size={14}/>Ad charge</button><button className={mode==='insight'?'selected':''} data-testid="insight-mode-button" onClick={()=>setMode('insight')} disabled={running}><Sparkles size={14}/>Daily insight</button></div></div>;
};