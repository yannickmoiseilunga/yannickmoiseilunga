'use strict';
let current=null, currentId='', running=false;
const $=id=>document.getElementById(id);
const h=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const fmt=(n,d=3)=>n===undefined||n===null||!Number.isFinite(Number(n))?'—':Number(n).toFixed(d);
function toast(t){const el=$('toast');el.textContent=t;el.style.display='block';setTimeout(()=>{if(el.textContent===t)el.style.display='none'},4400)}
async function request(path,opts){let r=await fetch(path,opts);let v=await r.json();if(!r.ok)throw new Error(v.error||`HTTP ${r.status}`);return v}
function post(path,body){return request(path,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)})}
function navigate(page){document.querySelectorAll('.panel').forEach(x=>x.classList.toggle('active',x.id===page));document.querySelectorAll('.tab').forEach(x=>x.classList.toggle('active',x.dataset.tab===page))}
document.querySelectorAll('.tab').forEach(e=>e.addEventListener('click',()=>navigate(e.dataset.tab)));
async function refreshRuns(){try{let v=await request('/api/runs');let select=$('run-select');let old=select.value;select.innerHTML=v.runs.length?v.runs.map(n=>`<option value="${h(n)}">${h(n)}</option>`).join(''):'<option value="">No previous runs</option>';if(v.runs.includes(old))select.value=old;else if(currentId&&v.runs.includes(currentId))select.value=currentId;if(!current&&v.runs.length){await load(v.runs[0]);}}catch(e){toast(e.message)}}
async function load(id){if(!id)return;try{let v=await request('/api/result?run='+encodeURIComponent(id));current=v;currentId=id;$('run-select').value=id;$('download-link').href='/api/download?run='+encodeURIComponent(id);$('download-link').classList.remove('disabled');$('run-tag').textContent=id.slice(0,22);if(current.type){renderResearch(current);if(current.type==='real_v2')navigate('real');if(current.type==='real_v3')navigate('transport');}else{render();}}catch(e){toast(e.message)}}
function render(){if(!current)return;let rows=current.rows||[],findings=current.findings||[];$('kpi-rows').textContent=rows.length;$('kpi-hypotheses').textContent=findings.length||'—';$('kpi-consistent').textContent=findings.filter(f=>f.status.startsWith('consistent')).length;let info=rows.find(r=>r.experiment==='sensors_full'&&r.model==='linear');$('kpi-info').textContent=info?fmt(info.mutual_information_bits,2):'—';
 $('findings-preview').classList.remove('empty');$('findings-preview').innerHTML=findings.slice(0,6).map(f=>`<div class="finding-mini"><div><strong>${h(f.id)} · ${h(f.name)}</strong><small>effect ${fmt(f.effect)} · threshold ${fmt(f.threshold)}</small></div><span class="pill ${f.status.startsWith('consistent')?'good':f.status.startsWith('contradicted')?'bad':''}">${h(f.status)}</span></div>`).join('')||'<div class="empty">No preregistered comparisons for this imported study.</div>';
 let list=Array.from(new Set(rows.map(r=>r.experiment))).sort();let sel=$('experiment-filter'),old=sel.value;sel.innerHTML='<option value="all">All experiments</option>'+list.map(x=>`<option value="${h(x)}">${h(x.replace(/_/g,' '))}</option>`).join('');if(list.includes(old))sel.value=old;
 let atlas=current.corollary_map||{};$('corollary-grid').innerHTML=Object.keys(atlas).map(title=>`<div class="corollary"><strong>${h(title)}</strong><p>Prespecified test mechanisms and empirical controls linked to this proposition.</p><span>${atlas[title].map(h).join(' · ')}</span></div>`).join('');$('hypotheses-full').innerHTML=findings.map(f=>`<div class="hypothesis"><strong>${h(f.id)} · ${h(f.name)}</strong><small>${h(f.status)} · measured effect ${fmt(f.effect)} · 95% seed bootstrap ${f.bootstrap_95?.map(x=>fmt(x)).join(' to ')||'—'} · ${h(f.analysis)}</small></div>`).join('')||'<div class="empty">No synthetic hypotheses in this dataset.</div>';
 chartAndTable();renderForecasts()}
