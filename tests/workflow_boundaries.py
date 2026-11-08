# Browser regression: 2/15 second guarantees, unbilled studio preview, unload and analytics export integrity.
async def run(page):
    import json,uuid
    base=page.url.split('/')[0]+'//'+page.url.split('/')[2]
    await page.set_viewport_size({'width':360,'height':780})
    failures=[]
    async def go(route):
        await page.goto(base+route); await page.locator('.page-container').wait_for(state='visible')
    async def state():
        token=await page.evaluate("localStorage.getItem('meantime-demo-token')")
        r=await page.request.get(base+'/api/state',headers={'X-Demo-Token':token}); assert r.status==200
        return await r.json()
    async def put_campaign(cid,data):
        token=await page.evaluate("localStorage.getItem('meantime-demo-token')")
        r=await page.request.put(base+'/api/campaigns/'+cid,headers={'X-Demo-Token':token},data=data)
        assert r.status==200
    async def click(id):
        await page.get_by_test_id(id).click(force=True); await page.wait_for_timeout(200)
    async def send():
        await page.get_by_test_id('simulator-prompt-input').fill('TEST_boundary API question')
        async with page.expect_response(lambda r:'/api/charges/start' in r.url and r.request.method=='POST') as info:
            await click('simulator-send')
        return (await (await info.value).json())['id']
    def real(s):return [e for e in s['profile']['events'] if not e.get('sample')]
    cid='TEST_'+str(uuid.uuid4())
    data={'name':'TEST_Boundaries','variants':[{'headline':'TEST_variant '+str(i),'description':'TEST_description','cta':'TEST_Go'} for i in range(3)],'topics':['AI / ML'],'bid':.02,'budget':100,'url':'https://example.org','duration_seconds':2,'countries':[]}
    try:
        await go('/simulator'); await put_campaign(cid,data); await page.reload(); await page.get_by_test_id('simulator-campaign').select_option(cid); await click('response-speed-3')
        before=await state(); view_id=await send()
        await page.get_by_test_id('simulator-receipt').wait_for(state='visible',timeout=5000)
        assert await page.get_by_test_id('simulator-earned').inner_text()=='+$0.011'
        await page.get_by_test_id('simulator-response').wait_for(state='visible',timeout=4000)
        assert real(await state())[-1]['required_seconds']==2
        print('PASS 2-second UI threshold credits once')
        data['duration_seconds']=15; await put_campaign(cid,data); await page.reload(); await page.get_by_test_id('simulator-campaign').select_option(cid); await click('response-speed-3')
        before=await state(); view_id=await send()
        await page.get_by_test_id('simulator-response').wait_for(state='visible',timeout=6000)
        assert await page.get_by_test_id('simulator-ad-box').is_visible() and await page.get_by_test_id('simulator-receipt').count()==0
        await page.wait_for_timeout(7500)
        assert await page.get_by_test_id('simulator-ad-box').is_visible() and (await state())['profile']['balance_mills']==before['profile']['balance_mills']
        await page.get_by_test_id('simulator-receipt').wait_for(state='visible',timeout=7500)
        assert await page.get_by_test_id('simulator-earned').inner_text()=='+$0.011'
        assert next(e for e in real(await state()) if e['id']==view_id)['watched_seconds']==15
        print('PASS 15-second mobile guarantee, response arrives3s but payout waits15s')
    except Exception as e: failures.append('boundaries: '+str(e)); print('FAIL boundaries',str(e))
    try:
        await go('/advertiser'); before=await state(); await page.get_by_test_id('studio-chat-send').click(force=True)
        await page.get_by_test_id('studio-chat-response').wait_for(state='visible',timeout=9000)
        await page.get_by_test_id('studio-chat-receipt').wait_for(state='visible',timeout=18000)
        assert 'Not billed' in await page.get_by_test_id('studio-chat-receipt').inner_text()
        after=await state(); assert before['profile']['balance_mills']==after['profile']['balance_mills'] and len(real(before))==len(real(after))
        print('PASS studio animated preview never billed or added to event ledger')
    except Exception as e: failures.append('preview: '+str(e)); print('FAIL preview',str(e))
    try:
        await go('/simulator'); await click('response-speed-12'); before=await state(); view_id=await send()
        await page.get_by_test_id('simulator-ad-box').wait_for(state='visible'); await page.wait_for_timeout(300)
        await page.reload(); await page.get_by_test_id('simulator-workspace').wait_for(state='visible'); await page.wait_for_timeout(1000)
        after=await state(); matches=[e for e in real(after) if e['id']==view_id]
        if len(matches)!=1 or matches[0]['status'] not in ['navigation','window_blurred']:
            failures.append('Reload abandons active view without cancellation receipt')
            print('FAIL reload cancellation',view_id,'receipts',matches)
        else: print('PASS reload cancels and records receipt',matches)
        assert after['profile']['balance_mills']==before['profile']['balance_mills']
        token=await page.evaluate("localStorage.getItem('meantime-demo-token')")
        # Cleanup this abandoned test-owned view, by its exact returned ID only.
        await page.request.post(base+'/api/charges/cancel',headers={'X-Demo-Token':token},data={'id':view_id,'reason':'navigation'})
    except Exception as e: failures.append('reload: '+str(e)); print('FAIL reload',str(e))
    try:
        data['bid']=.04; await put_campaign(cid,data)
        await go('/advertiser/analytics?campaign='+cid)
        assert await page.get_by_test_id('ad-analytics-kpi-2').inner_text()=='$0.04'
        async with page.expect_download() as info: await click('export-analytics')
        download=await info.value; path='/app/test_reports/workflow_boundaries/changed-bid.csv'; await download.save_as(path)
        from pathlib import Path
        csv=Path(path).read_text(); print('CHANGED_BID_EXPORT',csv)
        # Both historical views cost .02 each, hence regional CPVV must remain .02.
        if '2,0,0.04' in csv:
            failures.append('Historical CSV CPVV uses current campaign bid .04 rather than recorded .02')
            print('FAIL historical CSV bid differs from recorded spend')
        else: print('PASS historical CSV bid integrity')
    except Exception as e: failures.append('CSV: '+str(e)); print('FAIL CSV',str(e))
    print('BOUNDARY_FAILURES',json.dumps(failures))
    print('TEST_TOKEN',await page.evaluate("localStorage.getItem('meantime-demo-token')"))
    error_text=await page.evaluate("""() => {const errorElements = Array.from(document.querySelectorAll('.error, [class*="error"], [id*="error"]'));return errorElements.map(el => el.textContent).join(', ');} """)
    print(f'Found error message: {error_text}' if error_text else 'No error messages found on the page')