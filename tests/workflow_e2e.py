# Browser regression: studio editing -> persisted manual campaign -> chat -> analytics and ledger.
async def run(page):
    import json
    from pathlib import Path
    base=page.url.split('/')[0]+'//'+page.url.split('/')[2]
    await page.set_viewport_size({'width':1920,'height':800})
    failures=[]
    async def go(route):
        await page.goto(base+route)
        await page.locator('.page-container').wait_for(state='visible')
    async def state():
        token=await page.evaluate("localStorage.getItem('meantime-demo-token')")
        r=await page.request.get(base+'/api/state',headers={'X-Demo-Token':token})
        assert r.status==200
        return await r.json()
    async def click(id):
        await page.get_by_test_id(id).click(force=True)
        await page.wait_for_timeout(350)
    async def flow(prompt='TEST_Explain APIs simply'):
        await page.get_by_test_id('simulator-prompt-input').fill(prompt)
        async with page.expect_response(lambda r:'/api/charges/start' in r.url and r.request.method=='POST') as info:
            await click('simulator-send')
        return (await (await info.value).json())['id']
    def real(s): return [e for e in s['profile']['events'] if not e.get('sample')]
    try:
        await go('/advertiser')
        await page.get_by_test_id('campaign-name').fill('TEST_Workflow_UI_8s')
        ad=await page.get_by_test_id('composer-ad-box').bounding_box()
        thinking=await page.get_by_test_id('studio-chat-thinking').bounding_box()
        assert ad['y']+ad['height']<thinking['y']
        print('PASS studio ad above thinking')
        await click('editor-mode-form')
        for key,value in [('headline','TEST_Canvas headline'),('description','TEST_Canvas description'),('cta','TEST_Canvas CTA')]:
            await page.get_by_test_id('composer-ad-'+key+'-input').fill(value)
            assert await page.get_by_test_id('visual-'+key).input_value()==value
            await page.get_by_test_id('visual-'+key).fill('TEST_Form '+key)
            assert await page.get_by_test_id('composer-ad-'+key+'-input').input_value()=='TEST_Form '+key
        await click('variant-B'); await page.get_by_test_id('visual-headline').fill('TEST_Variant B')
        await click('variant-C'); await page.get_by_test_id('visual-headline').fill('TEST_Variant C')
        await click('variant-A'); assert await page.get_by_test_id('visual-headline').input_value()=='TEST_Form headline'
        print('PASS reciprocal edits all fields, separate variants')
        await click('advanced-options-toggle')
        slider=page.get_by_test_id('campaign-duration-slider')
        assert await slider.get_attribute('min')=='2' and await slider.get_attribute('max')=='15'
        for duration in [2,15,8]:
            await slider.fill(str(duration)); assert await page.get_by_test_id('campaign-duration-value').inner_text()==str(duration)+'s'
        await page.get_by_test_id('country-search').fill('India'); await click('target-country-India')
        await page.get_by_test_id('country-search').fill('France'); await click('target-country-France')
        async with page.expect_response(lambda r:'/api/campaigns/' in r.url and r.request.method=='PUT'):
            await click('save-campaign-button')
        s=await state(); c=next(c for c in s['campaigns'] if c['name']=='TEST_Workflow_UI_8s'); cid=c['id']
        assert c['duration_seconds']==8 and set(c['countries'])=={'India','France'}
        assert [v['headline'] for v in c['variants']]==['TEST_Form headline','TEST_Variant B','TEST_Variant C']
        await page.reload(); await page.get_by_test_id('composer-ad-headline-input').wait_for()
        assert await page.get_by_test_id('composer-ad-headline-input').input_value()=='TEST_Form headline'
        print('PASS studio persisted duration, geography and variants',cid)
        await go('/advertiser/analytics?campaign='+cid)
        assert await page.get_by_test_id('ad-analytics-kpi-0').inner_text()=='0'
        assert await page.get_by_test_id('ad-analytics-kpi-2').inner_text()=='$0.00'
        assert await page.get_by_test_id('campaign-analytics-empty').is_visible()
        assert await page.locator('[data-testid^="ad-spark-"]').count()==0
        print('PASS empty campaign zero analytics')
        await go('/simulator'); await page.get_by_test_id('simulator-campaign').select_option(cid)
        await page.get_by_test_id('simulator-variant').select_option('1')
        await page.get_by_test_id('simulator-platform').select_option('Claude')
        await click('response-speed-3'); await click('lab-display-wait_time_only')
        before=await state(); view_id=await flow()
        await page.get_by_test_id('simulator-ad-box').wait_for(state='visible')
        assert await page.get_by_test_id('simulator-ad-headline').inner_text()=='TEST_Variant B'
        ad=await page.get_by_test_id('simulator-ad-box').bounding_box(); prompt=await page.get_by_test_id('simulator-sent-prompt').bounding_box(); thinking=await page.get_by_test_id('simulator-thinking').bounding_box()
        assert prompt['y']+prompt['height']<ad['y'] and ad['y']+ad['height']<thinking['y']
        await page.get_by_test_id('simulator-response').wait_for(state='visible',timeout=6000)
        await page.get_by_test_id('simulator-receipt').wait_for(state='visible')
        assert await page.get_by_test_id('simulator-earned').inner_text()=='$0.000'
        after=await state(); e=next(e for e in real(after) if e['id']==view_id)
        assert e['status']=='below_threshold' and e['watched_seconds']==3 and e['required_seconds']==8 and after['profile']['balance_mills']==before['profile']['balance_mills']
        assert await page.get_by_test_id('simulator-prompt-input').input_value()==''
        print('PASS wait-only 3s response no payout, under-prompt placement')
        await click('lab-display-persist_until_5s'); await click('lab-placement-above_composer')
        before=await state(); view_id=await flow('TEST_Why do LLMs need a cache?')
        await page.get_by_test_id('simulator-response').wait_for(state='visible',timeout=6000)
        assert await page.get_by_test_id('simulator-ad-box').is_visible()
        assert await page.get_by_test_id('simulator-receipt').count()==0
        assert (await state())['profile']['balance_mills']==before['profile']['balance_mills']
        assert await page.get_by_test_id('simulator-above-composer-slot').get_by_test_id('simulator-ad-box').count()==1
        ad=await page.get_by_test_id('simulator-ad-box').bounding_box(); composer=await page.get_by_test_id('simulator-prompt-input').bounding_box()
        assert ad['y']+ad['height']<composer['y']
        await click('simulator-ad-cta-button')
        await page.get_by_test_id('simulator-receipt').wait_for(state='visible',timeout=9000)
        assert await page.get_by_test_id('simulator-earned').inner_text()=='+$0.011'
        after=await state(); e=next(e for e in real(after) if e['id']==view_id)
        assert e['status']=='credited' and e['clicked'] and e['platform']=='Claude' and e['variant']=='B'
        assert after['profile']['balance_mills']==before['profile']['balance_mills']+11 and after['profile']['views']==before['profile']['views']+1
        await page.wait_for_timeout(1000); assert len([e for e in real(await state()) if e['id']==view_id])==1
        print('PASS guaranteed ad stays after AI response then pays once at8s; above-composer placement and click')
        await go('/advertiser/analytics?campaign='+cid)
        assert await page.get_by_test_id('ad-analytics-kpi-0').inner_text()=='1'
        assert await page.get_by_test_id('ad-analytics-kpi-2').inner_text()=='$0.02'
        assert await page.get_by_test_id('ad-analytics-kpi-3').inner_text()=='50.0%'
        assert '2 views' in await page.get_by_test_id('variant-comparison-B').inner_text()
        async with page.expect_download() as info: await click('export-analytics')
        download=await info.value; await download.save_as('/app/test_reports/workflow_e2e/campaign.csv')
        print('PASS campaign-specific recorded analytics and CSV')
        await page.get_by_test_id('ad-world-region-select').select_option('India'); await page.wait_for_timeout(250)
        assert await page.get_by_test_id('ad-analytics-kpi-0').inner_text()=='0'
        dim=await page.locator('circle[data-country="France"]').first.get_attribute('opacity')
        assert dim=='0.075' and await page.locator('circle[data-country="India"]').first.get_attribute('data-dimmed')=='false'
        print('PASS selected region filters metrics and dims other countries')
        await click('ad-world-reset'); await page.get_by_test_id('analytics-campaign-select').select_option('example')
        assert await page.get_by_test_id('ad-analytics-kpi-2').inner_text()=='$3014.80'
        await page.get_by_test_id('advertiser-period').select_option('30')
        assert await page.get_by_test_id('ad-analytics-kpi-2').inner_text()=='$12059.21'
        print('PASS previous weighted example spend bug fixed')
        await go('/dashboard')
        assert await page.get_by_test_id('ledger-real-events').inner_text()=='2'
        assert await page.get_by_test_id('ledger-total-earned').inner_text()=='$0.011'
        await click('ledger-expand-'+view_id)
        text=await page.get_by_test_id('ledger-detail-'+view_id).inner_text()
        assert '8s' in text and 'Variant B' in text and 'United States of America' in text
        for filter in ['paid','unpaid','insights','rotated','all']: await click('ledger-filter-'+filter)
        async with page.expect_download() as info: await click('export-ledger')
        await (await info.value).save_as('/app/test_reports/workflow_e2e/ledger.csv')
        print('PASS event ledger totals, receipts, filters and export')
    except Exception as e:
        failures.append(str(e)); print('FAIL workflow',str(e))
        await page.screenshot(path='/app/test_reports/workflow_e2e/failure.jpg',quality=40,full_page=False)
    print('WORKFLOW_FAILURES',json.dumps(failures))
    print('TEST_TOKEN',await page.evaluate("localStorage.getItem('meantime-demo-token')"))
    error_text=await page.evaluate("""() => {const errorElements = Array.from(document.querySelectorAll('.error, [class*="error"], [id*="error"]'));return errorElements.map(el => el.textContent).join(', ');} """)
    print(f'Found error message: {error_text}' if error_text else 'No error messages found on the page')