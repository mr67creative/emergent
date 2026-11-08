async def run_test(page, output_dir, page_url):
    namespace={}
    exec(compile(open('/app/tests/workflow_boundaries.py').read(),'/app/tests/workflow_boundaries.py','exec'),namespace)
    await namespace['run'](page)
