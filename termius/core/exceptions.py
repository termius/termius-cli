# -*- coding: utf-8 -*-
"""Module for application exceptions."""


class TermiusException(Exception):
    """Base exception class."""


class DoesNotExistException(TermiusException):
    """Raise it when model can not be found in storage."""


class TooManyEntriesException(TermiusException):
    """Raise it when there are more models then you think."""


class ArgumentRequiredException(ValueError):
    """Raise it when one of required CLI argument is missed."""


class InvalidArgumentException(ValueError):
    """Raise it when CLI argument have invalid value."""


class SkipField(TermiusException):
    """Raise it when needs to skip field."""


class OptionNotSetException(TermiusException):
    """Raise it when no option in section."""


class AuthyTokenIssue(TermiusException):
    """Raise it when API error caused by `authy_token`."""
