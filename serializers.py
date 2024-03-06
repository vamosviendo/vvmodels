from collections import UserDict


class SerializedObject(UserDict):

    def __setitem__(self, key, value):
        key, value = self._validate(key, value)
        super().__setitem__(key, value)

    @staticmethod
    def _validate(key, value):
        if key == "model":
            return key, value
        if key == "pk":
            if type(value) is int:
                return key, value
            raise ValueError(value)
        if key == "fields":
            if isinstance(value, dict):
                return key, value
            raise ValueError(value)

        raise KeyError(key)
