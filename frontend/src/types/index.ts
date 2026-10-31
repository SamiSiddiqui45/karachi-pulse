import type { Feature, FeatureCollection, Point } from 'geojson';
export type FacilityProperties = {id:string; name:string; category:string; address:string; operator:string; beds:string; emergency:string; osm_id:string; source_url:string; source_type:string};
export type Facility = Feature<Point,FacilityProperties>;
export type Facilities = FeatureCollection<Point,FacilityProperties>;
export type Quality = {extracted:number; accepted:number; rejected:number; rejection_reasons:Record<string,number>; categories:Record<string,number>; missing_values:Record<string,number>; boundary:string; provenance:Record<string,{url:string;sha256:string;retrieved_at:string}>};
