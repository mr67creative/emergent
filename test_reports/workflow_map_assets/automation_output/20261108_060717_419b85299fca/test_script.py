async def run_test(page, output_dir, page_url):
    namespace={}
    exec(compile(open('/app/tests/workflow_map_assets.py').read(),'/app/tests/workflow_map_assets.py','exec'),namespace)
    await namespace['run'](page)
