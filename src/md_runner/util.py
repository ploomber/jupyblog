def find_endings(md):
    n_all = [n for n, l in enumerate(md.splitlines()) if l.startswith('```')]
    endings = [n for i, n in enumerate(n_all) if i % 2]
    return endings


def add_output_tags(md, outputs, header=None):
    endings = find_endings(md)
    lines = md.splitlines()

    header = header+'\n' if header is not None else ''

    shifts = 0

    for out, end in zip(outputs, endings):
        if out is not None:
            # add trailing \n if there is not any
            out = out if out[-1] == '\n' else out + '\n'
            # remove leading \n if any, we will ad one
            out = out if out[0] != '\n' else out[1:]

            to_insert = "\n```\n{}{}```\n".format(header, out)
            lines.insert(end + 1 + shifts, to_insert)
            shifts += 1

    md_new = '\n'.join(lines)

    return md_new
