from invoke import task


@task
def docs_serve(c):
    with c.cd('docs'):
        c.run('jupyblog')

    c.run('mkdocs serve')
