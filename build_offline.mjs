/** Build a self-contained reference from the repository Markdown. */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
const root = path.dirname(fileURLToPath(import.meta.url));
const markedPath = require.resolve('marked', { paths: [root, process.env.CODEX_PRIMARY_RUNTIME_NODE_MODULES || root] });
const { marked } = await import(pathToFileURL(markedPath).href);
const esc = x => String(x).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
const pages = [
  ['readme','README.md','Overview'],
  ...fs.readdirSync(root).filter(f=>/^\d{2}-.*\.md$/.test(f)).sort().map(f=>[
    f.slice(0,2), f,
    ({'00':'Foundations','01':'1 · Transactions','02':'2 · Event sourcing','03':'3 · CDC','04':'4 · Sagas','05':'5 · Coordination','06':'6 · CAP','07':'7 · Distributed cache','08':'Combined transaction example','09':'Reliability companions','10':'Design questions','11':'Sources and references','12':'Small glossary','13':'Documented enterprise examples'})[f.slice(0,2)]
  ]),
  ['lab','FAILURE_MODELS.md','Failure models'],
];
const route = new Map(pages.map(([id,p])=>[path.resolve(root,p),id]));
const concepts = [
 ['01','transactions','Distributed transactions','One action, several data owners. Decide the commit boundary.','Loan capacity commits, but agreement creation fails. A transaction in one service cannot roll back the other.','Choose a local transaction, supported 2PC, or a saga based on the actual boundary.'],
 ['02','event-sourcing','Event sourcing','Business facts are the authoritative history.','OfferAccepted → CapacityReserved → AgreementPrepared → LoanActivated. Apply the stream to derive the loan state.','Publishing events alone is not event sourcing.'],
 ['03','cdc','Change data capture','Follow committed storage changes into another view.','A legacy status update reaches an indexer, then adviser search catches up.','Plan the initial snapshot, checkpoints, duplicates, deletes, and retention gaps.'],
 ['04','saga','Sagas','Local commits plus a business recovery plan.','If agreement preparation fails, release reservation R123. If release fails, keep recovery pending.','Compensation is new work, not a global rollback.'],
 ['05','orchestration','Choreography or orchestration','Who owns the decision about the next step?','Coordinate required loan activation steps with a durable workflow. Let independent reporting react to final facts.','Either style still needs safe retries and an owned failure path.'],
 ['06','cap','CAP theorem','Partition policy defines which operations may proceed without coordination.','Two isolated sides each see capacity 100 and each receive a request for 80. Both cannot independently accept safely.','For reservation, preserve authoritative coordination; for browsing, a stale view may be acceptable.'],
 ['07','cache','Distributed cache','Shared fast reads, with an explicit stale-data policy.','Several API instances use the same indicative product cache. Binding acceptance validates authoritative offer terms.','Expiry and invalidation do not make cached decisions strongly consistent.'],
];
let tour = '<h1>Enterprise system design notes</h1><p class="lead">Consistency, coordination, event-driven integration, and caching: the guarantees, tradeoffs, and failure boundaries.</p><p class="callout">Sample invariant: <strong>an accepted reservation must not make available lending capacity negative.</strong> The examples use loan acceptance to connect the concepts.</p>';
for(const [id,img,title,hook,example,trap] of concepts){
 const src='data:image/svg+xml;base64,'+fs.readFileSync(path.join(root,img+'.svg')).toString('base64');
 tour+=`<section class="tour-card"><p class="eyebrow">CONCEPT ${id}</p><h2>${title}</h2><p class="hook">${hook}</p><img src="${src}" alt="${esc(title)} diagram" loading="lazy"><p><strong>Example:</strong> ${example}</p><p class="trap">${trap}</p><a class="chapter-link" href="#p-${id}">Technical notes →</a></section>`;
}
tour+='<p class="callout">The supporting notes cover outbox/inbox reliability, ordering, retries, and operational recovery.</p>';
let articles=`<article id="p-tour" data-title="Concept overview">${tour}</article>`;
for(const [id,p,title] of pages){
 let html=marked.parse(fs.readFileSync(path.join(root,p),'utf8'),{gfm:true});
 html=html.replace(/src="([^\"]+)"/g,(match,src)=>{
  if(/^[a-z]+:/i.test(src))return match;
  const f=path.resolve(path.dirname(path.join(root,p)),src);
  return fs.existsSync(f)&&f.endsWith('.svg') ? 'src="data:image/svg+xml;base64,'+fs.readFileSync(f).toString('base64')+'"' : match;
 });
 html=html.replace(/href="([^\"]+)"/g,(match,href)=>{
  if(/^[a-z]+:/i.test(href))return match+' target="_blank" rel="noopener noreferrer"';
  const [file,fragment]=href.split('#');
  const target=route.get(path.resolve(path.dirname(path.join(root,p)),file));
  if(target)return 'href="#p-'+target+'"';
  const f=path.resolve(path.dirname(path.join(root,p)),file);
  if(fs.existsSync(f)&&f.endsWith('.py'))return 'href="data:text/plain;base64,'+fs.readFileSync(f).toString('base64')+'" download="'+esc(path.basename(f))+'"';
  return match;
 });
 articles+=`<article id="p-${id}" data-title="${esc(title)}" hidden>${html}</article>`;
}
const links=[['tour','Concept overview'],...pages.map(([id,p,t])=>[id,t])];
const nav=links.map(([id,title])=>`<a href="#p-${id}" data-route="p-${id}">${esc(title)}</a>`).join('');
const options=links.map(([id,title])=>`<option value="p-${id}">${esc(title)}</option>`).join('');
const html=`<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Enterprise System Design · Notes</title><style>
:root{color-scheme:light;--navy:#15324f;--blue:#245b9e;--muted:#536478;--bg:#f3f6fa;--line:#d6e0eb;--green:#137562}*{box-sizing:border-box}body{margin:0;font:17px/1.65 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;color:#243c53;background:var(--bg)}a{color:var(--blue);text-underline-offset:3px}button,input,select{font:inherit}button{cursor:pointer}aside{position:fixed;inset:0 auto 0 0;width:280px;padding:30px 22px;background:var(--navy);color:white;overflow:auto}aside h2{font-size:20px;line-height:1.3;margin:0 0 8px}aside p{font-size:13px;color:#bfd2e5;margin:0 0 22px}aside input{width:100%;padding:10px 12px;border:1px solid #7a98b6;border-radius:8px;background:#fff;margin-bottom:18px}nav a{display:block;color:#dbe8f5;text-decoration:none;padding:8px 12px;font-size:15px;border-radius:7px;margin:2px 0}nav a.active{background:#315779;color:#fff;font-weight:700}nav a:hover{background:#294d6c}main{max-width:1190px;margin-left:280px;padding:22px 44px 80px}.toolbar{display:flex;flex-wrap:wrap;gap:8px;align-items:center;justify-content:space-between;margin-bottom:24px;color:var(--muted);font-size:13px}.toolbar button{font-size:13px;padding:7px 10px;background:#fff;border:1px solid var(--line);border-radius:6px}.mobile-nav{display:none}article{background:#fff;border:1px solid var(--line);border-radius:16px;padding:38px;box-shadow:0 3px 16px #15324f05}article[hidden]{display:none}h1{font-size:34px;line-height:1.2;letter-spacing:-.8px;margin:0 0 23px;color:var(--navy)}h2{font-size:24px;line-height:1.3;margin:36px 0 16px;color:var(--navy)}h3{font-size:20px}p{margin:15px 0}img{display:block;width:100%;height:auto;border:1px solid #e0e7ef;border-radius:12px;margin:24px 0;cursor:zoom-in}.lead{font-size:20px;color:var(--muted)}.callout{padding:18px 21px;background:#edf4ff;border-left:4px solid var(--blue);border-radius:5px}.tour-card{border-top:1px solid var(--line);padding-top:24px;margin-top:38px}.tour-card h2{margin:0 0 14px;font-size:28px}.eyebrow{font-size:12px;letter-spacing:1.8px;color:var(--green);font-weight:800}.hook{font-size:21px;font-weight:650;color:var(--navy)}.trap{border-left:3px solid #d29a38;padding-left:16px;color:#755518}.chapter-link{display:inline-block;font-weight:700;margin:9px 0}table{display:block;max-width:100%;overflow-x:auto;border-collapse:collapse;font-size:15px;margin:24px 0}th,td{padding:12px 14px;border:1px solid var(--line);text-align:left;vertical-align:top;min-width:110px}th{background:#edf3f9;color:var(--navy)}tr:nth-child(even){background:#fafcff}details{border:1px solid var(--line);border-radius:10px;margin:18px 0;padding:0 18px}summary{cursor:pointer;padding:15px 0;line-height:1.5;color:var(--navy)}details[open]{padding-bottom:12px}details>p,details>ul{font-size:16px}blockquote{margin:20px 0;padding:5px 20px;border-left:4px solid var(--green);background:#eff8f5}pre{overflow:auto;background:#10293f;color:#e4effb;padding:20px;border-radius:9px;font-size:13px;line-height:1.7}code{font: .88em ui-monospace,SFMono-Regular,Consolas,monospace}p code,td code,li code{background:#edf2f7;padding:2px 5px;border-radius:4px}li{margin:8px 0}footer{text-align:center;font-size:12px;color:var(--muted);padding:26px 0}dialog{width:min(98vw,1450px);max-height:95vh;border:1px solid var(--line);border-radius:12px;padding:18px}dialog::backdrop{background:#15324fbf}dialog img{margin:14px 0 0;border:0;cursor:auto}dialog button{float:right;background:#edf4ff;border:0;padding:8px 14px;border-radius:6px}#no-js{background:#fff3df;padding:12px}.empty{font-size:13px;color:#dbe8f5}
@media(max-width:850px){aside{display:none}.mobile-nav{display:block;width:100%;padding:12px;background:var(--navy);color:white;border:0;border-radius:8px;margin-bottom:15px}main{margin:0;padding:14px 12px 50px}article{padding:24px 19px;border-radius:12px}h1{font-size:29px}.toolbar{margin-bottom:16px}.lead{font-size:18px}h2{font-size:23px}.tour-card h2{font-size:25px}body{font-size:16px}img{margin:18px 0}.hook{font-size:19px}th,td{padding:9px 11px}.toolbar>span{width:100%}}
@media print{aside,.toolbar,.mobile-nav,dialog{display:none!important}main{margin:0;padding:0;max-width:none}article{border:0;padding:0;box-shadow:none}a{color:inherit}details{break-inside:avoid}img{break-inside:avoid;max-height:650px;object-fit:contain}body{font-size:11pt;background:white}h1{font-size:24pt}}
</style></head><body><aside><h2>System design<br>notes</h2><p>Consistency · coordination · recovery<br>Reviewed 25 October 2026</p><input id="search" type="search" aria-label="Find a section by concept or keyword" placeholder="Find a concept…"><nav aria-label="Sections">${nav}</nav><p id="no-results" class="empty" hidden>No matching section. Try another term.</p></aside><main><select class="mobile-nav" aria-label="Choose a section">${options}</select><div class="toolbar"><span id="position">Concept overview · click any diagram to enlarge</span><div><button id="expand">Open details</button> <button id="collapse">Close details</button> <button id="print">Print section</button></div></div><noscript><p id="no-js">Enable JavaScript for section navigation. The visual tour remains available below.</p></noscript>${articles}<footer>Engineering notes · generic transaction examples · primary-source references</footer></main><dialog aria-label="Enlarged diagram"><button id="close-dialog">Close</button><img alt="Enlarged concept diagram"></dialog><script>
const articles=[...document.querySelectorAll('article')];
const select=document.querySelector('select');
function show(){const wanted=location.hash.slice(1)||'p-tour';const found=document.getElementById(wanted);const active=found&&found.tagName==='ARTICLE'?found:articles[0];articles.forEach(a=>a.hidden=a!==active);document.querySelectorAll('nav a').forEach(a=>{const current=a.dataset.route===active.id;a.classList.toggle('active',current);if(current)a.setAttribute('aria-current','page');else a.removeAttribute('aria-current')});select.value=active.id;document.getElementById('position').textContent=active.dataset.title+' · click a diagram to enlarge';document.title=active.dataset.title+' · Enterprise System Design';window.scrollTo(0,0)}
window.addEventListener('hashchange',show);select.addEventListener('change',()=>location.hash=select.value);show();
document.getElementById('search').addEventListener('input',e=>{const term=e.target.value.toLowerCase().trim();let count=0;document.querySelectorAll('nav a').forEach(a=>{const page=document.getElementById(a.dataset.route);const match=page.textContent.toLowerCase().includes(term);a.hidden=!match;a.style.display=match?'block':'none';if(match)count++});document.getElementById('no-results').hidden=count!==0});
for(const [id,open] of [['expand',true],['collapse',false]])document.getElementById(id).addEventListener('click',()=>document.querySelector('article:not([hidden])').querySelectorAll('details').forEach(d=>d.open=open));
document.getElementById('print').addEventListener('click',()=>window.print());
const dialog=document.querySelector('dialog');document.querySelectorAll('article img').forEach(img=>img.addEventListener('click',()=>{dialog.querySelector('img').src=img.src;dialog.querySelector('img').alt=img.alt;dialog.showModal()}));document.getElementById('close-dialog').addEventListener('click',()=>dialog.close());dialog.addEventListener('click',e=>{if(e.target===dialog)dialog.close()});
</script></body></html>`;
fs.writeFileSync(path.join(root,'START_HERE.html'),html);
console.log('Built self-contained reference with concept overview and '+pages.length+' reference chapters');
