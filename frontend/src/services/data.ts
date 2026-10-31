import type { Facilities, Facility } from '../types';
export async function loadFacilities(signal:AbortSignal):Promise<Facilities> {
  const response=await fetch(import.meta.env.VITE_DATA_URL || '/data/facilities.geojson',{signal});
  if(!response.ok) throw new Error(`Dataset request failed (${response.status}). If using S3, renew the read URL.`);
  const value=await response.json();
  if(!value||value.type!=='FeatureCollection'||!Array.isArray(value.features)) throw new Error('Invalid GeoJSON collection');
  const ids=new Set<string>();
  for(const f of value.features){
    if(!f) throw new Error('Dataset contains an invalid or duplicate facility');
    const c=f.geometry?.coordinates;
    if(f.type!=='Feature'||f.geometry?.type!=='Point'||!Array.isArray(c)||c.length!==2||!c.every(Number.isFinite)||Math.abs(c[0])>180||Math.abs(c[1])>90||!f.properties?.id||!f.properties?.name||!f.properties?.category||ids.has(f.properties.id)) throw new Error('Dataset contains an invalid or duplicate facility');
    ids.add(f.properties.id);
  }
  return value;
}
export function filterFacilities(features:Facility[],query:string,categories:string[]) {
  const term=query.trim().toLocaleLowerCase();
  return features.filter(f=>(!categories.length||categories.includes(f.properties.category))&&[f.properties.name,f.properties.category,f.properties.address].join(' ').toLocaleLowerCase().includes(term));
}
export function categoryCounts(features:Facility[]) {
  return features.reduce<Record<string,number>>((counts,f)=>{counts[f.properties.category]=(counts[f.properties.category]||0)+1; return counts;},{});
}
export const colors:Record<string,string>={Hospital:'#a89aff',Clinic:'#40d7d1',Doctor:'#7baeff',Pharmacy:'#f5bf70',Dentist:'#f58ab3'};
export const colorFor=(name:string)=>colors[name]||'#b7c8da';
