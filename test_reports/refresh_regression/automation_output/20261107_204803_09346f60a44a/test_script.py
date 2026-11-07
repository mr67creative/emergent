async def run_test(page, output_dir, page_url):
    base=page.url.split('/')[0]+'//'+page.url.split('/')[2]
    await page.evaluate("localStorage.setItem('meantime-demo-token','I6wKwR2HzXjJXUBCDpi23TY8yadrjXAwRb1Yoa0MGy8')")
    await page.set_viewport_size({'width':1920,'height':800})
    try:
        await page.goto(base+'/advertiser')
        await page.get_by_test_id('campaign-name').fill('TEST_refresh_campaign')
        await page.get_by_test_id('composer-ad-headline-input').fill('TEST_refresh_headline')
        await page.get_by_test_id('composer-ad-description-input').fill('TEST_refresh_description')
        await page.get_by_test_id('composer-ad-cta-input').fill('TEST_visit')
        await page.get_by_test_id('save-campaign-button').click(force=True)
        await page.wait_for_timeout(450)
        await page.reload()
        await page.wait_for_selector('[data-testid="campaign-name"]')
        assert await page.get_by_test_id('campaign-name').input_value()=='TEST_refresh_campaign'
        assert await page.get_by_test_id('composer-ad-headline-input').input_value()=='TEST_refresh_headline'
        await page.get_by_test_id('variant-B').click(force=True)
        await page.get_by_test_id('composer-ad-headline-input').fill('TEST_second_variant')
        await page.get_by_test_id('variant-A').click(force=True)
        await page.get_by_test_id('submit-campaign-button').click(force=True)
        await page.wait_for_timeout(400)
        assert await page.get_by_test_id('campaign-status').inner_text()=='PENDING'
        await page.goto(base+'/extension')
        assert await page.get_by_test_id('popup-ad-headline').inner_text()=='TEST_refresh_headline'
        print('PASS studio editable 2-row AdBox/save/reload/variants/submit/shared popup preview')
        await page.goto(base+'/admin')
        await page.get_by_test_id('review-filter-ad').click(force=True)
        while await page.get_by_test_id('review-brand').inner_text()!='TEST_refresh_campaign':
            await page.get_by_test_id('next-review').click(force=True)
        await page.get_by_test_id('approve-review-button').click(force=True)
        await page.wait_for_timeout(400)
        await page.goto(base+'/simulator')
        assert await page.get_by_test_id('hero-ad-headline').inner_text()=='TEST_refresh_headline'
        print('PASS moderation approval propagates to simulator creative')
        await page.goto(base+'/advertiser')
        await page.get_by_test_id('composer-ad-headline-input').fill('TEST_updated_headline')
        await page.get_by_test_id('save-campaign-button').click(force=True)
        await page.wait_for_timeout(400)
        page.once('dialog', lambda dialog: dialog.accept())
        await page.get_by_test_id('delete-campaign-button').click(force=True)
        await page.wait_for_timeout(450)
        assert await page.get_by_test_id('saved-campaign-select').locator('option').count()==1
        print('PASS creative update and delete')
    except Exception as e:
        print('FAIL studio/admin',repr(e))
    try:
        await page.goto(base+'/rewards')
        assert await page.locator('[data-testid^="reward-node-"]').count()==4
        assert await page.get_by_text('overclock',exact=False).count()==0
        await page.get_by_test_id('reward-node-stickers').click(force=True)
        await page.get_by_test_id('reward-claim-button').click(force=True)
        await page.wait_for_timeout(400)
        await page.get_by_test_id('reward-advance-button').click(force=True)
        await page.wait_for_timeout(400)
        await page.get_by_test_id('reward-advance-button').click(force=True)
        await page.wait_for_selector('[data-testid="reward-delivered"]')
        print('PASS four physical milestones/no overclock/claim/dispatch/delivery')
        await page.keyboard.press('Escape')
        await page.goto(base+'/insights')
        await page.get_by_test_id('insight-bookmark-kv-cache').click(force=True)
        await page.wait_for_timeout(300)
        await page.get_by_test_id('insights-bookmarked-filter').click(force=True)
        assert await page.locator('[data-testid^="insight-card-"]').count()==1
        await page.get_by_test_id('insight-open-kv-cache').click(force=True)
        await page.get_by_test_id('reader-mark-read').click(force=True)
        await page.wait_for_timeout(300)
        assert await page.get_by_test_id('reader-mark-read').is_disabled()
        assert 'https://' in await page.get_by_test_id('reader-source-link').get_attribute('href')
        await page.keyboard.press('Escape')
        await page.goto(base+'/admin')
        await page.get_by_test_id('review-filter-insight').click(force=True)
        await page.keyboard.press('k')
        await page.wait_for_timeout(350)
        assert await page.get_by_test_id('review-empty').is_visible()
        print('PASS insights bookmark/filter/reader/read/source and admin keyboard rejection')
    except Exception as e:
        print('FAIL rewards/insights',repr(e))
    try:
        await page.goto(base+'/payouts')
        await page.get_by_test_id('payout-amount-input').fill('5.0004')
        print('PAYOUT_FRACTION_ROUNDING',await page.get_by_test_id('payout-amount-input').input_value())
        await page.goto(base+'/dashboard')
        assert await page.get_by_test_id('withdraw-button').is_disabled()
        print('PASS quick withdrawal disabled below minimum')
    except Exception as e:
        print('FAIL payout check',repr(e))
    error_text=await page.evaluate("""() => {const errorElements = Array.from(document.querySelectorAll('.error, [class*="error"], [id*="error"]'));return errorElements.map(el => el.textContent).join(", ");}""")
    print(f'Found error message: {error_text}' if error_text else 'No error messages found on the page')
