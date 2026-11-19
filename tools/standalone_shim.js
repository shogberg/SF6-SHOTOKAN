(function(){const calcs={},draws={};const cache={};
window.dash={colors:['var(--c0)','var(--c1)'],
data(id){if(id in window.__DATA__)return{status:'ok',data:window.__DATA__[id]};if(calcs[id]){if(!(id in cache)){const c=calcs[id];cache[id]=c.fn(...c.inputs.map(i=>this.data(i).data));}return{status:'ok',data:cache[id]};}return{status:'missing',data:[]};},
calc(id,c){calcs[id]=c;},loader(){},onData(fn){fn();},params(){return{};},setParams(){},resetParams(){},setLink(){},refresh(){},
draw(name,fn){if(fn===undefined){(draws[name]||[]).forEach(f=>f());return;}const run=()=>document.querySelectorAll('[data-draw="'+name+'"]').forEach(el=>{if(typeof fn==='function')fn(el);});draws[name]=[run];if(document.readyState!=='loading')setTimeout(run,0);else document.addEventListener('DOMContentLoaded',run);let t;window.addEventListener('resize',()=>{clearTimeout(t);t=setTimeout(run,150);});}};})();