function chartAndTable(){if(!current)return;let ex=$('experiment-filter').value,metric=$('metric-filter').value;let all=current.rows||[];let rows=all.filter(r=>ex==='all'||r.experiment===ex);let grouped={};for(let r of rows){if(!Number.isFinite(Number(r[metric]))||r[metric]===undefined)continue;let key=r.experiment+' · '+r.model+' · '+r.domain;(grouped[key]??=[]).push(Number(r[metric]))}let entries=Object.entries(grouped).map(([name,v])=>({name,mean:v.reduce((a,b)=>a+b,0)/v.length,count:v.length})).sort((a,b)=>b.mean-a.mean).slice(0,26);let max=Math.max(.01,...entries.map(e=>e.mean));let width=960,height=Math.max(260,entries.length*32+44);let svg=`<svg viewBox="0 0 ${width} ${height}" role="img" aria-label="Experiment measurements">`;for(let i=0;i<entries.length;i++){let y=32+i*32,e=entries[i],barX=360,barW=Math.max(1,(width-475)*e.mean/max);svg+=`<text x="10" y="${y+13}" font-size="12" fill="#526b7e">${h(e.name.length>51?e.name.slice(0,48)+'…':e.name)}</text><rect x="${barX}" y="${y}" width="${barW}" height="18" rx="3" fill="#3479af"/><text x="${barX+barW+9}" y="${y+14}" font-size="12" fill="#244761">${fmt(e.mean)} (${e.count})</text>`}svg+='</svg>';$('chart-area').innerHTML=entries.length?svg:'<div class="empty">This measure is not available for the selected trials.</div>';let agg={};for(let r of rows){let key=r.experiment+'|'+r.model+'|'+r.domain;(agg[key]??=[]).push(r)}let summary=Object.values(agg).map(rr=>{let f=rr[0],mean=k=>{let arr=rr.map(x=>x[k]).filter(x=>x!==undefined&&x!==null);return arr.length?arr.reduce((a,b)=>a+b,0)/arr.length:null};return{experiment:f.experiment,model:f.model,domain:f.domain,accuracy:mean('accuracy'),brier:mean('brier'),info:mean('mutual_information_bits'),bayes:mean('bayes_accuracy'),params:f.params}});
 $('observation-tbody').innerHTML=summary.slice(0,180).map(r=>`<tr><td>${h(r.experiment)}</td><td>${h(r.model)}</td><td>${h(r.domain)}</td><td>${fmt(r.accuracy)}</td><td>${fmt(r.brier)}</td><td>${fmt(r.info)}</td><td>${fmt(r.bayes)}</td><td>${r.params??'—'}</td></tr>`).join('')||'<tr><td colspan="8" class="empty">No observations.</td></tr>'}
