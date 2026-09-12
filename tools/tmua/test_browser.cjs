// Run against a local static server. Needs Playwright and an installed Chrome.
// All GitHub requests in the editor test are intercepted; nothing is published.
const {chromium} = require('playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const base = process.env.TMUA_BASE_URL || 'http://127.0.0.1:8765';
const db = JSON.parse(fs.readFileSync(path.join(__dirname, '../../tmua/data/questions.json'), 'utf8'));
const overrides = JSON.parse(fs.readFileSync(path.join(__dirname, '../../tmua/data/overrides.json'), 'utf8'));
const shots = process.env.TMUA_SCREENSHOTS;

(async () => {
  const browser = await chromium.launch({channel: 'chrome', headless: true});
  try {
    const context = await browser.newContext({viewport: {width: 1440, height: 1000}});
    // External fonts/KaTeX are optional; make the checks deterministic offline.
    await context.route(/https:\/\/(?:cdnjs|fonts)\./, route => route.abort());
    const page = await context.newPage();
    const errors = [];
    page.on('pageerror', e => errors.push(e.message));
    async function ready() {
      await page.waitForFunction(() => document.querySelector('#count b'));
    }
    async function count(n) {
      await page.waitForFunction(n => document.querySelector('#count b')?.textContent === String(n), n);
    }
    await page.goto(base+'/tmua-database.html'); await ready(); await count(360);
    assert.deepEqual(await page.locator('.qcard').evaluateAll(es => es.slice(0,12).map(e=>e.id)),
      Array.from({length:12},(_,i)=>`2023-p1-Q${i+1}`));
    assert.equal(await page.locator('.sidebar a.active').textContent(), '▸ TMUA Database');
    assert.equal(await page.locator('.qcard').count(), 30);
    await page.locator('#more').click(); assert.equal(await page.locator('.qcard').count(),60);
    await page.locator('#f-number button').filter({hasText:'Paper 2'}).click(); await count(180);
    await page.locator('details.more').filter({hasText:'Filter by year'}).locator('summary').click();
    await page.locator('#f-year button').filter({hasText:/^2023$/}).click(); await count(20);
    await page.locator('details.more').filter({hasText:'Filter by topic'}).locator('summary').click();
    await page.locator('#f-topic button').filter({hasText:/^Logic & proof$/}).click();
    const expected = db.questions.filter(q=>q.paper==='2023-p2' && q.topics.includes('logic')).length;
    await count(expected);
    const url = page.url(); await page.reload(); await ready(); await count(expected);
    assert.equal(page.url(),url);
    await page.locator('#reset').click(); await count(360);
    await page.locator('#q').fill('triangle building'); await count(0);
    await page.locator('#q').fill('2023-p1 Q13'); await count(1);
    assert.equal(await page.locator('.qcard').getAttribute('id'),'2023-p1-Q13');
    await page.locator('.solution summary').click();
    assert.equal(await page.locator('.answer').textContent(),'Correct answer: F');
    assert.equal(await page.getByRole('link',{name:/Enlarge question/}).getAttribute('href'),'tmua/img/2023-p1/Q13.png');
    assert.equal(await page.getByRole('link',{name:/Enlarge solution/}).getAttribute('href'),'tmua/img/2023-p1/sol-Q13.png');
    await page.waitForFunction(() => Array.from(document.querySelectorAll('.qimg')).every(i=>i.complete && i.naturalWidth>0));
    await page.locator('#expandall').click();
    assert.equal(await page.locator('.solution').getAttribute('open'),'');
    await page.locator('#expandall').click();
    assert.equal(await page.locator('.solution').getAttribute('open'),null);
    await page.goto(base+'/tmua-database.html#specimen-p2-Q20'); await ready();
    await page.waitForFunction(()=>document.querySelector('#specimen-p2-Q20'));
    assert.ok(page.url().endsWith('#specimen-p2-Q20'));
    await page.goto(base+'/tmua-database.html#q=%ZZ'); await ready(); await count(360);
    await page.locator('#q').fill('2016-p1 expansion');
    await count(db.questions.filter(q=>q.paper==='2016-p1' && (q.text+' '+q.stext).toLowerCase().includes('expansion')).length);
    assert.ok(await page.locator('[id="2016-p1-Q1"]').count());
    await page.goto(base+'/tmua-database.html'); await ready();
    if (shots) {
      fs.mkdirSync(shots,{recursive:true});
      await page.screenshot({path:path.join(shots,'tmua-desktop.png')});
    }
    await page.setViewportSize({width:390,height:844});
    assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
    await page.locator('#q').fill('2023-p1 Q13'); await count(1);
    await page.locator('.solution summary').click();
    await page.waitForFunction(() => Array.from(document.querySelectorAll('.qimg')).every(i=>i.complete && i.naturalWidth>0));
    if (shots) await page.screenshot({path:path.join(shots,'tmua-mobile.png'),fullPage:true});

    // Use a fixture password only in this intercepted response. Production digest stays intact.
    await page.route('**/tmua-database.html', async route => {
      const response = await route.fetch();
      const body = (await response.text()).replace(/PW_DIGEST = \d+/, 'PW_DIGEST = cyrb53("test-only", PW_SEED)');
      await route.fulfill({response,body});
    });
    let writes=0;
    await page.route('https://api.github.com/**', async route => {
      assert.ok(route.request().url().includes('/contents/tmua/data/overrides.json'));
      if (route.request().method()==='GET') {
        await route.fulfill({json:{sha:'fixture-sha',content:Buffer.from(JSON.stringify(overrides)).toString('base64')}});
      } else {
        const body=route.request().postDataJSON();
        assert.equal(body.branch,'main'); assert.equal(body.sha,'fixture-sha');
        const updated=JSON.parse(Buffer.from(body.content,'base64').toString('utf8'));
        assert.equal(Object.keys(updated).length,360);
        assert.ok(updated['2023-p1-Q1'].includes('logic'));
        writes++;
        await route.fulfill({json:{commit:{html_url:'https://github.com/example/fixture'}}});
      }
    });
    await page.goto(base+'/tmua-database.html'); await ready();
    await page.evaluate(()=>localStorage.setItem('mat-tag-edits',JSON.stringify({'2025-Q1':['circles']})));
    await page.locator('#editorbtn').click();
    await page.locator('#pw').fill('wrong'); await page.locator('#unlock').click();
    assert.match(await page.locator('#gatenote').textContent(),/not correct/);
    await page.locator('#pw').fill('test-only'); await page.locator('#unlock').click();
    await page.locator('[id="2023-p1-Q1"] [data-act=edit]').click();
    await page.locator('[id="2023-p1-Q1"] [data-act=auto]').click();
    assert.equal(await page.locator('[id="2023-p1-Q1"] [data-topic=algebra]').getAttribute('aria-pressed'),'false');
    await page.locator('[id="2023-p1-Q1"] [data-act=revert]').click();
    assert.equal(await page.locator('[id="2023-p1-Q1"] [data-topic=algebra]').getAttribute('aria-pressed'),'true');
    await page.locator('[id="2023-p1-Q1"] [data-topic=logic]').click();
    assert.equal(JSON.parse(await page.evaluate(()=>localStorage.getItem('tmua-tag-edits')))['2023-p1-Q1'].includes('logic'),true);
    assert.deepEqual(JSON.parse(await page.evaluate(()=>localStorage.getItem('mat-tag-edits'))),{'2025-Q1':['circles']});
    const downloadPromise=page.waitForEvent('download');
    await page.locator('#download').click(); const download=await downloadPromise;
    const exported=JSON.parse(fs.readFileSync(await download.path(),'utf8'));
    assert.equal(Object.keys(exported).length,360);
    assert.ok(exported['2023-p1-Q1'].includes('logic'));
    page.on('dialog', async dialog => {
      if (dialog.type()==='prompt') await dialog.accept('fixture-token'); else await dialog.dismiss();
    });
    await page.locator('#publish').click();
    await page.waitForFunction(()=>document.querySelector('#editnote').textContent.startsWith('Published.'));
    assert.equal(writes,1);
    assert.deepEqual(errors,[]);
    await page.goto(base+'/mat-database.html');
    await page.waitForFunction(()=>document.querySelector('#count b')?.textContent==='349');
    assert.equal(await page.locator('h1').textContent(),'MAT Questions Database');
    console.log('PASS: desktop/mobile, 360 records, numeric order, pagination, combined filters, URL reload, old-PDF search, permalink, images, solutions, tag editor/export and mocked GitHub publish; MAT still has 349 questions');
  } finally { await browser.close(); }
})().catch(e=>{console.error(e);process.exitCode=1});
