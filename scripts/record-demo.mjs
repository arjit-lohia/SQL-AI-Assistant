// A real timed, captioned recording of the running local app. No mocked APIs.
import {chromium} from '@playwright/test';
import {mkdir,writeFile,unlink} from 'node:fs/promises';
import path from 'node:path';
const base=process.env.DEMO_URL||'http://127.0.0.1:8000';
await mkdir('artifacts',{recursive:true});
const browser=await chromium.launch();
const context=await browser.newContext({viewport:{width:1440,height:1000},recordVideo:{dir:'artifacts',size:{width:1440,height:1000}},reducedMotion:'reduce',acceptDownloads:true});
const page=await context.newPage();
const transcript=[],started=Date.now();
async function caption(title,text){
  const timestamp=((Date.now()-started)/1000).toFixed(1);transcript.push(`${timestamp}s — ${title}\n${text}\n`);console.log(`${timestamp}s: ${title}`);
  await page.evaluate(({title,text})=>{let el=document.getElementById('demo-caption');if(!el){el=document.createElement('div');el.id='demo-caption';el.setAttribute('style','position:fixed;z-index:9999;bottom:12px;left:50%;transform:translateX(-50%);width:min(970px,94vw);padding:14px 22px;background:#132e28f5;color:#edf9f2;border:1px solid #73b49a;border-radius:9px;box-shadow:0 5px 20px #0003;font-family:Arial,sans-serif;pointer-events:none;text-align:center;');document.body.appendChild(el);}el.replaceChildren();const h=document.createElement('strong');h.textContent=title;h.style.cssText='display:block;font-size:15px;margin-bottom:6px;color:#b8e3cf;';const p=document.createElement('div');p.textContent=text;p.style.cssText='font-size:14px;line-height:1.5;';el.append(h,p);},{title,text});
}
async function hold(seconds){await new Promise(r=>setTimeout(r,seconds*1000));}
async function send(text,mode='generate'){
  await page.getByLabel('Task mode').selectOption(mode);await page.getByLabel('Your SQL or database question').fill(text);await hold(1.5);await page.getByRole('button',{name:'Send question',exact:true}).click();await page.getByRole('button',{name:'Cancel request'}).waitFor({state:'hidden'});await hold(.8);
}
try{
  await page.goto(base);await page.getByText('Sample database connected',{exact:true}).waitFor();
  const health = await (await page.request.get(base + '/api/health')).json();
  if (health.provider !== 'sample') throw new Error('Use a keyless local server for this sample-mode recording. Your live server is left unchanged.');
  await caption('QueryAtlas · a focused SQL assistant','This recording uses the clearly labeled keyless sample mode. A server-side Groq key enables full schema-bound AI. All results shown are real SQLite data.');await hold(10);
  await page.getByRole('button',{name:'View schema',exact:true}).click();await caption('A real sample database, ready for serverless hosting','Six related business tables contain 1,426 synthetic records. The bundled database is immutable and is opened read-only at runtime.');await hold(12);await page.getByRole('button',{name:'Close dialog'}).click();
  await caption('Natural language → validated SQL → actual results','Ask for customers in California. Every query must pass syntax, table, column, function and foreign-key checks before it can be returned.');await send('Show customers in California');await hold(13);
  await page.getByRole('tab',{name:'Explanation',exact:true}).click();await caption('SQL explained in plain English','The explanation describes the accepted query. Independent validation checks and existing-index advice are visible here.');await hold(10);
  await caption('Follow-ups preserve the previous query','“Sort by name” refines the California query rather than starting over. The state filter stays in place.');await send('Sort by name');await hold(12);await send('Only the first 10');await hold(8);
  await page.getByRole('button',{name:'New conversation'}).click();await caption('Employee hire-date example','The SQL generation specification defines an inclusive January 1, 2024 boundary. Execution returns only matching hire dates.');await send('Show all employees hired after January 2024');await hold(15);
  await page.getByRole('button',{name:'New conversation'}).click();await caption('Revenue through declared relationships','The simplified UI uses SQLite. Monthly 2025 revenue uses declared order/item relationships and historical line prices, excluding cancelled orders. Additional output dialects remain supported by the API.');await send('Monthly revenue for 2025');await hold(13);
  await page.getByRole('tab',{name:'Query plan',exact:true}).click();await caption('Real EXPLAIN, a relative work estimate','This is the actual SQLite sample plan, not a monetary cost or production latency prediction. Execution is independently capped and timed.');await hold(12);
  await page.getByRole('button',{name:'New conversation'}).click();await caption('Debugging diagnoses the original mistake','The supplied hiredate column does not exist. Debug mode explains the issue and returns a corrected, independently validated hire_date query.');await send('SELECT name, hiredate FROM employees','debug');await page.getByRole('tab',{name:'Explanation',exact:true}).click();await hold(12);
  await caption('Optimization applies only proven safe rewrites','This unused LEFT JOIN points to a unique customer primary key, so removing it preserves order rows. Unused joins to a many-side table are retained.');await send('SELECT o.id FROM orders o LEFT JOIN customers c ON o.customer_id = c.id','optimize');await page.getByRole('tab',{name:'Explanation',exact:true}).click();await hold(12);
  await caption('Scope and write guardrails','General knowledge is refused. Destructive SQL is refused before execution. A model proposal cannot bypass the independent AST validator or SQLite authorizer.');await send('Who won the FIFA World Cup?');await hold(8);await send('DELETE FROM customers');await hold(8);
  await page.getByRole('button',{name:'New conversation'}).click();await send('Show customers in California');await page.getByRole('switch',{name:'Dark mode',exact:true}).click();await caption('A complete local workbench','Dark mode, persistent conversation history, SQL highlighting, copy, SQL downloads and formula-safe CSV exports are included. PostgreSQL/MySQL output executes on SQLite sample data.');const sqlDownload=page.waitForEvent('download');await page.getByRole('button',{name:'Download SQL',exact:true}).click();await sqlDownload;const csvDownload=page.waitForEvent('download');await page.getByRole('button',{name:'Export CSV',exact:true}).click();await csvDownload;await hold(12);
  await caption('Spec-first delivery · local app complete','The repository includes detailed specs, exact prompts, architecture, tests and Docker/Vercel setup. GitHub and public Vercel publication are deferred at the user’s request.');await hold(13);
  const elapsed=(Date.now()-started)/1000;console.log(`Recording interactions finished after ${elapsed.toFixed(1)} seconds`);
  await writeFile('artifacts/demo-transcript.md','# QueryAtlas demo transcript\n\nMode: keyless sample, actual local API/database; captions only.\n\n'+transcript.join('\n')+`\nInteraction duration: ${elapsed.toFixed(1)} seconds.\n`);
  const video=page.video();await context.close();const source=await video.path();await video.saveAs('artifacts/queryatlas-demo.webm');
  if(path.dirname(path.resolve(source))===path.resolve('artifacts') && path.resolve(source)!==path.resolve('artifacts/queryatlas-demo.webm')) await unlink(source);
  console.log('Saved artifacts/queryatlas-demo.webm');
}finally{await browser.close();}
