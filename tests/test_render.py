
mdr = MarkdownRenderer('.')
out = mdr.render('sample.md')
print(out)
Path('out.md').write_text(out)
