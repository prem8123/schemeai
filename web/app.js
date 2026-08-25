const $ = (id) => document.getElementById(id);

function esc(value){return String(value ?? '').replace(/[&<>\"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));}
function badge(status){return status.replaceAll('_',' ')}

async function checkApi(){
  const base=$('apiUrl').value.replace(/\/$/,'');
  try{const r=await fetch(`${base}/health`); if(!r.ok) throw new Error(); $('status').textContent='API online'; $('status').style.background='#e8f7ee'; $('status').style.color='#16713b';}
  catch{$('status').textContent='API unreachable'; $('status').style.background='#fff0f0'; $('status').style.color='#a11';}
}

$('apiUrl').addEventListener('change',checkApi); checkApi();
$('profileForm').addEventListener('submit',async(e)=>{
 e.preventDefault(); $('error').textContent=''; $('results').innerHTML='<div class="empty">Analyzing your profile…</div>';
 const base=$('apiUrl').value.replace(/\/$/,'');
 const payload={age:Number($('age').value),state:$('state').value,education_level:$('education').value,course:$('course').value||null,category:$('category').value||null,annual_family_income:Number($('income').value),disability:$('disability').checked};
 const params=new URLSearchParams({query:$('query').value,language:$('language').value});
 try{
  const r=await fetch(`${base}/recommend?${params}`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
  if(!r.ok) throw new Error(`API returned ${r.status}`); const data=await r.json();
  $('status').textContent='API online'; $('status').style.background='#e8f7ee'; $('status').style.color='#16713b';
  $('results').innerHTML=data.results.map(item=>`<article class="result"><div class="result-head"><h3>${esc(item.scheme.name)}</h3><span class="badge">${esc(badge(item.status))}</span></div><div class="score">Match score: ${Math.round(item.score*100)}%</div><ul>${item.reasons.map(x=>`<li>${esc(x)}</li>`).join('')}</ul>${item.missing_information?.length?`<div class="missing">Missing information: ${item.missing_information.map(esc).join(', ')}</div>`:''}<p><strong>Benefit:</strong> ${esc(item.scheme.benefit)}</p><p><strong>Documents:</strong> ${item.scheme.documents.map(esc).join(', ')}</p><div class="meta">Evidence: ${esc(item.scheme.source)} · page ${esc(item.scheme.source_page||'N/A')}</div></article>`).join('') || '<div class="empty">No matching schemes found.</div>';
 }catch(err){$('results').innerHTML='<div class="empty">Could not connect to SchemeAI API.</div>'; $('error').textContent=`${err.message}. Set API URL to your deployed FastAPI backend.`; $('status').textContent='API unreachable';}
});
