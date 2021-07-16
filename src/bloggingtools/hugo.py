import re

# match ![any num of word characters or hyphens](filename)
REGEX = re.compile(f'!\[[\w-]*\]\((.*)\)')


def find_images(md):
    for match in re.finditer(REGEX, md):
        yield match.group(0), match.group(1)


def make_img_links_absolute(post, prefix):
    for img, img_link in find_images(post):
        img_link_fixed = '/' + prefix + '/' + img_link.split('/')[-1]
        post = post.replace(img, img.replace(img_link, img_link_fixed))

    return post


def get_first_image_path(md):
    images = find_images(md)
    _, path = next(images)
    return path