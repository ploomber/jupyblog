# Advanced configuration


## Default front matter

You can add a default front matter to all your posts, add this toy our  `jupyblog.yaml`:

```yaml
front_matter_template: front-matter.yaml
```

Then, store your default front matter in a `front-matter.yaml` file. For example, let's say your blog engine takes author information in an `author_info` field:

```yaml
author_info:
  name: "John Doe"
  image: "images/author/john-doe.png"
```

You can also use a few placeholders that will be resolved when rendering your post:

```yaml
# {{name}} resolves to the name of your post (the folder name that contains it)
image: "images/blog/{{name}}.png"

# {{now}} resolves to the current timestamp
date: '{{now}}'
```


## UTM tags

To include UTM tags to all links in a posts, add the following to your `jupyblog.yaml` file:

```yaml
utm_source: some-source
utm_medium: some-medium
```
