import { render,screen,fireEvent,waitFor } from '@testing-library/react';
import { beforeEach,expect,it,vi } from 'vitest';
import App from '../src/App';
import { categoryCounts,filterFacilities,loadFacilities } from '../src/services/data';
import type { Facilities } from '../src/types';
vi.mock('../src/map/PulseMap',()=>({default:({data,onSelect}:{data:Facilities;onSelect:(f:unknown)=>void})=><button onClick={()=>onSelect(data.features[0])}>Select map point</button>}));
const data:Facilities={type:'FeatureCollection',features:[{type:'Feature',id:'1',geometry:{type:'Point',coordinates:[67,25]},properties:{id:'1',name:'Fixture Hospital',category:'Hospital',address:'',operator:'',beds:'',emergency:'',osm_id:'1',source_url:'https://example.com',source_type:'hospital'}},{type:'Feature',id:'2',geometry:{type:'Point',coordinates:[67.1,25]},properties:{id:'2',name:'Fixture Clinic',category:'Clinic',address:'',operator:'',beds:'',emergency:'',osm_id:'2',source_url:'https://example.com',source_type:'clinic'}}]};
beforeEach(()=>{vi.stubGlobal('fetch',vi.fn(async(url:string)=>({ok:true,json:async()=>url.includes('quality')?null:data})));});
it('searches case insensitively and combines categories',()=>{
  expect(filterFacilities(data.features,'HOSP',[])).toHaveLength(1);
  expect(filterFacilities(data.features,'clinic',['Hospital'])).toHaveLength(0);
  expect(categoryCounts(data.features)).toEqual({Hospital:1,Clinic:1});
});
it('shows loading, filters actual rows, and resets',async()=>{
  render(<App/>);expect(screen.getByRole('status')).toBeInTheDocument();
  await screen.findByText('Fixture Clinic');
  fireEvent.change(screen.getByLabelText('Search facilities'),{target:{value:'nonexistent'}});
  expect(screen.getByText('No facilities found')).toBeInTheDocument();
  fireEvent.click(screen.getByText('Reset'));
  expect(screen.getByText('Fixture Hospital')).toBeInTheDocument();
  fireEvent.click(screen.getByRole('checkbox',{name:/Hospital/}));
  expect(screen.queryByText('Fixture Clinic')).not.toBeInTheDocument();
});
it('opens source details from the map and closes them',async()=>{
  render(<App/>);await screen.findByText('Fixture Hospital');
  fireEvent.click(await screen.findByText('Select map point'));
  expect(screen.getByLabelText('Facility details')).toBeInTheDocument();
  expect(screen.getAllByText('Not provided by source')).toHaveLength(2);
  fireEvent.click(screen.getByLabelText('Close details'));
  expect(screen.queryByLabelText('Facility details')).not.toBeInTheDocument();
});
it('shows recoverable fetch failures and retry',async()=>{
  vi.stubGlobal('fetch',vi.fn(async()=>({ok:false,status:403})));
  render(<App/>);await screen.findByRole('alert');
  expect(screen.getByText(/Dataset request failed \(403\)/)).toBeInTheDocument();
  vi.stubGlobal('fetch',vi.fn(async(url:string)=>({ok:true,json:async()=>url.includes('quality')?null:data})));
  fireEvent.click(screen.getByText('Try again'));await screen.findByText('Fixture Hospital');
});
it('rejects malformed dataset coordinates',async()=>{
  vi.stubGlobal('fetch',vi.fn(async()=>({ok:true,json:async()=>({...data,features:[{...data.features[0],geometry:{type:'Point',coordinates:[999,25]}}]})})));
  await expect(loadFacilities(new AbortController().signal)).rejects.toThrow('invalid');
});
it.each([null,{type:'FeatureCollection',features:[null]}])('rejects malformed JSON records with a useful error',async(value)=>{
  vi.stubGlobal('fetch',vi.fn(async()=>({ok:true,json:async()=>value})));
  await expect(loadFacilities(new AbortController().signal)).rejects.toThrow(/Invalid GeoJSON|invalid or duplicate/);
});
it('switches to analytics with current filters',async()=>{
  render(<App/>);await screen.findByText('Fixture Hospital');
  fireEvent.change(screen.getByLabelText('Search facilities'),{target:{value:'hospital'}});
  fireEvent.click(screen.getByRole('button',{name:'Analytics'}));
  await waitFor(()=>expect(screen.getByText(/1 records in the current search/)).toBeInTheDocument());
});
