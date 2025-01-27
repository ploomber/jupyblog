# CHANGELOG

## 0.0.16dev

## 0.0.15 (2025-01-10)

* [Feature] Copying `.webm` files when rendering posts

## 0.0.14 (2024-03-25)

* [Feature] Keep existing date if the current file has been rendered already
* [Feature] Add utm codes to front matter url (`marketing.url`)
* [Feature] Adding `jupyblog.version_jupyblog` to rendered markdown files
* [Feature] Only add UTM tags to URLs included in `utm_base_urls` (`jupyblog.yml`)

## 0.0.13 (2023-03-14)

* [Feature] Rendering fails if front matter template contains undefined placeholders
* [Feature] Front matter template now accepts environment variables as parameters: `{{env.ENV_VAR}}`
* [Fix] Rendering a `post.ipynb` file no londer needs a copy in markdown format (`post.md`)

## 0.0.12 (2023-02-24)

* [Feature] Adds `jupyblog tomd` to export Jupyter notebooks with outputs to Markdown
* [Fix] Keeping `%%sql` magic when exporting to Markdown

## 0.0.11 (2022-12-21)

* Fixes error when expanding utms in posts where the same base url appeared more than once

## 0.0.10 (2022-11-17)

* UTM module ignores URLs inside code fences

## 0.0.9 (2022-11-15)

* Moving image files after rendering a post will also move `.gif` files

## 0.0.8 (2022-11-08)

* Adds UTM CLI `python -m jupyblog.utm --help`

## 0.0.7 (2022-11-06)

* Extract images from outputs in paired notebooks
* Skipping image paths when adding UTM tags
* Rendering plain text outputs from notebooks with the `txt` tag

## 0.0.6 (2022-11-05)

* Adds support for adding UTM tags to links

## 0.0.5 (2022-08-30)

* Updates telemetry key

## 0.0.4 (2022-08-13)

* Adds telemetry

## 0.0.3 (2022-04-16)

* Increases timeout for jupyter executor
* Creates subclass of ClickException, raised when H1 headers appear
* Custom error when missing keys in front matter
* Validating `jupyblog` front matter section
* Adds support for front matter template
* Footer template is optional
* Adds more arguments for custom postprocessor for greater flexibility

## 0.0.2 (2022-01-24)

* `jupyblog.yaml` can be used for config
* Removes `--hugo` option, replaces it with `--local`
* Fixes img tag parser to allow dots, underscores, and spaces
* Adds language_mapping to `jupyblog.yaml`
* Adds option to switch config file
* Adds image_placeholders config option
* Adds `MarkdownAST`, `GistUploader`, and `config.postprocessor`
* Adds `config.processor`

## 0.0.1 (2021-10-13)

* First public release
