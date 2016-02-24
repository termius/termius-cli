# -*- coding: utf-8 -*-
"""Module with mixins for transformers."""


# pylint: disable=too-few-public-methods
class CryptoChildTransformerCreatorMixin(object):
    """Add method to create new crypto controller."""

    def create_child_transformer(self, model_class):
        """Generate specific set transformer."""
        return self.child_transformer_class(
            model_class=model_class, storage=self.storage,
            crypto_controller=self.crypto_controller,
            account_manager=self.account_manager
        )
