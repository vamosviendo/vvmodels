from __future__ import annotations

import json
from collections import UserDict, UserList
from typing import Any, TextIO, Self

from django.apps import apps
from django.core.exceptions import ValidationError

serializedobjectvalue: type = str | int | dict[str: Any]


def _validate_app(app: str) -> str:
    if app in apps.all_models.keys():
        return app
    raise ValueError(f'App "{app}" inexistente')


def _validate_app_model(app: str, model: str) -> str:
    if model in apps.all_models[app].keys():
        return model
    raise ValueError(f'Modelo "{model}" inexistente en app "{app}"')

def _validate_app_and_model(model: str) -> str:
    app, app_model = model.split(".")
    _validate_app(app)
    _validate_app_model(app, app_model)
    return model


class SerializedObject(UserDict):

    @classmethod
    def model_string(cls):
        """ En subclases de SerializedObject, debe ser implementada para que
            devuelva la cadena "app.model" correspondiente al modelo
            representado
        """
        raise NotImplementedError('Método "model_string" no implementado')

    def __init__(self, dict: dict | SerializedObject = None, /, container: SerializedDb = None, **kwargs):
        super().__init__(dict, **kwargs)
        self.container = container
        if container is None:
            if isinstance(dict, SerializedObject):
                self.container = dict.container

    @classmethod
    def primere(cls, container: SerializedDb, **kwargs) -> Self | None:
        result = container.primere(cls.model_string(), **kwargs)
        return cls(result) or None

    def __setitem__(self, key: str, value: serializedobjectvalue):
        key, value = self._validate(key, value)
        super().__setitem__(key, value)

    @property
    def model(self) -> str:
        return self['model']

    @model.setter
    def model(self, value: str):
        self['model'] = value

    @property
    def pk(self) -> int:
        return self['pk']

    @pk.setter
    def pk(self, value: int):
        self['pk'] = value

    @property
    def fields(self) -> dict[str, Any]:
        return self['fields']

    @fields.setter
    def fields(self, value: dict[str, Any]):
        self['fields'] = value

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
                app, app_model = model.split('.')
            except ValueError:
                raise ValueError(f'Valor "{model}" no responde a estructura correcta "<app>.<model>"')
            return f"{_validate_app(app)}.{_validate_app_model(app, app_model)}"

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

    def filter_by_model(self, model: str) -> SerializedDb:
        return SerializedDb([
            x for x in self
            if x["model"] == _validate_app_and_model(model)
        ])

    def primere(self, model: str, **kwargs) -> SerializedObject | None:
        try:
            return self.tomar(model=model, **kwargs)
        except StopIteration:
            return None

    def tomar(self, **kwargs) -> SerializedObject:
        # Validar argumentos: Si se pasa "pk", debe pasarse "model".
        if "pk" in kwargs.keys() and "model" not in kwargs.keys():
            raise ValidationError(
                'Si se pasa argumento "pk", debe estar presente el argumento "model"'
            )

        def all_kwargs_present(x: SerializedObject, **_kwargs) -> bool:
            result = True
            for key, value in _kwargs.items():
                result = (x.pk == value) if key == "pk" \
                    else (x.model == value) if key == "model" \
                    else (x.fields[key] == value)
                if result is False:
                    break
            return result

        return next(x for x in self if all_kwargs_present(x, **kwargs))

    @staticmethod
    def _validate(item: SerializedObject) -> SerializedObject:
        if isinstance(item, SerializedObject):
            return item
        raise TypeError


def load_serialized_filename(archivo: str) -> SerializedDb:
    with open(archivo, 'r') as db:
        return load_serialized_file(db)


def load_serialized_file(archivo: TextIO) -> SerializedDb:
    serialized_db = SerializedDb()
    for obj in json.load(archivo):
        serialized_db.append(SerializedObject(obj, container=serialized_db))
    return serialized_db
