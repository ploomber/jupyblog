# CHANGELOG

## 0.0.6dev
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
