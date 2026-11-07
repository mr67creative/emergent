async def run_test(page, output_dir, page_url):
    import sys
    sys.path.insert(0,'/app/tests')
    from refresh_responsive import run
    await page.wait_for_selector('[data-testid="send-prompt-button"]',timeout=20000)
    print('FINAL_SESSION_TOKEN='+str(await page.evaluate("localStorage.getItem('meantime-demo-token')")))
    await run(page)
