
async function render(){const s=await (await fetch('/api/state')).json();console.log('AEGIS state',s)}
render();setInterval(render,1500);
