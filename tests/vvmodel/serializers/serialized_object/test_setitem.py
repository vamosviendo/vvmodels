import pytest

from vvmodel.serializers import SerializedObject


def test_permite_solo_claves_consistentes_con_objeto_serializado():
    serialized_object = SerializedObject()
    with pytest.raises(KeyError):
        serialized_object["clave_cualquiera"] = "valor"


def test_no_da_error_si_la_clave_esta_entre_las_permitidas():
    serialized_object = SerializedObject()
    # No debe dar error
    serialized_object["model"] = "vvmodel.mimodel"
    serialized_object["pk"] = 1
    serialized_object["fields"] = {"field1": "val1", "field2": "val2"}


def test_valor_de_clave_pk_debe_ser_int():
    serialized_object = SerializedObject()
    with pytest.raises(ValueError):
        serialized_object["pk"] = "casa"


def test_valor_de_clave_fields_debe_ser_dict():
    serialized_object = SerializedObject()
    with pytest.raises(ValueError):
        serialized_object["fields"] = "campos"
