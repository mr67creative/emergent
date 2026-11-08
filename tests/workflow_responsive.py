# Browser regression: all eleven routes, narrow-screen overflow and hero popover containment.
async def run(page):
    import json
    base=page.url.split('/')[0]+'//'+page.url.split('/')[2]
    routes=['/','/dashboard','/insights','/rewards','/advertiser','/advertiser/analytics','/admin','/simulator','/payouts','/referrals','/extension']
    failures=[]
    for width,height in [(1920,800),(390,844),(360,780)]:
        await page.set_viewport_size({'width':width,'height':height})
        for route in routes:
            try:
                await page.goto(base+route)
                await page.locator('[data-testid="app-loading"]').wait_for(state='hidden',timeout=15000)
                await page.locator('[data-testid="hero-workspace"]' if route=='/' else '.page-container').wait_for(state='visible')
                await page.wait_for_timeout(250)
                dims=await page.evaluate('({width:document.documentElement.clientWidth,scroll:document.documentElement.scrollWidth})')
                assert dims['scroll']<=width+1, str(dims)
                assert await page.get_by_test_id('connection-error').count()==0
                print('PASS route',width,route,dims)
                if route=='/':
                    await page.get_by_test_id('hero-extension-toggle').click(force=True)
                    popup=await page.get_by_test_id('hero-extension-popup').bounding_box()
                    assert popup['x']>=0 and popup['x']+popup['width']<=width+1
                    await page.get_by_test_id('hero-popup-display-wait_time_only').click(force=True)
                    assert 'selected' in (await page.get_by_test_id('hero-popup-display-wait_time_only').get_attribute('class'))
                    if width==360: await page.screenshot(path='/app/test_reports/workflow_responsive/hero-popup-360.jpg',quality=40,full_page=False)
                    await page.get_by_test_id('hero-extension-close').click(force=True)
                    print('PASS hero popup',width)
            except Exception as e:
                failures.append({'route':route,'width':width,'error':str(e)})
                print('FAIL route',width,route,str(e))
    print('RESPONSIVE_FAILURES',json.dumps(failures))
    print('TEST_TOKEN',await page.evaluate("localStorage.getItem('meantime-demo-token')"))
    error_text=await page.evaluate("""() => {const errorElements = Array.from(document.querySelectorAll('.error, [class*="error"], [id*="error"]'));return errorElements.map(el => el.textContent).join(', ');} """)
    print(f'Found error message: {error_text}' if error_text else 'No error messages found on the page')