from __future__ import annotations

from collections import UserDict, UserList
from typing import Any

from django.apps import apps


serializedobjectvalue = str | int | dict[str: Any]


class SerializedObject(UserDict):

    def __setitem__(self, key: str, value: serializedobjectvalue):
        key, value = self._validate(key, value)
        super().__setitem__(key, value)

    @staticmethod
    def _validate(key: str, value: serializedobjectvalue) -> tuple[str, serializedobjectvalue]:
        if key == "model":
            if type(value) is str:
                try:
                    app, model = value.split('.')
                except ValueError:
                    app, model = value, ""
                if app in apps.all_models.keys() and model in apps.all_models[app].keys():
                    return key, value
                raise ValueError(f'Valor "{value}" no responde a estructura correcta "<app>.<model>"')
            raise TypeError(f'Tipo de valor "{value}" de clave "{key}" erróneo. Debe ser str')
        if key == "pk":
            tipo = type(value)
            if tipo is int:
                return key, value
            raise TypeError(f'Tipo de valor "{value}" de clave "{key}" erróneo. Debe ser int')
        if key == "fields":
            if isinstance(value, dict):
                return key, value
            raise TypeError(f'Tipo de valor "{value}" de clave "{key}" erróneo. Debe ser dict')

        raise KeyError(
            f'Clave "{key}" no se encuentra entre las claves admitidas para SerializedObject')


class SerializedDb(UserList):

    def __init__(self, initlist: list[SerializedObject] = None):
        initlist = map(self._validate, initlist) if initlist else None
        super().__init__(initlist)

    def __setitem__(self, index: int, item: SerializedObject):
        self.data[index] = self._validate(item)

    def append(self, item: SerializedObject):
        self.data.append(self._validate(item))

    def insert(self, index: int, item: SerializedObject):
        self.data.insert(index, self._validate(item))

    def extend(self, other: list[SerializedObject]):
        if isinstance(other, type(self)):
            self.data.extend(other)
        else:
            self.data.extend(self._validate(item) for item in other)

    @staticmethod
    def _validate(item: SerializedObject) -> SerializedObject:
        if isinstance(item, SerializedObject):
            return item
        raise TypeError
