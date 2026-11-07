import {Link} from 'react-router-dom';
export const BrandMark=({className=''})=><img className={`merch-brandmark ${className}`} src="/brand/meantime-mark.png" alt="MeanTime lightning monogram"/>;
export const Logo=({id='brand-home'})=><Link className="brand merch-brand" to="/" data-testid={id}><BrandMark/><span className="merch-wordmark">meantime</span></Link>;