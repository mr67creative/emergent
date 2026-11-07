import {BrowserRouter,Routes,Route,Link} from 'react-router-dom';
import {Toaster} from 'sonner';
import {Zap,ArrowLeft} from 'lucide-react';
import {StoreProvider,useStore} from './lib/store';
import {Layout} from './components/Layout';
import Home from './pages/Home';
import Dashboard from './pages/Dashboard';
import Insights from './pages/Insights';
import Rewards from './pages/Rewards';
import Advertiser from './pages/Advertiser';
import AdvertiserAnalytics from './pages/AdvertiserAnalytics';
import Admin from './pages/Admin';
import Simulator from './pages/Simulator';
import './App.css';
import './pages.css';
import './responsive.css';
const Ready=({children})=>{const {state,error}=useStore();if(error)return <div className="loading-screen" data-testid="connection-error"><Zap size={30}/><span>We couldn't connect to your vault.</span><button className="button primary" data-testid="retry-connection" onClick={()=>window.location.reload()}>Try again</button></div>;if(!state)return <div className="loading-screen" data-testid="app-loading"><Zap size={30}/><span>Making a little time…</span></div>;return children;};
export default function App(){return <StoreProvider><BrowserRouter><Routes><Route element={<Layout/>}><Route path="/" element={<Home/>}/>{[['/dashboard',Dashboard],['/insights',Insights],['/rewards',Rewards],['/advertiser',Advertiser],['/advertiser/analytics',AdvertiserAnalytics],['/admin',Admin],['/simulator',Simulator]].map(([path,Page])=><Route key={path} path={path} element={<Ready><Page/></Ready>}/>)}<Route path="*" element={<div className="empty-state"><Zap size={32}/><h1>Nothing waiting here.</h1><Link to="/" className="button secondary" data-testid="not-found-home"><ArrowLeft size={14}/>Back to MeanTime</Link></div>}/></Route></Routes><Toaster theme="dark" position="bottom-right" richColors closeButton/></BrowserRouter></StoreProvider>;}