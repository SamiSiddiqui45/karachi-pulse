import { useEffect, useRef, useState } from 'react';
import * as maplibregl from 'maplibre-gl';
import type { GeoJSONSource, StyleSpecification } from 'maplibre-gl';
import type { Facilities, Facility } from '../types';
import { LocateFixed, Maximize2 } from 'lucide-react';
import 'maplibre-gl/dist/maplibre-gl.css';
import workerUrl from 'maplibre-gl/dist/maplibre-gl-worker.mjs?worker&url';
maplibregl.setWorkerUrl(workerUrl);
const region=import.meta.env.VITE_AWS_REGION||'ap-south-1';
const mapName=import.meta.env.VITE_LOCATION_MAP_NAME||'karachi-pulse';
const key=import.meta.env.VITE_LOCATION_API_KEY;
const offline:StyleSpecification={version:8,sources:{},layers:[{id:'background',type:'background',paint:{'background-color':'#101c2c'}}]};
export default function PulseMap({data,heat,selected,onSelect,boundaries}:{data:Facilities;heat:boolean;selected:Facility|null;onSelect:(f:Facility)=>void;boundaries:boolean}){
  const container=useRef<HTMLDivElement>(null),map=useRef<maplibregl.Map|null>(null);
  const latest=useRef({data,onSelect,heat,boundaries});
  latest.current={data,onSelect,heat,boundaries};
  const [ready,setReady]=useState(false),[error,setError]=useState('');
  useEffect(()=>{
    if(!container.current)return;
    const controller=new AbortController();
    const instance=new maplibregl.Map({container:container.current,style:key?`https://maps.geo.${region}.amazonaws.com/maps/v0/maps/${encodeURIComponent(mapName)}/style-descriptor?key=${encodeURIComponent(key)}`:offline,center:[67.055,24.91],zoom:10.4,minZoom:7,maxZoom:19,attributionControl:{compact:true}});
    map.current=instance;
    instance.addControl(new maplibregl.NavigationControl({showCompass:true}),'bottom-right');
    instance.addControl(new maplibregl.ScaleControl({unit:'metric'}),'bottom-left');
    instance.on('error',()=>setError('Map provider could not load. Check your Amazon Location key, region, map name and allowed referrers.'));
    instance.on('load',()=>{
      instance.addSource('facilities',{type:'geojson',data:latest.current.data,cluster:true,clusterRadius:42,clusterMaxZoom:14});
      instance.addSource('density',{type:'geojson',data:latest.current.data});
      instance.addLayer({id:'heat',type:'heatmap',source:'density',maxzoom:17,layout:{visibility:latest.current.heat?'visible':'none'},paint:{'heatmap-weight':1,'heatmap-intensity':1.1,'heatmap-radius':32,'heatmap-opacity':0.75,'heatmap-color':['interpolate',['linear'],['heatmap-density'],0,'rgba(50,30,90,0)',0.25,'#514eaa',0.5,'#9a7cff',0.75,'#51d9df',1,'#e1ffff']}});
      instance.addLayer({id:'clusters',type:'circle',source:'facilities',filter:['has','point_count'],paint:{'circle-color':'#8471df','circle-radius':['step',['get','point_count'],19,10,24,50,30],'circle-stroke-width':5,'circle-stroke-color':'rgba(164,142,255,0.18)'}});
      // HTML cluster counts avoid any glyph dependency in the credential-free mode.
      const clusterMarkers=new Map<number,maplibregl.Marker>();
      const updateCounts=()=>{
        if(!instance.isSourceLoaded('facilities'))return;
        clusterMarkers.forEach(marker=>marker.remove()); clusterMarkers.clear();
        instance.querySourceFeatures('facilities',{filter:['has','point_count']}).forEach(f=>{
          const id=Number(f.properties?.cluster_id);
          if(clusterMarkers.has(id)||f.geometry.type!=='Point')return;
          const button=document.createElement('button');button.className='cluster-count';button.textContent=String(f.properties?.point_count);button.setAttribute('aria-label',`Expand cluster of ${button.textContent} facilities`);
          button.onclick=()=>{void (instance.getSource('facilities') as GeoJSONSource).getClusterExpansionZoom(id).then(zoom=>instance.easeTo({center:(f.geometry as GeoJSON.Point).coordinates as [number,number],zoom}));};
          clusterMarkers.set(id,new maplibregl.Marker({element:button}).setLngLat(f.geometry.coordinates as [number,number]).addTo(instance));
        });
      };
      instance.on('idle',updateCounts);
      instance.addLayer({id:'points',type:'circle',source:'facilities',filter:['!', ['has','point_count']],paint:{'circle-radius':6,'circle-color':['match',['get','category'],'Hospital','#a89aff','Clinic','#40d7d1','Doctor','#7baeff','Pharmacy','#f5bf70','Dentist','#f58ab3','#b7c8da'],'circle-stroke-color':'#172033','circle-stroke-width':2}});
      instance.on('click','points',event=>{
        const id=event.features?.[0]?.properties?.id;
        const f=latest.current.data.features.find(f=>f.properties.id===id);
        if(f)latest.current.onSelect(f);
      });
      instance.on('mouseenter','points',()=>{instance.getCanvas().style.cursor='pointer';});
      instance.on('mouseleave','points',()=>{instance.getCanvas().style.cursor='';});
      instance.addSource('boundary',{type:'geojson',data:{type:'FeatureCollection',features:[]}});
      instance.addLayer({id:'boundary-fill',type:'fill',source:'boundary',layout:{visibility:latest.current.boundaries?'visible':'none'},paint:{'fill-color':'#7575b8','fill-opacity':0.045}},'heat');
      instance.addLayer({id:'boundary',type:'line',source:'boundary',layout:{visibility:latest.current.boundaries?'visible':'none'},paint:{'line-color':'#7b79bc','line-width':1.5,'line-dasharray':[4,3]}});
      fetch('/data/boundary.geojson',{signal:controller.signal}).then(r=>{if(!r.ok)throw Error();return r.json();}).then(value=>(instance.getSource('boundary') as GeoJSONSource)?.setData(value)).catch(e=>{if(e.name!=='AbortError')setError('Study boundary could not load. Facility data remains available.');});
      instance.addControl({onAdd:()=>{const div=document.createElement('div');div.className='maplibregl-ctrl attribution-extra';div.textContent='© OpenStreetMap contributors · healthsites.io · ODbL | Boundary: geoBoundaries';return div;},onRemove:()=>{}},'bottom-left');
      setReady(true);
    });
    const observer=new ResizeObserver(()=>instance.resize());observer.observe(container.current);
    return()=>{controller.abort();observer.disconnect();instance.remove();map.current=null;};
  },[]);
  useEffect(()=>{if(ready){(map.current?.getSource('facilities') as GeoJSONSource)?.setData(data);(map.current?.getSource('density') as GeoJSONSource)?.setData(data);}},[data,ready]);
  useEffect(()=>{if(ready)map.current?.setLayoutProperty('heat','visibility',heat?'visible':'none');},[heat,ready]);
  useEffect(()=>{if(ready){map.current?.setLayoutProperty('boundary','visibility',boundaries?'visible':'none');map.current?.setLayoutProperty('boundary-fill','visibility',boundaries?'visible':'none');}},[boundaries,ready]);
  useEffect(()=>{if(selected&&ready)map.current?.flyTo({center:selected.geometry.coordinates as [number,number],zoom:14});},[selected,ready]);
  return <div className="map-shell"><div ref={container} className="map-canvas" aria-label="Interactive map of Karachi healthcare facilities"/>{!key&&<div className="map-notice">DATA EXPLORER MODE <span>Amazon Location key not configured · basemap unavailable</span></div>}{error&&<div className="map-error" role="alert">{error}</div>}<div className="map-heading"><span className="live-dot"/> KARACHI METROPOLITAN AREA <span>24.8607° N · 67.0011° E</span></div><div className="map-tools"><button title="Fit all filtered facilities" aria-label="Fit facilities" onClick={()=>{if(!data.features.length)return;const bounds=new maplibregl.LngLatBounds();data.features.forEach(f=>bounds.extend(f.geometry.coordinates as [number,number]));map.current?.fitBounds(bounds,{padding:65,maxZoom:13});}}><Maximize2 size={17}/></button><button title="Reset Karachi view" aria-label="Reset map" onClick={()=>map.current?.flyTo({center:[67.055,24.91],zoom:10.4})}><LocateFixed size={17}/></button></div><div className="map-caption"><span className="live-dot"/>{data.features.length} mapped facilities <span>WGS 84 / EPSG:4326</span></div>{heat&&<div className="heat-legend"><span>Mapped-record density</span><i/><div><span>Lower</span><span>Higher</span></div></div>}</div>;
}
