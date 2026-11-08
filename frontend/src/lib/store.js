import {createContext, useContext, useEffect, useState, useCallback} from 'react';
import {toast} from 'sonner';
import {api, connect} from './api';
const Store = createContext(null);
export const StoreProvider = ({children}) => {
  const [state, setState] = useState(null);
  const [error, setError] = useState(false);
  useEffect(() => {connect().then(setState).catch(() => setError(true));}, []);
  const action = useCallback(async (path, payload = {}, method = 'post') => {
    try {const {data} = await api[method](path, payload); if (data.profile) setState(data); return data;}
    catch (e) {toast.error(typeof e.response?.data?.detail === 'string' ? e.response.data.detail : 'Could not save. Please try again.'); throw e;}
  }, []);
  return <Store.Provider value={{state, action, error, replaceState:setState}}>{children}</Store.Provider>;
};
export const useStore = () => useContext(Store);
export const money = (mills, digits = 2) => `$${(mills / 1000).toFixed(digits)}`;