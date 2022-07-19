from pathlib import Path

import jupytext
import nbclient

front_matter = """\
---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.13.6
  kernelspec:
    display_name: Python 3 (ipykernel)
    language: python
    name: python3
---
"""

# add front matter so jupytext correctly identifies the bash cells and adds
# the %%bash magic
content = front_matter + Path('README.md').read_text()

nb = jupytext.reads(content)

nbclient.execute(nb)
