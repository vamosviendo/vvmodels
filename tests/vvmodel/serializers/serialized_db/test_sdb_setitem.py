import pytest

from vvmodel.serializers import SerializedDb, SerializedObject


def test_no_admite_elementos_que_no_sean_instancias_de_serializedobject():
    serialized_db = SerializedDb([SerializedObject()])
    with pytest.raises(TypeError):
        serialized_db[0] = 2
