# Reusable MeanTime route, canvas, image and mobile overflow checks (async Playwright).
async def run(page):
    import json
    base = page.url.split('/')[0] + '//' + page.url.split('/')[2]
    routes = ['/', '/dashboard', '/insights', '/rewards', '/advertiser', '/advertiser/analytics', '/admin', '/simulator', '/payouts', '/referrals', '/extension']
    try:
        for width, height in [(1920, 800), (390, 844), (360, 780)]:
            await page.set_viewport_size({'width': width, 'height': height})
            for route in routes:
                await page.goto(base + route)
                await page.wait_for_selector('[data-testid="profile-menu-button"]')
                await page.wait_for_function("!document.querySelector('[data-testid=app-loading]') && !document.querySelector('[data-testid=connection-error]')")
                await page.wait_for_function('[...document.images].every(i=>i.complete)', timeout=10000)
                info = await page.evaluate("({width:innerWidth,scroll:document.documentElement.scrollWidth,broken:[...document.images].filter(i=>i.naturalWidth===0).map(i=>i.src)})")
                print('ROUTE', width, route, json.dumps(info), 'PASS' if info['scroll'] <= width and not info['broken'] else 'FAIL')
        error_text = await page.evaluate('''() => {const errorElements = Array.from(document.querySelectorAll('.error, [class*="error"], [id*="error"]')); return errorElements.map(el => el.textContent).join(", ");}''')
        print(f'Found error message: {error_text}' if error_text else 'No error messages found on the page')
    except Exception as exc:
        print('FAIL', repr(exc))