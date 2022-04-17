from click.exceptions import ClickException


class InvalidFrontMatter(ValueError):
    pass


class InputPostException(ClickException):
    pass
