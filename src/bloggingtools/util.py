import shutil
from pathlib import Path
from glob import glob
from jinja2 import Template


def find_endings(md):
    n_all = [n for n, l in enumerate(md.splitlines()) if l.startswith('```')]
    endings = [n for i, n in enumerate(n_all) if i % 2]
    return endings


def build_output(parts):
    # remove trailing and leading whitespace, remove empty content
    parts = [(kind, content.rstrip().lstrip()) for kind, content in parts
             if content]

    t = Template("""
{% for kind, content in parts %}
**Console output: ({{loop.index}}/{{total}}):**
{% if kind == 'text/plain' %}
```
{{content}}
```
{% else %}
{{content}}{% endif %}{% endfor %}""")

    return t.render(parts=parts, total=len(parts))


def add_output_tags(md, outputs):
    endings = find_endings(md)
    lines = md.splitlines()

    shifts = 0

    for out, end in zip(outputs, endings):
        if out is not None:
            # add trailing \n if there is not any
            # out = out if out[-1] == '\n' else out + '\n'
            # remove leading \n if any, we will ad one
            # out = out if out[0] != '\n' else out[1:]

            to_insert = build_output(out)
            lines.insert(end + 1 + shifts, to_insert)
            shifts += 1

    md_new = '\n'.join(lines)

    return md_new


def copy_images(path, canonical_name, target):
    for img in glob(str(Path(path, '*.png'))):
        name = Path(img).name
        target_file = str(Path(target, canonical_name + '-' + name))
        print('Moving %s to %s' % (img, target_file))
        shutil.copy(img, target_file)
