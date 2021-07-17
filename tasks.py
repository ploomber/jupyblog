from invoke import task


@task
def docs_serve(c):
    c.run('mkdocs serve')