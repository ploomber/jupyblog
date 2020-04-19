from jinja2 import Template


def find_endings(md):
    n_all = [n for n, l in enumerate(md.splitlines()) if l.startswith('```')]
    endings = [n for i, n in enumerate(n_all) if i % 2]
    return endings


def build_output(parts):

    t = Template("""
**Output:**
{% for kind, content in parts %}{% if kind == 'text/plain' %}
```
{{content}}
```
{% else %}
{{content}}
{% endif %}{% endfor %}
""")

    return t.render(parts=parts)


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
