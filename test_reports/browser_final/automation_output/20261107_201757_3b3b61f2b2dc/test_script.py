async def run_test(page, output_dir, page_url):
    base=page.url.rstrip('/')
    await page.set_viewport_size({'width':1920,'height':800})
    await page.evaluate("localStorage.setItem('meantime-demo-token','1PDBAvoIksPCuIFVfiwCpCa3cqV1aY4eCRgil1H3aeA')")
    async def state():
     return await page.evaluate("""async () => (await fetch('/api/state',{headers:{'X-Demo-Token':localStorage.getItem('meantime-demo-token')}})).json()""")
    try:
     await page.goto(base+'/admin')
     await page.wait_for_selector('[data-testid="review-brand"]')
     assert '6' in await page.get_by_test_id('review-queue-count').inner_text()
     await page.keyboard.press('ArrowRight')
     assert await page.get_by_test_id('review-brand').inner_text()=='PlanetScale'
     await page.keyboard.press('ArrowLeft')
     assert await page.get_by_test_id('review-brand').inner_text()=='Linear'
     await page.keyboard.press('j')
     await page.wait_for_timeout(400)
     assert await page.get_by_test_id('review-brand').inner_text()=='PlanetScale'
     assert '5' in await page.get_by_test_id('review-queue-count').inner_text()
     await page.get_by_test_id('review-filter-ad').click()
     assert '3' in await page.get_by_test_id('review-queue-count').inner_text()
     await page.keyboard.press('ArrowRight')
     assert await page.get_by_test_id('review-brand').inner_text()=='QuickYield'
     assert await page.get_by_test_id('approve-review-button').is_disabled()
     await page.keyboard.press('j')
     await page.wait_for_timeout(250)
     assert await page.get_by_test_id('review-brand').inner_text()=='QuickYield'
     await page.keyboard.press('k')
     await page.wait_for_timeout(400)
     assert await page.get_by_test_id('review-brand').inner_text()=='TEST_UI campaign'
     await page.keyboard.press('j')
     await page.wait_for_timeout(400)
     assert (await state())['campaigns'][0]['status']=='approved'
     await page.get_by_test_id('review-filter-insight').click()
     assert '2' in await page.get_by_test_id('review-queue-count').inner_text()
     await page.keyboard.press('ArrowRight')
     assert await page.get_by_test_id('review-brand').inner_text()=='Your brand'
     await page.keyboard.press('j')
     await page.wait_for_timeout(400)
     assert (await state())['submissions'][0]['status']=='approved'
     await page.keyboard.press('k')
     await page.wait_for_timeout(400)
     assert await page.get_by_test_id('review-empty').is_visible()
     await page.get_by_test_id('review-filter-all').click()
     await page.keyboard.press('k')
     await page.wait_for_timeout(400)
     assert await page.get_by_test_id('review-empty').is_visible()
     await page.keyboard.press('ArrowRight')
     await page.keyboard.press('ArrowLeft')
     await page.keyboard.press('j')
     print('PASS admin shortcuts, filters/count, correct next item, risk block and empty queue')
     sid=(await state())['submissions'][0]['id']
     await page.goto(base+'/insights')
     await page.wait_for_selector('[data-testid="insight-card-'+sid+'"]')
     print('PASS approved organic contribution published in Explore')
     await page.goto(base+'/advertiser')
     await page.wait_for_selector('[data-testid="campaign-status"]')
     assert await page.get_by_test_id('campaign-status').inner_text()=='APPROVED'
     page.once('dialog', lambda dialog: dialog.accept())
     await page.get_by_test_id('delete-campaign-button').click()
     await page.wait_for_timeout(500)
     assert (await state())['campaigns']==[]
     print('PASS studio reviewed status and native-confirm deletion')
    except Exception as e: print('FAIL moderation',repr(e))
    try:
     await page.goto(base+'/advertiser/analytics')
     await page.wait_for_selector('[data-testid="ad-analytics-kpi-0"]')
     initial=await page.get_by_test_id('ad-analytics-kpi-0').inner_text()
     viewbox=await page.locator('[data-testid="ad-world-map"] > svg').get_attribute('viewBox')
     await page.get_by_test_id('ad-world-country-United-States').click()
     assert await page.get_by_test_id('ad-analytics-kpi-0').inner_text()!=initial
     assert await page.locator('[data-testid="ad-world-map"] > svg').get_attribute('viewBox')!=viewbox
     region=await page.get_by_test_id('ad-analytics-kpi-0').inner_text()
     await page.get_by_test_id('advertiser-period').select_option('30')
     assert int((await page.get_by_test_id('ad-analytics-kpi-0').inner_text()).replace(',',''))==4*int(region.replace(',',''))
     async with page.expect_download() as info:
      await page.get_by_test_id('export-analytics').click()
     download=await info.value
     await download.save_as('/app/test_reports/browser_final/analytics.csv')
     assert download.suggested_filename=='meantime-sample-analytics.csv'
     print('PASS map filter zoom KPI, period and CSV download')
     await page.get_by_test_id('reset-region').click()
     assert await page.locator('[data-testid="ad-world-map"] > svg').get_attribute('viewBox')==viewbox
     for variant in ['A','B','C']:
      assert await page.get_by_test_id('variant-comparison-'+variant).is_visible()
     print('PASS map reset and confidence comparisons')
    except Exception as e: print('FAIL analytics',repr(e))
    routes=['/','/dashboard','/insights','/rewards','/advertiser','/advertiser/analytics','/admin','/simulator']
    for width,height in [(1920,800),(390,844),(360,780)]:
     await page.set_viewport_size({'width':width,'height':height})
     for route in routes:
      try:
       await page.goto(base+route)
       await page.wait_for_timeout(650)
       assert await page.get_by_test_id('connection-error').count()==0
       assert await page.get_by_test_id('app-loading').count()==0
       measurements=await page.evaluate("""() => ({width:innerWidth, scroll:document.documentElement.scrollWidth, offenders:[...document.querySelectorAll('main button,main input,main article,main h1,main h2,main .kpi-value, main .journey-node-label')].filter(e=>{let r=e.getBoundingClientRect();return r.width>0 && (r.right>innerWidth+1||r.left< -1)}).map(e=>({testid:e.dataset.testid, text:e.textContent.slice(0,60),left:e.getBoundingClientRect().left,right:e.getBoundingClientRect().right})), brokenImages:[...document.images].filter(e=>e.complete&&!e.naturalWidth).map(e=>e.src)})""")
       print('RESPONSIVE',width,route,measurements)
       if width==390 and route in ['/dashboard','/advertiser','/rewards']:
        await page.screenshot(path='/app/test_reports/browser_final/automation_output/20261107_201757_3b3b61f2b2dc/mobile-.jpeg'+route.strip('/.jpeg', type="jpeg", quality=40)+'.jpeg', quality=40, full_page=False)
       if width==360 and route=='/dashboard':
        print('KPI CLIPPING',await page.locator('.kpi-value').evaluate_all("els=>els.map(e=>({text:e.textContent,width:e.getBoundingClientRect().width,scroll:e.scrollWidth,parent:e.parentElement.getBoundingClientRect().width}))"))
      except Exception as e: print('FAIL responsive',width,route,repr(e))
    error_text=await page.evaluate("""() => {const errorElements = Array.from(document.querySelectorAll('.error, [class*="error"], [id*="error"]'));return errorElements.map(el=>el.textContent).join(', ');} """)
    print('Found error message: '+error_text if error_text else 'No error messages found on the page')
