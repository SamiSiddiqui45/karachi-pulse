import { Component,type ReactNode } from 'react';
export default class MapErrorBoundary extends Component<{children:ReactNode},{failed:boolean}>{
  state={failed:false};
  static getDerivedStateFromError(){return {failed:true};}
  render(){return this.state.failed?<div className="state-panel map-fallback" role="alert"><strong>Map rendering is unavailable</strong><p>This browser may not support WebGL. Search, facility lists and analytics remain available.</p><button onClick={()=>this.setState({failed:false})}>Retry map</button></div>:this.props.children;}
}
