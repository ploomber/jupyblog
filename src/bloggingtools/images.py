import re

# match ![any num of word characters or hyphens](filename)
REGEX_IMAGE = re.compile(r'!\[[\w-]*\]\((.*)\)')


def find_images(md):
    for match in re.finditer(REGEX_IMAGE, md):
        yield match.group(0), match.group(1)


def make_img_links_absolute(post, prefix):
    for img, img_link in find_images(post):
        img_link_fixed = '/' + prefix + '/' + img_link.split('/')[-1]
        post = post.replace(img, img.replace(img_link, img_link_fixed))

    return post


def get_first_image_path(md):
    images = find_images(md)

    try:
        _, path = next(images)
    except StopIteration:
        return None

    return path


def replace_images_with_placeholders(md):
    """This helps when uploading to medium
    """
    for img_tag, img_link in find_images(md):
        md = md.replace(img_tag, f'**ADD {img_link} HERE**')

    return md