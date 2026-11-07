async def run_test(page, output_dir, page_url):
    base=page.url.rstrip('/')
    await page.evaluate("localStorage.setItem('meantime-demo-token','1PDBAvoIksPCuIFVfiwCpCa3cqV1aY4eCRgil1H3aeA')")
    await page.set_viewport_size({'width':390,'height':844})
    for route,name in [('/dashboard','dashboard'),('/rewards','rewards'),('/advertiser','studio')]:
     try:
      await page.goto(base+route)
      await page.wait_for_timeout(1000)
      await page.screenshot(path='/app/test_reports/browser_visual/automation_output/20261107_201845_d7791bfe28f4/browser_visual.jpeg'+name+'.jpeg', type="jpeg", quality=40, full_page=False)
      print('PASS mobile screenshot',route)
     except Exception as e: print('FAIL screenshot',repr(e))
    try:
     await page.goto(base+'/simulator')
     await page.wait_for_selector('[data-testid="sim-balance"]')
     for n in [1,2]:
      before=await page.get_by_test_id('sim-balance').inner_text()
      await page.get_by_test_id('send-prompt-button').click()
      await page.wait_for_timeout(5500)
      print('BOOST UI',n,'before',before,'after',await page.get_by_test_id('sim-balance').inner_text(),'earned indicator',await page.get_by_test_id('charge-earned').inner_text())
     print('PASS boosted credit completed; compare actual balance and indicator')
    except Exception as e: print('FAIL boosted UI',repr(e))
