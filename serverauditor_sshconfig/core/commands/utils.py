# -*- coding: utf-8 -*-
# pylint: disable=no-self-use
def parse_ids_names(self, ids__names):
    """Parse ids__models list."""
    ids = [int(i) for i in ids__names if i.isdigit()]
    return ids, ids__names
