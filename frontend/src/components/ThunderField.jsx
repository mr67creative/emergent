import {useEffect,useRef} from 'react';
export const ThunderField=({running=false})=>{
 const canvas=useRef(null),energy=useRef(running);useEffect(()=>{energy.current=running;},[running]);
 useEffect(()=>{const el=canvas.current,ctx=el.getContext('2d');if(!ctx)return;let w=0,h=0,raf=0,last=0,visible=true;const reduced=window.matchMedia('(prefers-reduced-motion: reduce)').matches;
 const resize=()=>{const r=el.getBoundingClientRect();w=r.width;h=r.height;const dpr=Math.min(window.devicePixelRatio||1,1.5);el.width=w*dpr;el.height=h*dpr;ctx.setTransform(dpr,0,0,dpr,0,0);};
 const draw=(now)=>{raf=requestAnimationFrame(draw);if(!visible||document.hidden||now-last<32)return;last=now;if(!w||!h)return;const t=reduced?1.4:now*.00028;ctx.clearRect(0,0,w,h);ctx.globalCompositeOperation='lighter';
  const power=energy.current?1.55:1.23;
  for(let strand=0;strand<34;strand++){const layer=strand/33,phase=layer*Math.PI*2;const points=[];
   for(let j=0;j<=220;j++){const u=j/220,x=u*w;const edge=Math.pow(Math.abs(u-.5)*2,.5);const wave=Math.sin(u*Math.PI*4.3+t+phase*.18)*h*.16+Math.sin(u*16-t*.8+phase)*h*.067;const ripple=Math.sin(u*145+t*2+phase)*Math.sin(u*73-t+phase)*h*.006;const y=h*.52+wave*edge*power+Math.sin(u*20+t+phase)*20*edge+(layer-.5)*40*(.25+edge)+ripple;points.push([x,y]);}
   const path=()=>{ctx.beginPath();points.forEach(([x,y],j)=>j?ctx.lineTo(x,y):ctx.moveTo(x,y));};
   const gradient=ctx.createLinearGradient(0,0,w,0);const opacity=strand%5===0?.9:.32;gradient.addColorStop(0,`rgba(12,137,114,${opacity*.1})`);gradient.addColorStop(.16,`rgba(20,218,163,${opacity})`);gradient.addColorStop(.44,`rgba(104,255,205,${opacity*.8})`);gradient.addColorStop(.65,`rgba(32,204,220,${opacity*.6})`);gradient.addColorStop(.88,`rgba(87,239,200,${opacity})`);gradient.addColorStop(1,'rgba(16,185,129,0)');
   if(strand%5===0){path();ctx.strokeStyle='rgba(16,185,129,.08)';ctx.lineWidth=23;ctx.shadowColor='#10b981';ctx.shadowBlur=29;ctx.stroke();}
   path();ctx.strokeStyle=gradient;ctx.lineWidth=strand%5===0?1.75:.8;ctx.shadowColor=strand%3===0?'#92ffe2':'#10b981';ctx.shadowBlur=strand%5===0?15:3;ctx.stroke();
  }
  ctx.shadowBlur=0;ctx.globalCompositeOperation='source-over';
  if(reduced){cancelAnimationFrame(raf);}
 };
 const observer=new ResizeObserver(()=>{resize();if(reduced){cancelAnimationFrame(raf);raf=requestAnimationFrame(draw);}});observer.observe(el);const io=new IntersectionObserver(entries=>{visible=entries[0].isIntersecting;});io.observe(el);resize();raf=requestAnimationFrame(draw);return()=>{cancelAnimationFrame(raf);observer.disconnect();io.disconnect();};
 },[]);
 return <canvas ref={canvas} className="thunder-field" data-testid="thunder-canvas" aria-label="Flowing emerald and cyan electrical waves"/>;
};