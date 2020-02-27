%load_ext autoreload
%autoreload 2

from pathlib import Path
import logging

from md_runner.md import MarkdownRenderer

logging.basicConfig(level=logging.DEBUG)

mdr = MarkdownRenderer('.')
out = mdr.render('sample.md')

print(out)

Path('out.md').write_text(out)
