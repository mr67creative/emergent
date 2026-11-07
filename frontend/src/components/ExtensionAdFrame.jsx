import {Puzzle} from 'lucide-react';
import {AdBox} from './AdBox';
import {BrandMark} from './Brand';
export const ExtensionAdFrame=({id='extension-ad',label=true,...props})=><div className="extension-ad-frame" data-testid={`${id}-placement`}>{label&&<div className="extension-placement-label"><BrandMark/><span>meantime</span><i/><Puzzle size={10}/><span>IN-PAGE EXTENSION</span></div>}<AdBox id={id} {...props}/></div>;