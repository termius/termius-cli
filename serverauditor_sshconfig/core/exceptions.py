# -*- coding: utf-8 -*-
"""Module for application exceptions."""


class DoesNotExistException(Exception):
    """Raise it when model can not be found in storage."""

    pass


class TooManyEntriesException(Exception):
    """Raise it when there are more models then you think."""

    pass


class ArgumentRequiredException(ValueError):
    """Raise it when one of required CLI argument is missed."""

    pass


class InvalidArgumentException(ValueError):
    """Raise it when CLI argument have invalid value."""

    pass


class SkipField(Exception):
    """Raise it when needs to skip field."""

    pass
