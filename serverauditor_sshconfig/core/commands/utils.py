# -*- coding: utf-8 -*-
"""Module tool heplers to parse command lines."""


# pylint: disable=no-self-use
def parse_ids_names(ids__names):
    """Parse ids__models list."""
    ids = [int(i) for i in ids__names if i.isdigit()]
    return ids, ids__names
