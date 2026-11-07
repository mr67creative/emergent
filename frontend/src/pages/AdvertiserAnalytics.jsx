import {useState} from 'react';
import {Link} from 'react-router-dom';
import {ArrowLeft,Download,MousePointerClick,Eye,Wallet,Activity} from 'lucide-react';
import {PageHeader} from '../components/PageHeader';
import {WorldMap,mapCountries as countries} from '../components/WorldMap';
import {Heatmap,Sparkline} from '../components/AnalyticsVisuals';
import {Ring,Segments} from '../components/Meters';

const InterestPerformance=()=> <section className="panel"><div className="panel-header"><h2>The interest advantage.</h2><span>CTR / VERIFIED</span></div><div className="interest-bars">{[['AI / ML',88,4.8],['DevTools',79,4.2],['Cloud',68,3.9],['Hardware',58,3.4],['Science',45,2.8],['Finance',36,2.1]].map(([name,pct,ctr])=><div key={name}><div><span>{name}</span><span className="mono">{ctr}%</span></div><div className="stacked-track" data-testid={`interest-bar-${name}`} title={`${name}: ${ctr}% CTR · ${pct}% sample verification rate`}><i style={{width:`${pct}%`}}/><b style={{width:`${100-pct}%`}}/></div></div>)}</div></section>;
const VariantPerformance=()=> <section className="panel"><div className="panel-header"><h2>Every variant. In perspective.</h2><span>SAMPLE COMPARISON</span></div><div className="variant-comparison">{[['A',94,3.84,312],['B',89,3.21,248],['C',91,3.62,286]].map(([v,vr,ctr,n])=><article key={v} data-testid={`variant-comparison-${v}`}><h3>Variant {v}</h3><Ring value={vr} size={73}><span className="mono">{vr}<small>%</small></span></Ring><span className="comparison-label">Verification</span><div className="ctr-value mono">{ctr}<small>% CTR</small></div><Segments value={n/5} color="#22d3ee" count={12} id={`confidence-${v}`}/><span className="confidence-value mono" title="500 verified views required for the sample-size threshold.">{n} / 500</span></article>)}</div></section>;

export default function AdvertiserAnalytics(){
 const [region,setRegion]=useState(null),[period,setPeriod]=useState('7');
 const country=countries.find(c=>c.name===region),factor=period==='30'?4:1,selected=country?[country]:countries;
 const total=selected.reduce((sum,c)=>sum+c.views,0)*factor;
 const clicks=selected.reduce((sum,c)=>sum+c.clicks,0)*factor;
 const spend=selected.reduce((sum,c)=>sum+c.views*Number(c.cpvv),0)*factor;
 const ctr=total?clicks/total*100:0;
 const metrics=[['Verified views',total.toLocaleString(),Eye,'#10b981'],['Click-through rate',`${ctr.toFixed(2)}%`,MousePointerClick,'#22d3ee'],['Ad spend',`$${spend.toFixed(2)}`,Wallet,'#fbbf24'],['Verification rate','94.2%',Activity,'#10b981']];
 const download=()=>{const rows=selected.map(c=>`"${c.name.replaceAll('"','""')}",${c.views*factor},${c.clicks*factor},${c.cpvv},${c.platform}`);const blob=new Blob([`Country,Sample verified views,Sample clicks,CPVV,Top AI platform\n${rows.join('\n')}`],{type:'text/csv'});const url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='meantime-sample-analytics.csv';a.click();URL.revokeObjectURL(url);};
 return <div className="page-container">
  <PageHeader eyebrow="ADVERTISER / SAMPLE ANALYTICS" title="Attention. Not just impressions."><Link to="/advertiser" className="button secondary" data-testid="analytics-back"><ArrowLeft size={14}/>Studio</Link><select data-testid="advertiser-period" className="select-control" value={period} onChange={e=>setPeriod(e.target.value)} aria-label="Analytics period"><option value="7">Last 7 days</option><option value="30">Last 30 days</option></select><button className="button secondary" onClick={download} data-testid="export-analytics"><Download size={14}/>Export</button></PageHeader>
  <div className="kpi-grid">{metrics.map(([label,value,Icon,color],i)=><article className="kpi-card" key={label}><div className="kpi-top"><span>{label}</span><Icon size={14}/></div><div className="kpi-value mono" data-testid={`ad-analytics-kpi-${i}`}>{value}</div><div className="kpi-foot"><span style={{color}}>↗ {['18.6','0.42','12.8','2.1'][i]}%</span> this period</div><div className="kpi-chart"><Sparkline color={color} id={`ad-spark-${i}`}/></div></article>)}</div>
  <section className="panel advertiser-world-section"><div className="panel-header"><h2 data-testid="advertiser-region-title">{region||'Every pixel. A little more perspective.'}</h2><span>GEOGRAPHIC ATTENTION</span></div><WorldMap id="ad-world" filter={region} onFilter={setRegion} period={factor}/></section>
  <div className="advertiser-secondary-grid"><InterestPerformance/><VariantPerformance/></div>
  <section className="panel temporal-panel"><div className="panel-header"><h2>The hours that work.</h2><span>Views · UTC</span></div><Heatmap id="ad-hours" variant={period==='7'?1:2}/></section>
 </div>;
}