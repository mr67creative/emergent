# Browser regression: interrupted/paused views, threshold edges, extension settings, destinations and assets.
async def run(page):
    import json
    base=page.url.split('/')[0]+'//'+page.url.split('/')[2]
    await page.set_viewport_size({'width':390,'height':844})
    failures=[]; responses=[]
    page.on('response',lambda r:responses.append((r.url,r.status)) if '/api/' in r.url else None)
    async def go(route):
        await page.goto(base+route); await page.locator('.page-container').wait_for(state='visible')
    async def click(id):
        await page.get_by_test_id(id).click(force=True); await page.wait_for_timeout(300)
    async def state():
        token=await page.evaluate("localStorage.getItem('meantime-demo-token')")
        r=await page.request.get(base+'/api/state',headers={'X-Demo-Token':token}); assert r.status==200
        return await r.json()
    def real(s):return [e for e in s['profile']['events'] if not e.get('sample')]
    async def send(id='simulator'):
        await page.get_by_test_id(id+'-prompt-input').fill('TEST_Explain APIs simply')
        async with page.expect_response(lambda r:'/api/charges/start' in r.url and r.request.method=='POST') as info:
            await click(id+'-send')
        return (await (await info.value).json())['id']
    try:
        await go('/simulator'); await click('response-speed-3')
        before=await state(); cid=await send(); await click('simulator-ad-dismiss')
        await page.get_by_test_id('simulator-response').wait_for(state='visible',timeout=6000)
        assert 'Ad dismissed' in await page.get_by_test_id('simulator-receipt').inner_text()
        after=await state(); assert after['profile']['balance_mills']==before['profile']['balance_mills'] and real(after)[-1]['status']=='dismissed'
        print('PASS dismissal continues AI response without payment')
        cid=await send()
        await page.evaluate("Object.defineProperty(document,'hidden',{configurable:true,get:()=>true});document.dispatchEvent(new Event('visibilitychange'))")
        await page.get_by_test_id('simulator-receipt').wait_for(state='visible')
        await page.evaluate("delete document.hidden;document.dispatchEvent(new Event('visibilitychange'))")
        await page.get_by_test_id('simulator-response').wait_for(state='visible',timeout=6000)
        assert next(e for e in real(await state()) if e['id']==cid)['status']=='window_blurred'
        print('PASS synthetic hidden-page signal cancels payment')
        cid=await send(); await click('mobile-nav-dashboard')
        await page.get_by_test_id('event-ledger').wait_for(state='visible'); await page.wait_for_timeout(500)
        assert next(e for e in real(await state()) if e['id']==cid)['status']=='navigation'
        print('PASS normal in-app navigation cancellation')
    except Exception as e: failures.append('interruptions: '+str(e)); print('FAIL interruptions',str(e))
    try:
        await go('/simulator')
        async def delayed(route):
            response=await route.fetch(); await page.wait_for_timeout(1500); await route.fulfill(response=response)
        await page.route('**/api/charges/start',delayed)
        prior=len(real(await state())); n=len(responses)
        await page.get_by_test_id('simulator-send').click(force=True)
        await page.wait_for_timeout(150)
        await click('mobile-nav-dashboard'); await page.wait_for_timeout(2500)
        await page.unroute('**/api/charges/start',delayed)
        print('DELAYED_START_RESPONSES',responses[n:])
        s=await state(); assert len(real(s))==prior+1 and real(s)[-1]['status']=='navigation'
        bad=[r for r in responses[n:] if r[1]>=400]
        if bad: failures.append('early navigation sends invalid cancellation: '+str(bad)); print('FAIL early navigation invalid cancellation',bad)
        else: print('PASS delayed start navigation cancellation')
    except Exception as e: failures.append('delayed navigation: '+str(e)); print('FAIL delayed navigation',str(e))
    try:
        await go('/extension'); await click('extension-power-switch')
        before=await state(); assert before['profile']['extension']['enabled'] is False
        await page.get_by_test_id('extension-chat-send').click(force=True)
        await page.get_by_test_id('extension-chat-response').wait_for(state='visible',timeout=9000)
        assert await page.get_by_test_id('extension-chat-ad-box').count()==0
        assert 'paused' in (await page.get_by_test_id('extension-chat-receipt').inner_text()).lower()
        after=await state(); assert len(real(after))==len(real(before)) and after['profile']['balance_mills']==before['profile']['balance_mills']
        print('PASS paused extension still answers, no ad, event or payout')
        await click('extension-power-switch'); await click('extension-mode-insights'); before=await state()
        cid=await send('extension-chat'); await page.get_by_test_id('extension-chat-insight').wait_for(state='visible')
        await page.get_by_test_id('extension-chat-response').wait_for(state='visible',timeout=9000)
        await page.get_by_test_id('extension-chat-receipt').wait_for(state='visible')
        after=await state(); assert after['profile']['balance_mills']==before['profile']['balance_mills'] and real(after)[-1]['status']=='insight'
        print('PASS insight response creates zero-money event')
        await click('extension-mode-ads'); await click('extension-placement-above_composer'); await click('extension-display-wait_time_only')
        await click('extension-settings-toggle'); await click('extension-platform-ChatGPT'); await page.reload()
        await page.get_by_test_id('extension-power-switch').wait_for()
        s=await state(); ext=s['profile']['extension']
        assert ext['placement']=='above_composer' and ext['display_mode']=='wait_time_only' and 'ChatGPT' not in ext['platforms']
        before=s; await page.get_by_test_id('extension-chat-send').click(force=True)
        await page.get_by_test_id('extension-chat-response').wait_for(state='visible',timeout=9000)
        assert await page.get_by_test_id('extension-chat-ad-box').count()==0 and len(real(await state()))==len(real(before))
        print('PASS site-excluded chat responds, settings persist')
    except Exception as e: failures.append('extension: '+str(e)); print('FAIL extension',str(e))
    try:
        await go('/payouts'); await click('payout-destination-settings')
        for key,value in [('label','TEST_My bank'),('holder','TEST_Alex'),('bank','TEST_Bank'),('last4','4242')]:
            await page.get_by_test_id('destination-'+key).fill(value)
        await click('save-destination'); await page.get_by_test_id('destination-settings').wait_for(state='hidden')
        await page.reload(); await click('payout-destination-settings')
        assert await page.get_by_test_id('destination-label').input_value()=='TEST_My bank' and await page.get_by_test_id('destination-last4').input_value()=='4242'
        popup=await page.get_by_test_id('destination-settings').bounding_box(); assert popup['x']>=0 and popup['x']+popup['width']<=390
        await page.keyboard.press('Escape'); await click('payout-method-demo-wallet'); await click('payout-destination-settings')
        await page.get_by_test_id('destination-label').fill('TEST_My wallet'); await page.get_by_test_id('destination-address').fill('TEST_wallet@example.org'); await click('save-destination')
        await page.reload(); await click('payout-destination-settings')
        assert await page.get_by_test_id('destination-address').input_value()=='TEST_wallet@example.org'
        await page.keyboard.press('Escape'); await click('payout-preset-0'); await click('request-payout-button'); await click('payout-confirm-button')
        await page.locator('[data-testid^="payout-record-"]').first.wait_for(state='visible')
        assert (await state())['profile']['transactions'][-1]['method']=='demo-wallet'
        await click('payout-method-demo-bank'); assert 'TEST_Bank' in await page.get_by_test_id('payout-method-demo-bank').inner_text()
        assert 'Digital wallet' in await page.locator('[data-testid^="payout-record-"]').first.inner_text()
        print('PASS bank/wallet editing persistence, mobile modal containment and safe payout history')
    except Exception as e: failures.append('payout: '+str(e)); print('FAIL payout',str(e))
    try:
        await go('/rewards'); assert await page.locator('[data-testid^="reward-node-"]').count()==4
        await click('desk-set-preview-button'); await page.get_by_test_id('reward-product-image').wait_for()
        await page.wait_for_function("document.querySelector('[data-testid=reward-product-image]').naturalWidth>0")
        assert 'Extended' in await page.get_by_test_id('reward-drawer-title').inner_text()
        await page.screenshot(path='/app/test_reports/workflow_edges/desk-mobile.jpg',quality=40,full_page=False)
        print('PASS four physical rewards, extended deskmat image loaded and locked')
    except Exception as e: failures.append('assets: '+str(e)); print('FAIL assets',str(e))
    print('EDGE_FAILURES',json.dumps(failures))
    print('TEST_TOKEN',await page.evaluate("localStorage.getItem('meantime-demo-token')"))
    error_text=await page.evaluate("""() => {const errorElements = Array.from(document.querySelectorAll('.error, [class*="error"], [id*="error"]'));return errorElements.map(el => el.textContent).join(', ');} """)
    print(f'Found error message: {error_text}' if error_text else 'No error messages found on the page')