from jupyblog import md


def upload_to_github(doc, name):
    gu = md.GistUploader(doc)
    doc = gu.upload_blocks(prefix=name)

    data = dict(description=f'Blog post: {name}',
                files={f'{name}.md': {
                    'content': doc
                }},
                public=False)

    response = gu._api.gists.create(**data)
    return f'https://gist.github.com/{response.id}'
