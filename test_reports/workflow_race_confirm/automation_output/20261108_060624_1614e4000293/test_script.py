async def run_test(page, output_dir, page_url):
    try:
        await page.set_viewport_size({'width':1920,'height':800})
        await page.goto(page.url.rstrip('/')+'/simulator')
        await page.get_by_test_id('simulator-send').wait_for(state='visible')
        requests=[]
        page.on('request',lambda r:requests.append({'url':r.url,'body':r.post_data}) if '/charges/cancel' in r.url else None)
        async def delay(route):
            response=await route.fetch()
            await page.wait_for_timeout(1500)
            await route.fulfill(response=response)
        await page.route('**/api/charges/start',delay)
        await page.get_by_test_id('simulator-send').click(force=True)
        await page.wait_for_timeout(150)
        await page.get_by_test_id('nav-dashboard').click(force=True)
        await page.wait_for_timeout(2200)
        print('CANCEL_REQUESTS',requests)
        assert len(requests)==2 and '"id":null' in requests[0]['body'] and '"id":null' not in requests[1]['body']
        print('CONFIRMED null cancellation followed by valid cancellation; frontend race root cause')
        print('TEST_TOKEN',await page.evaluate("localStorage.getItem('meantime-demo-token')"))
    except Exception as e:
        print('FAIL race confirmation',str(e))
