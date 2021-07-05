from md_runner.md import MarkdownRenderer


def test_render(path_to_tests):
    mdr = MarkdownRenderer(str(path_to_tests / 'assets'))
    out = mdr.render('sample.md')
