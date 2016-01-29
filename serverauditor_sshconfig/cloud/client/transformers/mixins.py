# -*- coding: utf-8 -*-
"""Module with mixins for transformers."""


# pylint: disable=too-few-public-methods
class CryptoChildSerializerCreatorMixin(object):
    """Add method to create new crypto controller."""

    def create_child_serializer(self, model_class):
        """Generate specific set serializer."""
        return self.child_serializer_class(
            model_class=model_class, storage=self.storage,
            crypto_controller=self.crypto_controller
        )
