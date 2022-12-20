import jupytext
import nbclient
from jupytext.config import JupytextConfiguration

c = JupytextConfiguration()
c.notebook_metadata_filter
c.cell_metadata_filter = '-all'

nb = jupytext.read('_tutorial.md')

# cells = []

out = nbclient.execute(nb)

# for cell in nb.cells:
#     if 'hide' not in cell.metadata.get('tags', []):
#         cells.append(cell)

#     if 'hide-source' in cell.metadata.get('tags', []):
#         cell['source'] = ''
#         cells.append(cell)

# nb.cells = cells

jupytext.write(out, 'tutorial.ipynb')
