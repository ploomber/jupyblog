import re

# match ![any num of word characters or hyphens](filename)
regex = re.compile(f'!\[[\w-]*\]\((.*)\)')


def make_img_links_absolute(post, prefix):
    for match in re.finditer(regex, post):
        img = match.group(0)
        img_link = match.group(1)
        img_link_fixed = '/'+prefix+'-'+img_link.split('/')[-1]
        post = post.replace(img, img.replace(img_link, img_link_fixed))

    return post
