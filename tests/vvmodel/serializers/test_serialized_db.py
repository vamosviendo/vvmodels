from collections import UserList

import pytest

from vvmodel.serializers import SerializedDb, SerializedObject


def test_es_subclase_de_userlist():
    serialized_db = SerializedDb()
    assert isinstance(serialized_db, UserList)


def test_todos_sus_elementos_son_instancias_de_serializedobject():
    with pytest.raises(TypeError):
        serialized_db = SerializedDb([1, 2, 3])


def test_no_admite_elementos_que_no_sean_instancias_de_serializedobject():
    serialized_db = SerializedDb([SerializedObject()])
    with pytest.raises(TypeError):
        serialized_db[0] = 2
