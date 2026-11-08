async def run_test(page, output_dir, page_url):
    try:
        await page.set_viewport_size({'width':1920,'height':800})
        await page.get_by_test_id('hero-send').wait_for(state='visible')
        await page.get_by_test_id('hero-send').click(force=True)
        await page.get_by_test_id('hero-ad-box').wait_for(state='visible')
        print('PASS hero interactive ad')
        await page.get_by_test_id('hero-response').wait_for(state='visible',timeout=12000)
        await page.get_by_test_id('hero-receipt').wait_for(state='visible')
        assert await page.get_by_test_id('hero-earned').inner_text()=='+$0.011'
        print('PASS hero simulated response and payout')
        await page.screenshot(path='/app/test_reports/workflow_smoke/automation_output/20261108_055941_0bc446578eff/hero.jpeg', type="jpeg", quality=40, full_page=False)
        print('TEST_TOKEN',await page.evaluate("localStorage.getItem('meantime-demo-token')"))
        error_text = await page.evaluate("""() => {const errorElements = Array.from(document.querySelectorAll('.error, [class*="error"], [id*="error"]'));return errorElements.map(el => el.textContent).join(', ');} """)
        print(f'Found error message: {error_text}' if error_text else 'No error messages found on the page')
    except Exception as e:
        print('FAIL smoke',str(e))
