<!-- #region -->
# Jupyblog

Jupyblog executes code snippets in markdown files and embeds the results as new code snippets.

We use it at [Ploomber](https://github.com/ploomber/ploomber) to write [technical blog posts](https://ploomber.io/blog/snapshot-testing/) and publish them in our [Hugo](https://github.com/gohugoio/hugo) blog; however, any engine that takes markddown files works.

https://user-images.githubusercontent.com/989250/180660666-d1262a07-2cd9-45ae-9019-79d79ef693e9.mp4


For example, if your **input** is a markdown like this:

~~~md

# My markdown post

Some description

```python
1 + 1
```
~~~

The **output** will look like this:

~~~md

# My markdown post

Some description

```python
1 + 1
```

**Console output (1/1):**

```
2
```

~~~

Jupyblog supports rich outputs like HTML tables or matplotlib plots.

## Installation

```sh
pip install jupyblog
```

Works with Python 3.7 and higher.

## Example

* Input: [docs/post.md](docs/post.md)
* Output: [docs/output/docs.md](docs/output/docs.md)

To reproduce the example, get the sample markdown and configuration files:

```sh
git clone https://github.com/ploomber/jupyblog
```

Execute markdown file:
<!-- #endregion -->

```bash
cd docs
jupyblog render
```

Then, open `output/docs.md`

## Documentation

Check out [docs/tutorial.ipynb](docs/tutorial.ipynb).

## Support

For support, feature requests, and product updates: [join our community](https://ploomber.io/community) or follow us on [Twitter](https://twitter.com/ploomber)/[LinkedIn](https://www.linkedin.com/company/ploomber/).


## Telemetry

We collect anonymous statistics to understand and improve usage. For details, [see here](https://docs.ploomber.io/en/latest/community/user-stats.html)
