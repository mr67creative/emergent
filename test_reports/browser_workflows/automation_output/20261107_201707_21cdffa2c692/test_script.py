async def run_test(page, output_dir, page_url):
    await page.set_viewport_size({'width':1920,'height':800})
    base=page.url.rstrip('/')
    await page.evaluate("localStorage.setItem('meantime-demo-token','1PDBAvoIksPCuIFVfiwCpCa3cqV1aY4eCRgil1H3aeA')")
    await page.reload()
    async def profile():
     return await page.evaluate("""async () => (await fetch('/api/state',{headers:{'X-Demo-Token':localStorage.getItem('meantime-demo-token')}})).json()""")
    try:
     await page.goto(base+'/insights')
     await page.get_by_test_id('insight-open-kv-cache').click()
     await page.wait_for_timeout(600)
     await page.get_by_test_id('reader-mark-read').click(force=True)
     await page.wait_for_timeout(400)
     assert await page.get_by_test_id('reader-mark-read').is_disabled()
     assert (await profile())['profile']['discovered']['AI / ML']==12
     await page.keyboard.press('Escape')
     await page.wait_for_timeout(400)
     await page.reload()
     await page.wait_for_selector('[data-testid="insight-upvote-kv-cache"]')
     assert 'selected' in await page.get_by_test_id('insight-upvote-kv-cache').get_attribute('class')
     assert 'selected' in await page.get_by_test_id('insight-bookmark-kv-cache').get_attribute('class')
     print('PASS persisted upvote, bookmark, read and discovered')
     await page.get_by_test_id('insights-contribute-tab').click()
     assert 'Separate from ad billing' in await page.locator('.organic-footer').inner_text()
     await page.get_by_test_id('new-insight-button').click()
     await page.wait_for_timeout(400)
     await page.get_by_test_id('publish-insight-button').click(force=True)
     assert await page.get_by_test_id('insight-compose-modal').is_visible()
     await page.get_by_test_id('compose-headline').fill('TEST_UI micro insight')
     await page.get_by_test_id('compose-body').fill('TEST_A small technical idea with enough meaningful text to satisfy the editorial minimum.')
     await page.get_by_test_id('compose-source').fill('https://example.org/docs')
     await page.get_by_test_id('compose-topic').select_option('Systems',force=True)
     await page.get_by_test_id('publish-insight-button').click(force=True)
     await page.wait_for_timeout(600)
     assert await page.get_by_test_id('insight-compose-modal').count()==0
     assert (await profile())['submissions'][0]['status']=='pending'
     print('PASS required brand contribution and pending')
    except Exception as e: print('FAIL insights',repr(e))
    try:
     await page.goto(base+'/rewards')
     await page.get_by_test_id('reward-node-stickers').click()
     await page.wait_for_timeout(600)
     await page.get_by_test_id('reward-claim-button').click(force=True)
     await page.wait_for_selector('[data-testid="reward-advance-button"]')
     await page.get_by_test_id('reward-advance-button').click(force=True)
     await page.wait_for_timeout(400)
     assert 'Simulate delivery' in await page.get_by_test_id('reward-advance-button').inner_text()
     await page.get_by_test_id('reward-advance-button').click(force=True)
     await page.wait_for_selector('[data-testid="reward-delivered"]')
     await page.keyboard.press('Escape')
     await page.wait_for_timeout(400)
     await page.get_by_test_id('reward-node-boost').click()
     await page.wait_for_timeout(600)
     await page.get_by_test_id('reward-claim-button').click(force=True)
     await page.wait_for_selector('[data-testid="boost-active"]')
     await page.keyboard.press('Escape')
     await page.wait_for_timeout(400)
     await page.reload()
     await page.get_by_test_id('reward-node-stickers').click()
     await page.wait_for_timeout(600)
     assert await page.get_by_test_id('reward-delivered').is_visible()
     assert await page.locator('input').count()==0
     print('PASS claim, dispatch, delivery, boost, reload without address')
    except Exception as e: print('FAIL rewards',repr(e))
    try:
     await page.goto(base+'/dashboard')
     await page.wait_for_selector('[data-testid="earnings-balance"]')
     print('Balance:',await page.get_by_test_id('earnings-balance').inner_text())
     await page.get_by_test_id('dashboard-period').select_option('30')
     assert '58,240' in await page.locator('.analytics-grid .panel-header').first.inner_text()
     if 'selected' not in await page.get_by_test_id('interest-Finance').get_attribute('class'):
      await page.get_by_test_id('interest-Finance').click()
      await page.wait_for_timeout(400)
     await page.reload()
     await page.wait_for_selector('[data-testid="interest-Finance"]')
     assert 'selected' in await page.get_by_test_id('interest-Finance').get_attribute('class')
     await page.get_by_test_id('interests-tab-Discovered').click()
     assert await page.get_by_test_id('interest-AI-/-ML').is_visible()
     await page.get_by_test_id('user-world-country-United-States').hover()
     await page.wait_for_selector('[data-testid="user-world-tooltip"]')
     assert 'CPVV' in await page.get_by_test_id('user-world-tooltip').inner_text()
     assert await page.locator('[data-testid^="user-activity-cell-"]').count()==168
     assert 'UTC' in await page.get_by_test_id('user-activity-cell-0').get_attribute('title')
     await page.get_by_test_id('withdraw-button').click()
     await page.wait_for_timeout(400)
     assert 'No money moves' in await page.get_by_test_id('withdraw-simulation-note').inner_text()
     await page.get_by_test_id('withdraw-cancel').click(force=True)
     await page.get_by_test_id('withdraw-button').click()
     await page.wait_for_timeout(400)
     await page.get_by_test_id('withdraw-confirm').click(force=True)
     await page.wait_for_timeout(500)
     assert await page.get_by_test_id('earnings-balance').inner_text()=='$0.00'
     assert await page.get_by_test_id('withdraw-button').is_disabled()
     assert await page.locator('[data-testid^="transaction-"]').count()==1
     print('PASS dashboard period, interests, hover, heatmap, withdrawal minimum')
     await page.goto(base+'/')
     await page.wait_for_selector('[data-testid="charge-vault-total"]')
     await page.wait_for_timeout(600)
     print('ZERO BALANCE HOME DISPLAY',await page.get_by_test_id('charge-vault-total').inner_text())
    except Exception as e: print('FAIL dashboard',repr(e))
    try:
     await page.goto(base+'/advertiser')
     await page.get_by_test_id('campaign-name').fill('TEST_UI campaign')
     for v in ['A','B','C']:
      await page.get_by_test_id('variant-'+v).click()
      await page.get_by_test_id('composer-ad-headline-input').fill('TEST_variant_'+v)
      await page.get_by_test_id('composer-ad-description-input').fill('TEST_description_'+v)
      await page.get_by_test_id('composer-ad-cta-input').fill('TEST_'+v)
     for v in ['A','B','C']:
      await page.get_by_test_id('variant-'+v).click()
      assert await page.get_by_test_id('composer-ad-headline-input').input_value()=='TEST_variant_'+v
     assert await page.get_by_test_id('composer-ad-headline-input').get_attribute('maxlength')=='70'
     assert await page.get_by_test_id('composer-ad-description-input').get_attribute('maxlength')=='140'
     assert await page.get_by_test_id('composer-ad-cta-input').get_attribute('maxlength')=='20'
     for host in ['ChatGPT','Claude','Gemini','DeepSeek','Grok']:
      await page.get_by_test_id('studio-host-'+host).click()
     for target in ['Cloud','Hardware','Science','Finance']:
      await page.get_by_test_id('target-'+target).click()
     forecast=await page.get_by_test_id('forecast-views').inner_text()
     await page.get_by_test_id('campaign-bid-slider').fill('0.05')
     assert forecast!=await page.get_by_test_id('forecast-views').inner_text()
     await page.get_by_test_id('campaign-budget-slider').fill('1000')
     await page.get_by_test_id('campaign-destination-url').fill('invalid')
     await page.get_by_test_id('save-campaign-button').click()
     await page.wait_for_timeout(300)
     assert len((await profile())['campaigns'])==0
     await page.get_by_test_id('campaign-destination-url').fill('https://example.org')
     await page.get_by_test_id('save-campaign-button').click()
     await page.wait_for_timeout(500)
     saved=(await profile())['campaigns'][0]
     assert saved['bid']==.05 and saved['budget']==1000
     await page.reload()
     await page.wait_for_selector('[data-testid="campaign-name"]')
     assert await page.get_by_test_id('campaign-name').input_value()=='TEST_UI campaign'
     await page.get_by_test_id('new-campaign-button').click()
     assert await page.get_by_test_id('campaign-name').input_value()!='TEST_UI campaign'
     await page.get_by_test_id('saved-campaign-select').select_option(saved['id'])
     await page.get_by_test_id('submit-campaign-button').click()
     await page.wait_for_timeout(500)
     assert (await profile())['campaigns'][0]['status']=='pending'
     print('PASS studio variants, limits, all hosts/targets, forecast, URL, save/reload, selector/new, submission')
    except Exception as e: print('FAIL studio',repr(e))
    print('UI TOKEN',await page.evaluate("localStorage.getItem('meantime-demo-token')"))
