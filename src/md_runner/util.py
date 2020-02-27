def find_endings(md):
    n_all = [n for n, l in enumerate(md.splitlines()) if l.startswith('```')]
    endings = [n for i, n in enumerate(n_all) if i % 2]
    return endings


def add_output_tags(md, outputs):
    endings = find_endings(md)
    lines = md.splitlines()

    shifts = 0

    for out, end in zip(outputs, endings):
        if out is not None:
            to_insert = "\n```{}\n```".format(out)
            lines.insert(end + 1 + shifts, to_insert)
            shifts += 1

    md_new = '\n'.join(lines)

    return md_new
