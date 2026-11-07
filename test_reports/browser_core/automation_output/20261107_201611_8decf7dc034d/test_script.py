async def run_test(page, output_dir, page_url):
    await page.set_viewport_size({'width':1920,'height':800})
    base = page.url.rstrip('/')
    async def profile():
     return await page.evaluate("""async () => (await fetch('/api/state', {headers:{'X-Demo-Token':localStorage.getItem('meantime-demo-token')}})).json()""")
    try:
     await page.wait_for_selector('[data-testid="send-prompt-button"]',timeout=20000)
     await page.wait_for_function("!document.querySelector('[data-testid=send-prompt-button]').disabled")
     assert await page.get_by_test_id('charge-vault-total').inner_text() == '$14.850'
     await page.screenshot(path='/app/test_reports/browser_core/automation_output/20261107_201611_8decf7dc034d/landing.jpeg', type="jpeg", quality=40, full_page=False)
     await page.get_by_test_id('send-prompt-button').click()
     await page.wait_for_timeout(5500)
     assert (await profile())['profile']['balance_mills']==14861
     print('PASS five-second charge +11 mills')
     await page.get_by_test_id('send-prompt-button').click()
     await page.wait_for_timeout(500)
     await page.get_by_test_id('hero-ad-dismiss').click()
     await page.wait_for_timeout(5100)
     assert (await profile())['profile']['balance_mills']==14861
     await page.get_by_test_id('restore-ad').click()
     await page.get_by_test_id('insight-mode-button').click()
     await page.get_by_test_id('send-prompt-button').click()
     await page.wait_for_timeout(5500)
     assert (await profile())['profile']['balance_mills']==14861
     print('PASS dismiss cancellation, restore, insight nonbilling')
     await page.get_by_test_id('ad-mode-button').click()
     await page.get_by_test_id('home-bid-slider').fill('0.05')
     assert await page.get_by_test_id('split-user-share').inner_text()=='$0.0275'
     assert await page.get_by_test_id('split-platform-share').inner_text()=='$0.0225'
     assert await page.locator('.desktop-nav a[href="/simulator"]').count()==0
     await page.get_by_test_id('profile-menu-button').click()
     await page.wait_for_timeout(200)
     await page.get_by_test_id('profile-simulator').click(force=True)
     await page.wait_for_selector('[data-testid="sim-total-views"]')
     for host in ['ChatGPT','Claude','Gemini','DeepSeek','Grok']:
      selector=page.get_by_test_id('sim-platform-'+host)
      if await selector.count():
       await selector.click()
      else:
       print('Host spelling:',await page.locator('.platform-switcher').inner_text())
     print('PASS simulator profile access')
    except Exception as e:
     print('FAIL home/simulator:',str(e))
    try:
     await page.goto(base+'/insights')
     await page.wait_for_selector('[data-testid="insight-card-kv-cache"]')
     await page.get_by_test_id('insights-filter-Systems').click()
     assert await page.locator('[data-testid^="insight-card-"]').count()==1
     await page.get_by_test_id('insights-filter-All-topics').click()
     await page.get_by_test_id('insights-time-filter').select_option('180')
     assert await page.locator('[data-testid^="insight-card-"]').count()==1
     await page.get_by_test_id('insights-time-filter').select_option('all')
     await page.get_by_test_id('insight-bookmark-kv-cache').click()
     await page.wait_for_timeout(300)
     await page.get_by_test_id('insight-upvote-kv-cache').click()
     await page.wait_for_timeout(300)
     await page.get_by_test_id('insights-bookmarked-filter').click()
     assert await page.locator('[data-testid^="insight-card-"]').count()==1
     await page.get_by_test_id('insight-open-kv-cache').click()
     await page.wait_for_selector('[data-testid="reader-mark-read"]')
     assert (await page.get_by_test_id('reader-source-link').get_attribute('href')).startswith('https://huggingface.co/')
     await page.get_by_test_id('reader-mark-read').click(force=True)
     await page.wait_for_timeout(400)
     assert await page.get_by_test_id('reader-mark-read').is_disabled()
     assert (await profile())['profile']['discovered']['AI / ML']==12
     await page.keyboard.press('Escape')
     await page.reload()
     await page.wait_for_selector('[data-testid="insight-upvote-kv-cache"]')
     assert 'selected' in await page.get_by_test_id('insight-upvote-kv-cache').get_attribute('class')
     assert 'selected' in await page.get_by_test_id('insight-bookmark-kv-cache').get_attribute('class')
     print('PASS insight filters, bookmarks, upvotes, reader, read-once and reload')
     await page.get_by_test_id('insights-contribute-tab').click()
     assert 'Separate from ad billing' in await page.locator('.organic-footer').inner_text()
     await page.get_by_test_id('new-insight-button').click()
     await page.get_by_test_id('publish-insight-button').click(force=True)
     assert await page.get_by_test_id('insight-compose-modal').is_visible()
     await page.get_by_test_id('compose-headline').fill('TEST_UI micro insight')
     await page.get_by_test_id('compose-body').fill('TEST_A small technical idea with enough meaningful text to satisfy the editorial minimum.')
     await page.get_by_test_id('compose-source').fill('https://example.org/docs')
     await page.get_by_test_id('compose-topic').select_option('Systems',force=True)
     await page.get_by_test_id('publish-insight-button').click(force=True)
     await page.wait_for_timeout(700)
     assert await page.get_by_test_id('insight-compose-modal').count()==0
     submission=(await profile())['submissions'][0]
     assert submission['status']=='pending'
     print('PASS brand required validation and pending submission',submission['id'])
    except Exception as e:
     print('FAIL insights:',str(e))
    try:
     await page.goto(base+'/rewards')
     await page.wait_for_selector('[data-testid="reward-node-stickers"]')
     for reward in ['tee','hoodie','desk']:
      await page.get_by_test_id('reward-node-'+reward).click()
      assert await page.get_by_test_id('reward-locked-button').is_disabled()
      await page.keyboard.press('Escape')
     await page.get_by_test_id('reward-node-stickers').click()
     await page.get_by_test_id('reward-claim-button').click(force=True)
     await page.wait_for_selector('[data-testid="reward-advance-button"]')
     await page.get_by_test_id('reward-advance-button').click(force=True)
     await page.wait_for_timeout(400)
     assert 'Simulate delivery' in await page.get_by_test_id('reward-advance-button').inner_text()
     await page.get_by_test_id('reward-advance-button').click(force=True)
     await page.wait_for_selector('[data-testid="reward-delivered"]')
     await page.keyboard.press('Escape')
     await page.get_by_test_id('reward-node-boost').click()
     await page.get_by_test_id('reward-claim-button').click(force=True)
     await page.wait_for_selector('[data-testid="boost-active"]')
     await page.keyboard.press('Escape')
     await page.reload()
     await page.wait_for_selector('[data-testid="reward-node-stickers"]')
     await page.get_by_test_id('reward-node-stickers').click()
     await page.wait_for_selector('[data-testid="reward-delivered"]')
     assert await page.locator('input').count()==0
     print('PASS all milestone previews, shipping, boost and claim persistence; no address')
    except Exception as e:
     print('FAIL rewards:',str(e))
    try:
     await page.goto(base+'/dashboard')
     await page.wait_for_selector('[data-testid="earnings-balance"]')
     assert await page.get_by_test_id('earnings-balance').inner_text()=='$14.86'
     await page.get_by_test_id('dashboard-period').select_option('30')
     assert '58,240' in await page.locator('.analytics-grid .panel-header').first.inner_text()
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
     assert 'No money moves' in await page.get_by_test_id('withdraw-simulation-note').inner_text()
     await page.get_by_test_id('withdraw-cancel').click(force=True)
     await page.get_by_test_id('withdraw-button').click()
     await page.get_by_test_id('withdraw-confirm').click(force=True)
     await page.wait_for_timeout(500)
     assert await page.get_by_test_id('earnings-balance').inner_text()=='$0.00'
     assert await page.get_by_test_id('withdraw-button').is_disabled()
     assert await page.locator('[data-testid^="transaction-"]').count()==1
     await page.goto(base+'/')
     await page.wait_for_selector('[data-testid="charge-vault-total"]')
     print('AFTER WITHDRAW LANDING VAULT:',await page.get_by_test_id('charge-vault-total').inner_text())
     print('PASS dashboard period, persistence, tooltip, heatmap, withdrawal/minimum')
    except Exception as e:
     print('FAIL dashboard:',str(e))
    error_text=await page.evaluate("""() => {const errorElements = Array.from(document.querySelectorAll('.error, [class*="error"], [id*="error"]'));return errorElements.map(el => el.textContent).join(', ');} """)
    print('Found error message: '+error_text if error_text else 'No error messages found on the page')
    print('UI TOKEN:',await page.evaluate("localStorage.getItem('meantime-demo-token')"))
