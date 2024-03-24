import pytest

from vvmodel.serializers import SerializedObject
from vvmodel.tests.serializers import SerializedMiTestModel


@pytest.fixture
def serialized_object():
    return SerializedObject(
        model="tests.mitestpolymorphmodel",
        pk=1,
        fields={"nombre": "nombre", "número": 15}
    )


class TestValidation:

    def test_no_admite_claves_no_consistentes_con_objeto_serializado(self):
        with pytest.raises(KeyError):
            serialized_object = SerializedObject(clave_cualquiera="valor")

    def test_permite_solo_claves_consistentes_con_objeto_serializado(self, serialized_object):
        with pytest.raises(
                KeyError,
                match='Clave "clave_cualquiera" no se encuentra entre las claves admitidas para SerializedObject'):
            serialized_object["clave_cualquiera"] = "valor"

    def test_no_da_error_si_la_clave_esta_entre_las_permitidas(self, serialized_object):
        # No debe dar error
        serialized_object["model"] = "tests.mitestmodel"
        serialized_object["pk"] = 1
        serialized_object["fields"] = {"field1": "val1", "field2": "val2"}

    def test_tipo_del_valor_de_clave_pk_debe_ser_int(self, serialized_object):
        with pytest.raises(
                TypeError,
                match='Tipo de valor "casa" de clave "pk" erróneo. Debe ser int'):
            serialized_object["pk"] = "casa"

    def test_tipo_del_valor_de_clave_fields_debe_ser_dict(self, serialized_object):
        with pytest.raises(
                TypeError,
                match='Tipo de valor "campos" de clave "fields" erróneo. Debe ser dict'):
            serialized_object["fields"] = "campos"

    def test_tipo_del_valor_de_clave_model_debe_ser_str(self, serialized_object):
        with pytest.raises(
                TypeError,
                match='Tipo de valor "2" de clave "model" erróneo. Debe ser str'):
            serialized_object["model"] = 2

    def test_contenido_del_valor_de_clave_model_debe_ser_app_y_un_modelo_de_la_misma(self, serialized_object):
        with pytest.raises(
                ValueError,
                match='Valor "clavecualquiera" no responde a estructura correcta "<app>.<model>"'):
            serialized_object["model"] = "clavecualquiera"

        serialized_object["model"] = "tests.mitestrelatedmodel"   # No debe dar error


class TestProperties:

    @pytest.mark.parametrize("prop", ["pk", "model", "fields"])
    def test_devuelve_valor_de_clave_correspondiente(self, serialized_object, prop):
        assert getattr(serialized_object, prop) == serialized_object[prop]

    @pytest.mark.parametrize("prop, value", [
        ("pk", 2),
        ("model", "tests.mitestrelatedmodel"),
        ("fields", {"nombre": "Juancho", "numero": 15})])
    def test_asigna_valor_a_clave_correspondiente(self, serialized_object, prop, value):
        setattr(serialized_object, prop, value)
        assert serialized_object[prop] == value


class TestContainer:

    def test_guarda_referencia_a_SerializedDb_de_la_que_forma_parte_el_objeto(self, serialized_db):
        for object in serialized_db:
            assert object.container == serialized_db

    def test_si_el_objeto_no_forma_parte_de_una_SerializedDb_es_None(self, serialized_object):
        assert serialized_object.container is None

    def test_toma_container_de_argumento_dict_si_dict_es_un_SerializedObject_y_container_es_None(self, serialized_db):
        assert SerializedObject(serialized_db[0]).container == serialized_db[0].container

    def test_toma_container_de_argumento_container_si_no_es_None_aunque_dict_sea_un_SerializedObject(self, serialized_db):
        serialized_model = serialized_db.filter_by_model("tests.mitestrelatedmodel")
        serialized_object = SerializedObject(serialized_db[0], container=serialized_model)
        assert serialized_object.container != serialized_db[0].container
        assert serialized_object.container == serialized_model


class TestModelStr:
    def test_da_error_de_no_implementacion_en_SerializedObject(self):
        with pytest.raises(NotImplementedError, match='Método "model_string" no implementado'):
            SerializedObject.model_string()

    def test_da_error_de_no_implementacion_si_no_se_redefine_en_subclases_de_SerializedObject(self):
        class SerializedSubObject(SerializedObject): pass
        with pytest.raises(NotImplementedError, match='Método "model_string" no implementado'):
            SerializedSubObject.model_string()

    def test_no_da_error_si_se_la_redefine_en_la_subclase(self):
        assert SerializedMiTestModel.model_string() == "tests.mitestmodel"

class TestPrimere:
    def test_devuelve_primer_objeto_del_modelo_de_la_clase_en_una_SerializedDb_dada(self, serialized_db):
        assert SerializedMiTestModel.primere(serialized_db) == serialized_db.primere("tests.mitestmodel")

    def test_en_clases_que_heredan_de_SerializedObject_objeto_devuelto_es_de_la_subclase_correcta(self, serialized_db):
        assert type(SerializedMiTestModel.primere(serialized_db)) is SerializedMiTestModel

    def test_da_error_de_no_implementacion_si_se_la_llama_en_SerializedObject(self, serialized_db):
        with pytest.raises(NotImplementedError):
            SerializedObject.primere(serialized_db)

    def test_da_error_de_no_implementacion_si_no_esta_implementado_el_metodo_model_str_en_la_subclase_de_SerializedObject(self, serialized_db):
        class SerializedSubObject(SerializedObject): pass
        with pytest.raises(NotImplementedError):
            SerializedSubObject.primere(serialized_db)

    def test_busca_campos_si_se_pasan_argumentos_con_clave(self, serialized_db):
        assert \
            SerializedMiTestModel.primere(serialized_db, nombre="miobjetocompleto") == \
            serialized_db.primere(SerializedMiTestModel.model_string(), nombre="miobjetocompleto")

    def test_devuelve_none_si_no_encuentra_argumento_con_clave(self, serialized_db):
        assert \
            SerializedMiTestModel.primere(serialized_db, nombre="nombreinexistente") is None
