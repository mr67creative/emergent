import {X} from 'lucide-react';
import {defaultCreative} from '../lib/content';
export const AdBox = ({creative = defaultCreative, progress = 72, onClose, onCta, editable = false, onChange, id = 'ad'}) => {
  const field = (key, max, cls) => editable ? <input data-testid={`${id}-${key}-input`} aria-label={key} className={cls} value={creative[key]} maxLength={max} onChange={e => onChange(key, e.target.value)} /> : <span className={cls} title={creative[key]} data-testid={`${id}-${key}`}>{creative[key]}</span>;
  return <div className="ad-box" data-testid={`${id}-box`}>
    <button data-testid={`${id}-dismiss`} className="ad-close" title="Dismiss advertisement" onClick={onClose}><X size={14}/></button>
    <div className="ad-title">{field('headline',70,'ad-headline')}</div>
    <div className="ad-row">{field('description',140,'ad-description')}{editable ? field('cta',20,'ad-cta ad-cta-input') : <button className="ad-cta" data-testid={`${id}-cta-button`} onClick={onCta}>{creative.cta}</button>}</div>
    <div className="ad-laser"><i style={{width:`${progress}%`}}/></div>
  </div>;
};