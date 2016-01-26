from .serializers import BulkSerializer
from ..core.api import API


class CryptoController(object):

    def __init__(self, cryptor):
        self.cryptor = cryptor

    def _mutate_fields(self, model, mutator):
        for i in model.crypto_fields:
            crypto_field = getattr(model, i)
            if crypto_field:
                setattr(model, i, mutator(crypto_field))
        return model

    def encrypt(self, model):
        return self._mutate_fields(model, self.cryptor.encrypt)

    def decrypt(self, model):
        return self._mutate_fields(model, self.cryptor.decrypt)


class ApiController(object):

    mapping = dict(
        bulk=dict(url='v2/terminal/bulk/', serializer=BulkSerializer)
    )

    def __init__(self, storage, config, cryptor):
        self.config = config
        username = self.config.get('User', 'username')
        apikey = self.config.get('User', 'apikey')
        assert username
        assert apikey
        self.api = API(username, apikey)
        self.storage = storage
        self.crypto_controller = CryptoController(cryptor)

    def _get(self, mapped):
        serializer = mapped['serializer'](
            storage=self.storage, crypto_controller=self.crypto_controller
        )
        response = self.api.get(mapped['url'])

        model = serializer.to_model(response)
        return model

    def get_bulk(self):
        mapped = self.mapping['bulk']
        model = self._get(mapped)
        self.config.set('CloudSynchronization', 'last_synced',
                        model['last_synced'])
        self.config.write()

    def _post(self, mapped, request_model):
        request_model = request_model
        serializer = mapped['serializer'](
            storage=self.storage, crypto_controller=self.crypto_controller
        )

        payload = serializer.to_payload(request_model)
        response = self.api.post(mapped['url'], payload)

        response_model = serializer.to_model(response)
        return response_model

    def post_bulk(self):
        mapped = self.mapping['bulk']
        model = {}
        model['last_synced'] = self.config.get(
            'CloudSynchronization', 'last_synced'
        )
        assert model['last_synced']
        out_model = self._post(mapped, model)
        self.config.set('CloudSynchronization', 'last_synced',
                        out_model['last_synced'])
        self.config.write()