function renderForecasts(){if(!current)return;let L=current.law_validation||{},preds=current.law_forecasts||[];
 $('forecast-mae').textContent=fmt(L.mae);$('forecast-constrained').textContent=fmt(L.constrained_mae);$('forecast-baseline').textContent=fmt(L.baseline_mae);$('forecast-violations').textContent=L.above_bayes_ceiling_predictions??'—';
 const width=790,height=405,padding=53,span=height-padding*2,step=width-padding*2;
 let svg=`<svg viewBox="0 0 ${width} ${height}" role="img" aria-label="Heldout predictions versus measured accuracy"><rect x="${padding}" y="${padding}" width="${step}" height="${span}" fill="#f8fbfd" stroke="#dce5ec"/><line x1="${padding}" y1="${height-padding}" x2="${width-padding}" y2="${padding}" stroke="#8ca5b7" stroke-dasharray="6 5" stroke-width="2"/>`;
 for(let tick=0;tick<=5;tick++){let v=tick/5,x=padding+step*v,y=height-padding-span*v;svg+=`<text x="${x}" y="${height-padding+24}" text-anchor="middle" font-size="11" fill="#8191a2">${v.toFixed(1)}</text><text x="${padding-12}" y="${y+4}" text-anchor="end" font-size="11" fill="#8191a2">${v.toFixed(1)}</text>`}
 for(let r of preds){let x=padding+step*r.constrained_predicted,y=height-padding-span*r.observed;svg+=`<circle cx="${x}" cy="${y}" r="3.7" fill="${r.absolute_error>.25?'#b45648':'#2773aa'}" opacity=".63"><title>${h(r.heldout_experiment+' '+r.model+' predicted='+fmt(r.constrained_predicted)+' observed='+fmt(r.observed))}</title></circle>`}
 svg+=`<text x="${width/2}" y="${height-3}" text-anchor="middle" font-size="13" fill="#567084">Bayes-constrained predicted accuracy</text><text transform="translate(16,${height/2}) rotate(-90)" text-anchor="middle" font-size="13" fill="#567084">Observed accuracy</text></svg>`;$('forecast-scatter').innerHTML=preds.length?svg:'<div class="empty">No out-of-condition synthetic forecasts available for this run.</div>';
 $('forecast-table').innerHTML=preds.slice().sort((a,b)=>b.constrained_abs_error-a.constrained_abs_error).slice(0,30).map(r=>`<tr><td>${h(r.heldout_experiment)}</td><td>${h(r.model)}</td><td>${fmt(r.predicted)}</td><td>${fmt(r.constrained_predicted)}</td><td>${fmt(r.observed)}</td><td>${fmt(r.constrained_abs_error)}</td><td>${fmt(r.bayes_ceiling)}</td></tr>`).join('')||'<tr><td colspan="7" class="empty">No forecasts for an external dataset.</td></tr>';
}
$('experiment-filter').addEventListener('change',chartAndTable);$('metric-filter').addEventListener('change',chartAndTable);$('run-select').addEventListener('change',e=>load(e.target.value));
async function launch(kind,payload){if(running)return;try{let path={synthetic:'/api/start',csv:'/api/csv',ollama:'/api/ollama',real:'/api/real',transport:'/api/transport',text:'/api/text',local:'/api/local'}[kind];await post(path,payload);running=true;$('progress-area').hidden=false;document.querySelectorAll('.primary').forEach(b=>b.disabled=true);toast('Study started. Reports will be saved to the local reports folder.')}catch(e){toast(e.message)}}
$('run-button').addEventListener('click',()=>launch('synthetic',{preset:$('preset').value,seed:Number($('seed').value)}));
$('csv-button').addEventListener('click',async()=>{let f=$('csv-file').files?.[0];if(!f)return toast('Select a CSV file.');if(f.size>7_000_000)return toast('CSV limit for browser upload: 7 MB. Use the command line for larger files.');let content=await f.text();launch('csv',{filename:f.name,content,target:$('csv-target').value.trim(),domain:$('csv-domain').value.trim(),train_domain:$('csv-train').value.trim(),seed:Number($('seed').value),seeds:3})});
$('ollama-refresh').addEventListener('click',async()=>{try{let v=await request('/api/models');$('ollama-select').innerHTML=v.models.map(m=>`<option value="${h(m)}">${h(m)}</option>`).join('')||'<option value="">No models found</option>';$('ollama-hint').textContent=v.notice||`${v.models.length} installed model(s) available.`}catch(e){toast(e.message)}});
$('ollama-button').addEventListener('click',()=>launch('ollama',{model:$('ollama-select').value,count:Number($('ollama-count').value),seed:Number($('seed').value)}));
async function monitor(){try{let v=await request('/api/status');if(v.status==='running'){running=true;$('progress-area').hidden=false;let p=v.progress||{};let val=100*(p.completed||0)/(p.total||1);$('progress-fill').style.width=Math.min(98,Math.max(0,val))+'%';$('progress-label').textContent=p.detail||'Running';$('progress-pct').textContent=Math.round(val)+'%';document.querySelectorAll('.primary').forEach(b=>b.disabled=true)}else if(running){running=false;$('progress-area').hidden=true;document.querySelectorAll('.primary').forEach(b=>b.disabled=false);if(v.status==='finished'){toast('Study finished; reports and raw predictions exported.');await refreshRuns();await load(v.run);if(v.kind==='transport')navigate('transport');else if(v.kind==='real'||v.kind==='text'||v.kind==='local')navigate('real');else navigate('experiments')}else if(v.status==='failed'){toast('Experiment failed: '+v.error)}}}catch(e){if(running)toast('Unable to connect to local laboratory: '+e.message)}}
refreshRuns();monitor();setInterval(monitor,1100);

