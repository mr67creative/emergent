import axios from 'axios';
export const api = axios.create({baseURL: `${process.env.REACT_APP_BACKEND_URL}/api`});
let starting;
export async function connect() {
  if (starting) return starting;
  starting = (async () => {
    let token = localStorage.getItem('meantime-demo-token');
    if (!token) { const referral_code = new URLSearchParams(window.location.search).get('ref'); const {data} = await api.post('/session', referral_code ? {referral_code} : {}); token = data.token; localStorage.setItem('meantime-demo-token', token); }
    api.defaults.headers.common['X-Demo-Token'] = token;
    try { return (await api.get('/state')).data; }
    catch (e) { if (e.response?.status === 401) { localStorage.removeItem('meantime-demo-token'); starting = null; return connect(); } throw e; }
  })();
  try { return await starting; } finally { starting = null; }
}