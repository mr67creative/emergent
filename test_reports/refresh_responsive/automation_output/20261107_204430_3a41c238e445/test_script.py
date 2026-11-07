async def run_test(page, output_dir, page_url):
    import json
    try:
        await page.wait_for_selector('[data-testid="send-prompt-button"]', timeout=20000)
        token=await page.evaluate("localStorage.getItem('meantime-demo-token')")
        print('TEST_SESSION_TOKEN='+token)
        routes=['/','/dashboard','/insights','/rewards','/advertiser','/advertiser/analytics','/admin','/simulator','/payouts','/referrals','/extension']
        for width,height in [(1920,800),(390,844),(360,780)]:
            await page.set_viewport_size({'width':width,'height':height})
            for route in routes:
                await page.goto(page.url.split('/')[0]+'//'+page.url.split('/')[2]+route)
                await page.wait_for_selector('[data-testid="profile-menu-button"]')
                await page.wait_for_timeout(350)
                sizes=await page.evaluate("({width:innerWidth,scroll:document.documentElement.scrollWidth,broken:[...document.images].filter(i=>!i.complete||i.naturalWidth===0).map(i=>i.src),error:!!document.querySelector('[data-testid=connection-error]')})")
                print('ROUTE',width,route,json.dumps(sizes),'PASS' if sizes['scroll']<=width and not sizes['broken'] and not sizes['error'] else 'FAIL')
            if width==390:
                await page.screenshot(path='/app/test_reports/refresh_responsive/automation_output/20261107_204430_3a41c238e445/popup-mobile.jpeg', type="jpeg", quality=40, full_page=False)
        await page.set_viewport_size({'width':1920,'height':800})
        await page.goto(page.url.split('/')[0]+'//'+page.url.split('/')[2]+'/')
        await page.wait_for_selector('[data-testid="thunder-canvas"]')
        await page.wait_for_timeout(500)
        first=await page.evaluate("() => {const c=document.querySelector('[data-testid=thunder-canvas]');const d=c.getContext('2d').getImageData(0,0,c.width,c.height).data;let count=0,sum=0;for(let i=3;i<d.length;i+=4){if(d[i])count++;sum+=d[i];}return {count,sum};}")
        await page.wait_for_timeout(600)
        second=await page.evaluate("() => {const c=document.querySelector('[data-testid=thunder-canvas]');const d=c.getContext('2d').getImageData(0,0,c.width,c.height).data;let sum=0;for(let i=3;i<d.length;i+=4)sum+=d[i];return sum;}")
        print('CANVAS',first,second,'PASS' if first['count']>1000 and first['sum']!=second else 'FAIL')
        btn=page.get_by_test_id('send-prompt-button')
        before=await btn.bounding_box();await btn.hover();await page.wait_for_timeout(250);after=await btn.bounding_box()
        print('HOVER_NO_SHIFT',before==after)
        print('CSS_MOTION',await page.evaluate("[...document.querySelectorAll('*')].filter(e=>getComputedStyle(e).animationName!=='none'||getComputedStyle(e).transitionDuration!=='0s').length"))
        await page.screenshot(path='/app/test_reports/refresh_responsive/automation_output/20261107_204430_3a41c238e445/hero-desktop.jpeg', type="jpeg", quality=40, full_page=False)
        error_text=await page.evaluate("""() => {const errorElements = Array.from(document.querySelectorAll('.error, [class*="error"], [id*="error"]'));return errorElements.map(el => el.textContent).join(", ");}""")
        print(f'Found error message: {error_text}' if error_text else 'No error messages found on the page')
    except Exception as e:
        print('FAIL',str(e))
