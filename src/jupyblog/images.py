from pathlib import PurePosixPath
import re

# match ![any num of word characters, [space], -, _ or .](filename)
REGEX_IMAGE = re.compile(r'!\[[\ \_\.\-\w]*\]\((.*)\)')


def find_images(md):
    for match in re.finditer(REGEX_IMAGE, md):
        yield match.group(0), match.group(1)


# FIXME: remove absolute arg, no longer used
def process_image_links(post, prefix, *, absolute):
    for img, img_link in find_images(post):
        # ignore paths that are already absolute, they come from
        # serialized images
        prefix_part = '' if not prefix else prefix + '/'

        if not PurePosixPath(img_link).is_absolute():
            img_link_fixed = ('/' if absolute else '') + prefix_part + img_link
            post = post.replace(img, img.replace(img_link, img_link_fixed))

    return post


def get_first_image_path(md):
    images = find_images(md)

    try:
        _, path = next(images)
    except StopIteration:
        return None

    return path


def add_image_placeholders(md):
    """This helps when uploading to medium
    """
    for img_tag, img_link in find_images(md):
        md = md.replace(img_tag, f'**ADD {img_link} HERE**\n{img_tag}')

    return md
