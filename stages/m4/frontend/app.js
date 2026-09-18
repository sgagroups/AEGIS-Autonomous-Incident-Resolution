
async function getState(){return (await fetch('/api/state')).json()}
async function render(){const s=await getState();document.getElementById('alerts').textContent=s.alert_count;document.getElementById('incidents').textContent=s.incident_count;
const vals=Object.values(s.trust||{});document.getElementById('trust').textContent=vals.length?Math.round(Math.max(...vals)*100)+'%':'0%';
const host=document.getElementById('list');host.innerHTML='';for(const i of s.incidents){const row=document.createElement('div');row.className='item';row.innerHTML=`<div><b>${i.incident_id}</b><div class="muted">${i.root_cause}</div></div><div><span class="badge ${i.severity==='CRITICAL'?'danger':'warn'}">${i.severity}</span><div class="muted">${i.execution}</div></div>`;host.appendChild(row)}}
async function simulate(){const scenarios=['db_pool_exhaustion','memory_leak','network_gateway_failure','ambiguous'];const s=scenarios[Math.floor(Math.random()*scenarios.length)];await fetch('/api/simulate/'+s,{method:'POST'});render()}render();setInterval(render,1500)
