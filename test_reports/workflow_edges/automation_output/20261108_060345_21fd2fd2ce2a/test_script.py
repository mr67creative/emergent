async def run_test(page, output_dir, page_url):
    namespace={}
    exec(compile(open('/app/tests/workflow_edges.py').read(),'/app/tests/workflow_edges.py','exec'),namespace)
    await namespace['run'](page)
