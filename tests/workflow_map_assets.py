# Browser regression: inactive map pixels stay inspectable, geographic filtering and hero motion/assets.
async def run(page):
    import json
    base=page.url.split('/')[0]+'//'+page.url.split('/')[2]
    try:
        await page.set_viewport_size({'width':1920,'height':800})
        await page.goto(base+'/advertiser/analytics'); await page.get_by_test_id('ad-world-map').wait_for()
        await page.get_by_test_id('analytics-campaign-select').select_option('all')
        await page.get_by_test_id('ad-world-region-select').select_option('France')
        await page.get_by_test_id('ad-world-viewport').scroll_into_view_if_needed()
        await page.wait_for_timeout(300)
        vp=await page.get_by_test_id('ad-world-viewport').bounding_box()
        pixels=page.locator('circle[data-country="France"]')
        chosen=None
        for i in range(await pixels.count()):
            box=await pixels.nth(i).bounding_box()
            if box and box['x']>vp['x']+5 and box['x']<vp['x']+vp['width']-5 and box['y']>vp['y']+5 and box['y']<vp['y']+vp['height']-5:
                chosen=await pixels.nth(i).get_attribute('data-testid');break
        assert chosen
        await page.get_by_test_id(chosen).hover(force=True)
        text=await page.get_by_test_id('ad-world-tooltip').inner_text()
        assert 'France' in text and 'Country views\n0' in text and 'COUNTRY-LEVEL SIMULATION' in text
        print('PASS inactive/no-pin pixel hover shows real country zero counts',chosen)
        await page.get_by_test_id('ad-world-zoom-in').click(force=True)
        assert await page.get_by_test_id('ad-world-zoom-level').inner_text()=='350%'
        await page.get_by_test_id('ad-world-reset').click(force=True)
        assert await page.get_by_test_id('ad-world-zoom-level').inner_text()=='100%'
        print('PASS map zoom and reset')
    except Exception as e:print('FAIL map',str(e))
    try:
        await page.goto(base);await page.get_by_test_id('thunder-canvas').wait_for()
        broken=await page.evaluate("Array.from(document.images).filter(i=>i.complete&&i.naturalWidth===0).map(i=>i.src)")
        assert not broken,broken
        waves=await page.get_by_test_id('thunder-canvas').bounding_box();cta=await page.get_by_test_id('hero-start-earning').bounding_box()
        assert waves['y']<=cta['y']+cta['height']<=waves['y']+waves['height']
        animations=await page.evaluate("document.getAnimations().filter(a=>a.constructor.name==='CSSAnimation'||a.constructor.name==='CSSTransition').length")
        assert animations==0
        print('PASS single-bolt brand image loaded, wave spans CTA height, CSS motion disabled')
        print('TEST_TOKEN',await page.evaluate("localStorage.getItem('meantime-demo-token')"))
        error_text=await page.evaluate("""() => {const errorElements = Array.from(document.querySelectorAll('.error, [class*="error"], [id*="error"]'));return errorElements.map(el => el.textContent).join(', ');} """)
        print(f'Found error message: {error_text}' if error_text else 'No error messages found on the page')
    except Exception as e:print('FAIL hero assets/motion',str(e))