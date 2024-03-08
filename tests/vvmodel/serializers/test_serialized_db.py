import json
from io import StringIO

import pytest

from django.core.management import call_command

from vvmodel.serializers import SerializedDb, SerializedObject
from vvmodel.tests.models import MiTestRelatedModel, MiTestModel, MiTestPolymorphModel


@pytest.fixture
def serialized_db(
        miobjeto: MiTestRelatedModel,
        miotroobjeto: MiTestRelatedModel,
        miobjetocomplejo: MiTestModel,
        miobjetopolimorfico: MiTestPolymorphModel) -> SerializedDb:
    serialization = StringIO()
    call_command('dumpdata', indent=2, stdout=serialization)
    return SerializedDb(
        [SerializedObject(x) for x in json.loads(serialization.getvalue())]
    )


class TestUpdateOrAppendElements:

    def test_todos_sus_elementos_son_instancias_de_serializedobject(self):
        with pytest.raises(TypeError):
            serialized_db = SerializedDb([1, 2, 3])
        serialized_db = SerializedDb([SerializedObject(), SerializedObject()])  # No debe dar error

    def test_no_admite_que_se_asignen_elementos_que_no_sean_instancias_de_serializedobject(self):
        serialized_db = SerializedDb([SerializedObject()])
        with pytest.raises(TypeError):
            serialized_db[0] = 2
        serialized_db[0] = SerializedObject()   # No debe dar error

    def test_no_admite_que_se_agreguen_elementos_que_no_sean_instancias_de_serializedobject(self):
        serialized_db = SerializedDb()
        with pytest.raises(TypeError):
            serialized_db.append(2)
        serialized_db.append(SerializedObject())    # No debe dar error

    def test_no_admite_que_se_inserten_elementos_que_no_sean_instancias_de_serializedobject(self):
        serialized_db = SerializedDb([SerializedObject(), SerializedObject()])
        with pytest.raises(TypeError):
            serialized_db.insert(1, "a")
        serialized_db.insert(1, SerializedObject())     # No debe dar error

    def test_no_admite_extender_con_listas_que_contengan_elementos_que_no_sean_serializedobject(self):
        serialized_db = SerializedDb([SerializedObject()])
        lista = [SerializedObject(), 2, SerializedObject()]
        with pytest.raises(TypeError):
            serialized_db.extend(lista)
        serialized_db.extend([x for x in lista if isinstance(x, SerializedObject)])     # No debe dar error


class TestModel:

    def test_devuelve_serializeddb_con_todos_los_elementos_de_un_modelo_dado(
            self, serialized_db):
        serialized_model = serialized_db.filter_by_model("tests", "mitestrelatedmodel")
        assert isinstance(serialized_model, SerializedDb)
        assert len(serialized_model) > 0
        for obj in serialized_model:
            assert obj["model"] == "tests.mitestrelatedmodel"

    def test_da_valueerror_si_recibe_app_no_registrada(self, serialized_db):
        with pytest.raises(
                ValueError,
                match='App "appinexistente" inexistente'
        ):
            serialized_db.filter_by_model("appinexistente", "mitestrelatedmodel")

    def test_da_valueerror_si_recibe_modelo_inexistente_en_app(self, serialized_db):
        with pytest.raises(
                ValueError,
                match='Modelo "modeloinexistente" inexistente en app "tests"'
        ):
            serialized_db.filter_by_model("tests", "modeloinexistente")
