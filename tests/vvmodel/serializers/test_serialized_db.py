import pytest

from vvmodel.serializers import SerializedDb, SerializedObject


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


class TestFilterByModel:

    def test_devuelve_serializeddb_con_todos_los_elementos_de_un_modelo_dado(
            self, serialized_db):
        serialized_model = serialized_db.filter_by_model("tests.mitestrelatedmodel")
        assert isinstance(serialized_model, SerializedDb)
        assert len(serialized_model) > 0
        for obj in serialized_model:
            assert obj["model"] == "tests.mitestrelatedmodel"

    def test_da_valueerror_si_recibe_app_no_registrada(self, serialized_db):
        with pytest.raises(
                ValueError,
                match='App "appinexistente" inexistente'
        ):
            serialized_db.filter_by_model("appinexistente.mitestrelatedmodel")

    def test_da_valueerror_si_recibe_modelo_inexistente_en_app(self, serialized_db):
        with pytest.raises(
                ValueError,
                match='Modelo "modeloinexistente" inexistente en app "tests"'
        ):
            serialized_db.filter_by_model("tests.modeloinexistente")


class TestPrimere:
    def test_devuelve_el_primer_elemento_del_modelo_dado_en_el_que_el_valor_del_campo_coincide_con_el_argumento(
            self, serialized_db):
        assert \
            serialized_db.primere("tests.mitestrelatedmodel", nombre="miotroobjeto") == \
            next(
                x for x in serialized_db.filter_by_model(
                    "tests.mitestrelatedmodel"
                ) if x.fields["nombre"] == "miotroobjeto"
            )

    def test_puede_manejar_mas_de_un_argumento(self, serialized_db):
        assert serialized_db.primere(
            "tests.mitestmodel", numero=5.0, nombre="miotroobjetocompleto"
        ) == next(
            x for x in serialized_db.filter_by_model(
                "tests.mitestmodel"
            ) if x.fields["nombre"] == "miotroobjetocompleto" and x.fields["numero"] == 5.0
        )

    def test_si_no_encuentra_elemento_con_todos_los_argumentos_devuelve_None(self, serialized_db):
        assert serialized_db.primere(
                "tests.mitestmodel", nombre="miotroobjetocompleto", numero=6.0
        ) is None

    def test_si_el_argumento_es_pk_busca_la_clave_primaria_y_no_un_campo(self, serialized_db):
        for obj in serialized_db.filter_by_model("tests.mitestmodel"):
            obj.fields.update({'pk': 5 if obj.pk == 1 else 1})
        assert serialized_db.primere(
            "tests.mitestmodel", pk=1
        ) == next(
            x for x in serialized_db.filter_by_model("tests.mitestmodel")
            if x.pk == 1
        )

    def test_si_recibe_pk_que_coincide_junto_con_campo_que_no_coincide_devuelve_None(self, serialized_db):
        assert serialized_db.primere("tests.mitestmodel", pk=2, nombre="objeto inexistente") is None

    def test_si_recibe_campo_que_coincide_junto_con_pk_que_no_coincide_devuelve_None(self, serialized_db):
        assert serialized_db.primere("tests.mitestmodel", pk=5, nombre="mitestmodel") is None

    def test_si_no_se_pasan_otros_argumentos_devuelve_el_primer_elemento_del_modelo_dado(self, serialized_db):
        assert \
            serialized_db.primere("tests.mitestrelatedmodel") == \
            next(
                x for x in serialized_db.filter_by_model(
                    "tests.mitestrelatedmodel"
                )
            )

    def test_devuelve_none_si_no_se_encuentra_el_elemento_solicitado(self, serialized_db):
        db_sin_model = SerializedDb([x for x in serialized_db if x.model != "tests.mitestrelatedmodel"])
        assert db_sin_model.primere("tests.mitestrelatedmodel") is None