// V2 empirical evidence is intentionally kept separate from V1 synthetic results.
function renderResearch(result){
 const kind=result.type;
 if(kind==='real_v3'){
    let rs=result.summary||[];
    let ids=['v3-mae-datasets','v3-mae-arch','v3-mae-double'];
    for(let i=0;i<3;i++){let x=rs[i];$(ids[i]).textContent=x?fmt(x.itl_macro_mae):'—';}
    $('v3-n-seeds').textContent=result.seeds??'—';
    $('v3-results').innerHTML=rs.map(x=>`<tr><td>${h(x.regime)}</td><td>${fmt(x.probe_macro_mae)}</td><td>${fmt(x.v2_macro_mae)}</td><td>${fmt(x.itl_macro_mae)}</td><td class="${x.itl_gain_over_probe>0?'success':'failure'}">${x.itl_gain_over_probe>=0?'+':''}${fmt(x.itl_gain_over_probe)}</td><td>${h((x.itl_gain_vs_probe_ci95||[]).map(q=>fmt(q)).join(' .. '))}</td><td>${h(x.decision)}</td></tr>`).join('');
    let w=result.impossibility||{};
    $('v3-impossibility').textContent=`Two worlds with identical visible evidence produce accuracies ${fmt(w.world_one_accuracy)} and ${fmt(w.world_two_accuracy)}. The unavoidable worst-case forecasting error is at least ${fmt(w.minimax_absolute_error_lower_bound)}. `+(result.limitations||'');
    $('v3-coverage').textContent='Exploratory source-fit interval coverage: '+(result.interval_coverage||[]).map(x=>x.regime+' '+fmt(x.empirical_coverage)).join(' · ')+'. These are not guaranteed coverage levels for unseen worlds.';
    return;
 }
 $('real-run-status').textContent='Selected study: '+(currentId||'not available')+' · '+kind;
 if(kind==='real_v2'){
  const n=result.settings||{},s=result.summary||[],hypotheses=result.hypotheses||[],groups=result.groups||[];
  $('real-kpi-cells').textContent=(n.seeds||'—')&&n.datasets?n.seeds*n.datasets.length*24:'—';
  for(let [id,name] of [['real-kpi-dataset','unseen_dataset'],['real-kpi-arch','unseen_architecture'],['real-kpi-double','unseen_both']]){
   let item=s.find(x=>x.test_type===name);$(id).textContent=item?fmt(item.law_macro_mae):'—';
  }
  $('real-forecast-rows').innerHTML=s.map(t=>`<tr><td>${h(t.test_type.replaceAll('_',' '))}</td><td>${fmt(t.law_macro_mae)}</td><td>${fmt(t.probe_only_macro_mae)}</td><td>${fmt(t.baseline_macro_mae)}</td><td class="${t.improvement_over_probe_mae>=0?'success':'failure'}">${t.improvement_over_probe_mae>=0?'+':''}${fmt(t.improvement_over_probe_mae)}</td></tr>`).join('');
  $('real-hypotheses').innerHTML=hypotheses.map(f=>`<div class="hypothesis"><strong>${h(f.id)} · ${h(f.name)}</strong><small><b class="${f.status==='supported_within_tested_datasets'?'success':'failure'}">${h(f.status.replaceAll('_',' '))}</b> · effect ${fmt(f.effect)} · predefined MDE ${fmt(f.minimum_effect)} · adjusted p ${fmt(f.holm_adjusted_p)}<br>Across-dataset CI: ${h((f.cluster_ci95||[]).map(x=>fmt(x)).join(' .. '))}</small></div>`).join('');
  $('real-hardest').innerHTML=groups.slice().sort((a,b)=>b.law_mae-a.law_mae).slice(0,14).map(g=>`<tr><td>${h(g.held_dataset||'all')}</td><td>${h(g.held_architecture||'all')}</td><td>${fmt(g.law_mae)}</td><td>${fmt(g.probe_only_mae)}</td><td>${fmt(g.correction_weight,2)}</td></tr>`).join('');
  $('real-other-results').innerHTML=`<div class="theory-note">${h(result.limitations||'')} · ${h(n.confirmatory_seed_count_met?'20-seed minimum met':'Exploratory underpowered study; minimum planned seed count not met')} · ${h((result.failures||[]).length)} excluded runs. <a href="/api/download?run=${encodeURIComponent(currentId)}">Download frozen protocol, all measurements, and failed forecasts.</a></div>`;
 }else if(kind==='local_pretrained_model'){
  let entries=Object.entries(result.summary||{});
  $('real-other-results').innerHTML='<h4>Separate pretrained-model evaluation</h4>'+entries.map(([arm,info])=>`<div class="theory-note">${h(arm)}: accuracy ${fmt(info.accuracy)} · format success ${fmt(info.format_success)} · ${info.requests} requests · ${info.errors} errors</div>`).join('');
 }else if(kind==='real_text_v2'){
  let arr=result.rows||[],agg={};for(let r of arr){let k=r.model+' / '+r.intervention;(agg[k]??=[]).push(r.accuracy)}
  $('real-other-results').innerHTML='<h4>Independent text benchmark: official train/test split</h4>'+Object.entries(agg).map(([name,values])=>`<div class="theory-note">${h(name)} — mean accuracy ${fmt(values.reduce((a,b)=>a+b,0)/values.length)} (${values.length} seeds)</div>`).join('');
 }
}
$('real-run').addEventListener('click',async()=>{
 const datasets=Array.from(document.querySelectorAll('.research-dataset:checked')).map(c=>c.value);
 const f=$('real-extra-csv').files?.[0];
 if(datasets.length+(f?1:0)<2)return toast('Select at least two datasets including any custom CSV');
 let payload={datasets,seeds:Number($('real-seeds').value),seed:Number($('real-seed').value),cap:Number($('real-cap').value)};
 if(f){if(f.size>7_000_000)return toast('CSV exceeds browser upload limit. Use --real-csv in the CLI.');
  payload.external_csv=await f.text();payload.external_target=$('real-extra-target').value.trim();
  payload.external_domain=$('real-extra-domain').value.trim();payload.external_base=$('real-extra-base').value.trim()||null;}
 launch('real',payload);
});
$('text-run').addEventListener('click',()=>launch('text',{seeds:Number($('real-seeds').value),seed:Number($('real-seed').value)}));
$('local-run').addEventListener('click',async()=>{
 let f=$('local-jsonl').files?.[0];if(!f)return toast('Choose a JSONL benchmark with question and answer fields');
 if(f.size>8_000_000)return toast('JSONL exceeds browser-upload limit');
 launch('local',{filename:f.name,content:await f.text(),model:$('local-model').value.trim(),count:Number($('local-count').value)});
});
request('/api/power').then(v=>{$('real-required-seeds').textContent=v.power.chosen_seeds;
 $('real-seeds').value=v.power.chosen_seeds;
}).catch(()=>{});

$('transport-run').addEventListener('click',()=>launch('transport',{seeds:Number($('transport-seeds').value),cap:Number($('transport-cap').value)}));
