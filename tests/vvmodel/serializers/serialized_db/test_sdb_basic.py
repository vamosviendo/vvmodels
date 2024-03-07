from collections import UserList

import pytest

from vvmodel.serializers import SerializedDb


def test_es_subclase_de_userlist():
    serialized_db = SerializedDb()
    assert isinstance(serialized_db, UserList)


def test_todos_sus_elementos_son_instancias_de_serializedobject():
    with pytest.raises(TypeError):
        serialized_db = SerializedDb([1, 2, 3])
