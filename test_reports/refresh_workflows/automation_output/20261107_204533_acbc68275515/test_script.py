async def run_test(page, output_dir, page_url):
    import json
    base=page.url.split('/')[0]+'//'+page.url.split('/')[2]
    await page.evaluate("localStorage.setItem('meantime-demo-token','I6wKwR2HzXjJXUBCDpi23TY8yadrjXAwRb1Yoa0MGy8')")
    await page.set_viewport_size({'width':1920,'height':800})
    try:
        await page.goto(base+'/payouts')
        await page.get_by_test_id('payout-method-demo-wallet').click(force=True)
        await page.wait_for_timeout(400)
        await page.reload()
        assert 'selected' in await page.get_by_test_id('payout-method-demo-wallet').get_attribute('class')
        for value in ['4.99','20']:
            await page.get_by_test_id('payout-amount-input').fill(value)
            assert await page.get_by_test_id('request-payout-button').is_disabled()
        await page.get_by_test_id('payout-preset-0').click(force=True)
        await page.get_by_test_id('request-payout-button').click(force=True)
        assert await page.get_by_test_id('payout-confirm-amount').inner_text()=='$5.000'
        await page.get_by_test_id('payout-cancel').click(force=True)
        assert await page.get_by_test_id('payout-available-balance').inner_text()=='$14.850'
        await page.get_by_test_id('request-payout-button').click(force=True)
        await page.get_by_test_id('payout-confirm-button').click(force=True)
        await page.wait_for_timeout(600)
        assert await page.get_by_test_id('payout-available-balance').inner_text()=='$9.850'
        async with page.expect_download() as download_info:
            await page.get_by_test_id('export-payouts').click(force=True)
        download=await download_info.value
        await download.save_as('/app/test_reports/refresh_workflows/payouts.csv')
        print('PASS payout validation/cancel/partial/destination persistence/history/CSV')
        await page.get_by_test_id('payout-preset-2').click(force=True)
        await page.get_by_test_id('request-payout-button').click(force=True)
        await page.get_by_test_id('payout-confirm-button').click(force=True)
        await page.wait_for_timeout(500)
        assert await page.get_by_test_id('payout-available-balance').inner_text()=='$0.000'
        assert await page.get_by_test_id('payout-total-withdrawn').inner_text()=='$14.85'
        print('PASS all-available payout and total')
        await page.goto(base+'/simulator')
        assert await page.get_by_test_id('charge-vault-total').inner_text()=='$0.000'
        print('PASS prior zero-balance defect regression')
        await page.goto(base+'/referrals')
        link=await page.get_by_test_id('referral-link').input_value()
        assert link.startswith(base+'/?ref=MT-')
        await page.get_by_test_id('copy-referral-link').click(force=True)
        await page.wait_for_timeout(300)
        print('COPY_FEEDBACK',await page.locator('[data-sonner-toast]').all_text_contents())
        await page.get_by_test_id('referral-claim-ref-maya').click(force=True)
        await page.wait_for_timeout(500)
        assert await page.get_by_test_id('referral-claimed-ref-maya').is_disabled()
        assert await page.get_by_test_id('referrals-earned').inner_text()=='$1.00'
        for i in range(3):
            await page.get_by_test_id('referral-simulate-ref-jamie').click(force=True)
            await page.wait_for_timeout(350)
        await page.get_by_test_id('referral-claim-ref-jamie').click(force=True)
        await page.wait_for_timeout(500)
        assert await page.get_by_test_id('referrals-earned').inner_text()=='$2.00'
        print('PASS referrals sample activity/qualification/credit/link')
        await page.goto(base+'/dashboard')
        assert await page.get_by_test_id('referral-value').inner_text()=='$2.00'
        assert await page.locator('[data-testid$="-map"]').count()==0
        await page.get_by_test_id('dashboard-period').select_option('30')
        await page.get_by_test_id('dashboard-ad-close').click(force=True)
        await page.get_by_test_id('dashboard-restore-ad').click(force=True)
        assert await page.get_by_test_id('dashboard-ad-placement').is_visible()
        print('PASS dashboard no map/referral sync/chart period/ad dismiss restore')
    except Exception as e:
        print('FAIL financial/dashboard workflow',str(e))
    try:
        await page.goto(base+'/simulator')
        await page.set_viewport_size({'width':390,'height':844})
        await page.wait_for_timeout(500)
        print('OVERFLOW_RCA',await page.evaluate("[...document.querySelectorAll('body *')].map(e=>({tag:e.tagName,cls:e.className,id:e.dataset.testid,left:e.getBoundingClientRect().left,right:e.getBoundingClientRect().right,width:e.getBoundingClientRect().width})).filter(e=>e.right>innerWidth+1||e.left < -1).slice(0,25)"))
        await page.screenshot(path='/app/test_reports/refresh_workflows/automation_output/20261107_204533_acbc68275515/simulator-mobile-overflow.jpeg', type="jpeg", quality=40, full_page=False)
        await page.goto(base+'/rewards')
        await page.get_by_test_id('desk-set-preview-button').click(force=True)
        await page.wait_for_timeout(1000)
        image=page.get_by_test_id('reward-product-image')
        print('DESK_IMAGE',await image.evaluate('(e)=>({loaded:e.complete&&e.naturalWidth>0,width:e.naturalWidth,height:e.naturalHeight})'))
        assert await page.get_by_test_id('reward-locked-button').is_disabled()
        await page.screenshot(path='/app/test_reports/refresh_workflows/automation_output/20261107_204533_acbc68275515/desk-mobile.jpeg', type="jpeg", quality=40, full_page=False)
        print('PASS desk product visible and locked milestone')
    except Exception as e:
        print('FAIL mobile/reward',str(e))
    error_text=await page.evaluate("""() => {const errorElements = Array.from(document.querySelectorAll('.error, [class*="error"], [id*="error"]'));return errorElements.map(el => el.textContent).join(", ");}""")
    print(f'Found error message: {error_text}' if error_text else 'No error messages found on the page')
