async def run_test(page, output_dir, page_url):
    namespace={}
    exec(compile(open('/app/tests/workflow_e2e.py').read(),'/app/tests/workflow_e2e.py','exec'),namespace)
    await namespace['run'](page)
