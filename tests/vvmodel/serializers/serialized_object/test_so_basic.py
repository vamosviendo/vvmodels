from collections import UserDict

import pytest

from vvmodel.serializers import SerializedObject


def test_es_subclase_de_userdict():
    serialized_object = SerializedObject()
    assert isinstance(serialized_object, UserDict)


def test_no_admite_claves_no_consistentes_con_objeto_serializado():
    with pytest.raises(KeyError):
        serialized_object = SerializedObject(clave_cualquiera="valor")
