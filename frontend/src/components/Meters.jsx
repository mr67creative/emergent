import {useId} from 'react';
export const Ring = ({value=55,size=84,color='var(--emerald)',children,label}) => {
 const r=40, c=2*Math.PI*r;
 return <div className="ring" style={{width:size,height:size}} title={label}>
 <svg viewBox="0 0 100 100" aria-hidden="true"><circle cx="50" cy="50" r={r} fill="none" stroke="#27272e" strokeWidth="5"/><circle cx="50" cy="50" r={r} fill="none" stroke={color} strokeWidth="5" strokeDasharray={`${c * Math.min(100,Math.max(0,value))/100} ${c}`} strokeLinecap="round" transform="rotate(-90 50 50)"/></svg><div className="ring-content">{children || <span className="mono">{value}%</span>}</div></div>;
};
export const Segments = ({value=60,color='var(--emerald)',count=28,id='segments'}) => <div className="segments" data-testid={id} role="meter" aria-valuenow={value} aria-valuemin={0} aria-valuemax={100}>{Array.from({length:count},(_,i)=><i key={i} style={{background:i/count*100<value?color:undefined}}/>)}</div>;
export const Gauge = ({value=28}) => {
 const uid=useId();
 return <div className="gauge" data-testid="laya-gauge" title="Laya simulation score. 0–40 safe, 40–85 review, 85–100 high risk."><svg viewBox="0 0 240 145"><defs><filter id={uid}><feGaussianBlur stdDeviation="2"/></filter></defs><path d="M 25 120 A 95 95 0 0 1 215 120" stroke="#25252c" strokeWidth="16" fill="none"/><path d="M25 120 A95 95 0 0 1 90.65 29.65" stroke="#10b981" strokeWidth="12" fill="none"/><path d="M90.65 29.65 A95 95 0 0 1 204.65 76.87" stroke="#fbbf24" strokeWidth="12" fill="none"/><path d="M204.65 76.87 A95 95 0 0 1 215 120" stroke="#f87171" strokeWidth="12" fill="none"/><g transform={`rotate(${value*1.8-90} 120 120)`}><path d="M117 121 L120 43 L123 121 Z" fill="white"/><circle cx="120" cy="120" r="6" fill="#fff"/></g><text x="23" y="143" fill="#797984" fontSize="10">0</text><text x="202" y="143" fill="#797984" fontSize="10">100</text></svg><div className="gauge-score mono">{value}<small>%</small></div></div>;
};