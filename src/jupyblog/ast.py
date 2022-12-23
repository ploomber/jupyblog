def create_md_parser():
    import mistune

    return mistune.create_markdown(renderer=mistune.AstRenderer())


def _traverse(ast):
    for node in ast:
        yield node

        if node.get("children"):
            yield from _traverse(node["children"])


# TODO: use this in ast executor
class MarkdownAST:
    def __init__(self, doc):
        parser = create_md_parser()
        self.ast_raw = parser(doc)
        self.doc = doc

    def iter_blocks(self):
        for node in self.ast_raw:
            if node["type"] == "block_code":
                yield node

    def iter_links(self):
        for node in _traverse(self.ast_raw):
            if node["type"] == "link":
                yield node["link"]

    def replace_blocks(self, blocks_new):
        doc = self.doc

        # TODO: support for code fences with structured info
        for block, replacement in zip(self.iter_blocks(), blocks_new):
            to_replace = f'```{block["info"]}\n{block["text"]}```'
            doc = doc.replace(to_replace, replacement)

        return doc
