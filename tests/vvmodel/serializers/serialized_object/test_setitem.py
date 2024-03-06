import pytest

from vvmodel.serializers import SerializedObject


@pytest.fixture
def serialized_object():
    return SerializedObject()


def test_permite_solo_claves_consistentes_con_objeto_serializado(serialized_object):
    with pytest.raises(KeyError):
        serialized_object["clave_cualquiera"] = "valor"


def test_no_da_error_si_la_clave_esta_entre_las_permitidas(serialized_object):
    # No debe dar error
    serialized_object["model"] = "tests.mitestmodel"
    serialized_object["pk"] = 1
    serialized_object["fields"] = {"field1": "val1", "field2": "val2"}


def test_tipo_del_valor_de_clave_pk_debe_ser_int(serialized_object):
    with pytest.raises(ValueError):
        serialized_object["pk"] = "casa"


def test_tipo_del_valor_de_clave_fields_debe_ser_dict(serialized_object):
    with pytest.raises(ValueError):
        serialized_object["fields"] = "campos"


def test_tipo_del_valor_de_clave_model_debe_ser_str(serialized_object):
    with pytest.raises(ValueError):
        serialized_object["model"] = 2


def test_contenido_del_valor_de_clave_model_debe_ser_app_y_un_modelo_de_la_misma(serialized_object):
    with pytest.raises(ValueError):
        serialized_object["model"] = "clavecualquiera"

    serialized_object["model"] = "tests.mitestrelatedmodel"   # No debe dar error
