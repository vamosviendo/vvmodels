from __future__ import annotations

from collections import UserDict, UserList
from typing import Any

from django.apps import apps


serializedobjectvalue = str | int | dict[str: Any]


def validate_app(app: str) -> str:
    if app in apps.all_models.keys():
        return app
    raise ValueError(f'App "{app}" inexistente')


def validate_app_model(app: str, model: str):
    if model in apps.all_models[app].keys():
        return model
    raise ValueError(f'Modelo "{model}" inexistente en app "{app}"')


class SerializedObject(UserDict):

    def __setitem__(self, key: str, value: serializedobjectvalue):
        key, value = self._validate(key, value)
        super().__setitem__(key, value)

    def _validate(self, key: str, value: serializedobjectvalue) -> tuple[str, serializedobjectvalue]:
        if key == "model":
            return key, self._validate_model(value)
        if key == "pk":
            return key, self._validate_pk(value)
        if key == "fields":
            return key, self._validate_fields(value)
        raise KeyError(
            f'Clave "{key}" no se encuentra entre las claves admitidas para SerializedObject')

    @staticmethod
    def _validate_model(model: str) -> str:
        if type(model) is str:
            try:
                app, model = model.split('.')
            except ValueError:
                raise ValueError(f'Valor "{model}" no responde a estructura correcta "<app>.<model>"')
            return f"{validate_app(app)}.{validate_app_model(app, model)}"

        raise TypeError(f'Tipo de valor "{model}" de clave "model" erróneo. Debe ser str')

    @staticmethod
    def _validate_pk(pk: int) -> int:
        if type(pk) is int:
            return pk
        raise TypeError(f'Tipo de valor "{pk}" de clave "pk" erróneo. Debe ser int')

    @staticmethod
    def _validate_fields(fields: dict[str, Any]):
        if isinstance(fields, dict):
            return fields
        raise TypeError(f'Tipo de valor "{fields}" de clave "fields" erróneo. Debe ser dict')


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

    def filter_by_model(self, app: str, model: str) -> SerializedDb:
        return SerializedDb([
            x for x in self
            if x["model"] == f"{validate_app(app)}."
                             f"{validate_app_model(app, model)}"
        ])
