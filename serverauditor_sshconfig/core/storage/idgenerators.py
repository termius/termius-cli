from uuid import uuid4


class UUIDGenerator(object):

    def __init__(self, storage):
        """Contruct IDGenerator.

        :param ApplicationStorage storage: Storage instance
        """

    def __call__(self, model):
        """Generate id.

        :param core.models.Model model: generate and set id for this Model.
        """
        assert not getattr(model, model.id_name)
        identificator = uuid4().time_low
        setattr(model, model.id_name, identificator)
        return identificator
