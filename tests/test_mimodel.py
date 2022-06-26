import datetime
from unittest.mock import patch, MagicMock

from django.db.models import QuerySet

from .models import MiTestModel, MiTestRelatedModel, MiTestPolymorphModel, \
    MiTestPolymorphSubmodel, MiTestPolymorphSubSubModel

from django.test import TestCase


class TestMiModel(TestCase):

    def setUp(self):
        super().setUp()
        self.ro = MiTestRelatedModel.objects.create(nombre='related object')
        self.o1 = MiTestModel.objects.create(
            nombre='obj1', numero=10.0, related=self.ro)
        self.o2 = MiTestModel.objects.create(
            nombre='obj2', numero=25.5, related=self.ro)


class TestMiModelMetodos(TestMiModel):

    def test_todes_devuelve_todos_los_objetos(self):
        self.assertEqual(
            list(MiTestModel.todes()),
            list(MiTestModel.objects.all())
        )

    def test_todes_devuelve_QuerySet(self):
        self.assertIsInstance(MiTestModel.todes(), QuerySet)

    def test_primere_devuelve_primer_objeto(self):
        self.assertEqual(MiTestModel.primere(), self.o1)

    def test_ultime_devuelve_ultimo_objeto(self):
        self.assertEqual(MiTestModel.ultime(), self.o2)

    def test_tomar_devuelve_objeto_indicado(self):
        self.assertEqual(MiTestModel.tomar(nombre='obj2'), self.o2)

    def test_cantidad_devuelve_cantidad_de_objetos(self):
        self.assertEqual(MiTestModel.cantidad(), 2)

    def test_excepto_devuelve_todos_los_objetos_excepto_uno(self):
        self.assertEqual(list(MiTestModel.excepto(pk=self.o1.pk)), [self.o2])

    def test_filtro_devuelve_todos_los_objetos_que_coincidan(self):
        o3 = MiTestModel.objects.create(
            nombre='obj3', numero=10.0, related=self.ro
        )
        self.assertEqual(list(MiTestModel.filtro(numero=10.0)), [self.o1, o3])


class TestMiModelCrear(TestMiModel):

    def test_crea_objeto(self):
        MiTestModel.crear(
            nombre='obj3', numero=10.0, related=self.ro
        )
        self.assertEqual(MiTestModel.cantidad(), 3)

    def test_devuelve_objeto(self):
        obj3 = MiTestModel.crear(
            nombre='obj3', numero=10.0, related=self.ro
        )
        self.assertEqual(obj3.nombre, 'obj3')
        self.assertEqual(obj3.numero, 10.0)
        self.assertEqual(obj3.related, self.ro)

    @patch('vvmodel.tests.models.MiTestModel.full_clean')
    def test_verifica_objeto(self, falso_full_clean):
        MiTestModel.crear(
            nombre='obj3', numero=10.0, related=self.ro
        )
        falso_full_clean.assert_called_once()

    @patch('vvmodel.tests.models.MiTestModel.save')
    def test_guarda_objeto(self, falso_save):
        MiTestModel.crear(
            nombre='obj3', numero=10.0, related=self.ro
        )
        falso_save.assert_called_once()


class TestMetodoTomarONada(TestCase):

    def test_devuelve_objeto_si_existe(self):
        objeto = MiTestRelatedModel.crear(nombre='objeto existente')
        self.assertEqual(
            MiTestRelatedModel.tomar_o_nada(nombre='objeto existente'),
            objeto
        )

    def test_devuelve_none_si_objeto_no_existe(self):
        self.assertIsNone(
            MiTestRelatedModel.tomar_o_nada(nombre='objeto inexistente')
        )


class TestMiModelUpdateFrom(TestMiModel):

    def test_actualiza_objeto_existente_a_partir_de_objeto_del_mismo_tipo(self):
        ro2 = MiTestRelatedModel.crear(nombre='ro2')
        o3 = MiTestModel(
                nombre='nuevo nombre',
                numero=567,
                fecha=datetime.date(2020, 2, 2),
                related=ro2
            )
        self.o1.update_from(o3)
        self.o1.refresh_from_db()

        self.assertEqual(self.o1.nombre, 'nuevo nombre')
        self.assertEqual(self.o1.numero, 567)
        self.assertEqual(self.o1.fecha, datetime.date(2020, 2, 2))
        self.assertEqual(self.o1.related, ro2)

    def test_no_guarda_objeto_actualizado_con_commit_false(self):
        ro2 = MiTestRelatedModel.crear(nombre='ro2')
        o3 = MiTestModel(
                nombre='nuevo nombre',
                numero=567,
                fecha=datetime.date(2020, 2, 2),
                related=ro2
            )
        self.o1.update_from(o3, commit=False)
        self.o1.refresh_from_db()
        self.assertEqual(self.o1.nombre, 'obj1')
        self.assertEqual(self.o1.numero, 10.0)
        self.assertEqual(self.o1.related, self.ro)

    def test_actualiza_objeto_aunque_no_lo_guarde_con_commit_false(self):
        ro2 = MiTestRelatedModel.crear(nombre='ro2')
        o3 = MiTestModel(
                nombre='nuevo nombre',
                numero=567,
                fecha=datetime.date(2020, 2, 2),
                related=ro2
            )
        self.o1.update_from(o3, commit=False)

        self.assertEqual(self.o1.nombre, 'nuevo nombre')
        self.assertEqual(self.o1.numero, 567)
        self.assertEqual(self.o1.fecha, datetime.date(2020, 2, 2))
        self.assertEqual(self.o1.related, ro2)

    def test_actualiza_solo_campos_pasados_como_argumento(self):
        o3 = MiTestModel(
                nombre='nuevo nombre',
            )
        self.o1.update_from(o3)
        self.o1.refresh_from_db()
        self.assertEqual(self.o1.nombre, 'nuevo nombre')
        self.assertEqual(self.o1.numero, 10.0)
        self.assertEqual(self.o1.related, self.ro)

    def test_devuelve_objeto_actualizado(self):
        ro2 = MiTestRelatedModel.crear(nombre='ro2')
        o3 = MiTestModel(
                nombre='nuevo nombre',
                numero=567,
                fecha=datetime.date(2020, 2, 2),
                related=ro2
            )
        updated_o1 = self.o1.update_from(o3, commit=False)

        self.assertEqual(updated_o1.nombre, o3.nombre)
        self.assertEqual(updated_o1.numero, o3.numero)
        self.assertEqual(updated_o1.fecha, o3.fecha)
        self.assertEqual(updated_o1.related, o3.related)


class TestGetClass(TestCase):

    def test_devuelve_la_clase_del_objeto(self):
        ro = MiTestRelatedModel.crear(nombre='ro2')
        o = MiTestModel(
                nombre='nuevo nombre',
                numero=567,
                fecha=datetime.date(2020, 2, 2),
                related=ro
            )
        self.assertEqual(ro.get_class(), MiTestRelatedModel)
        self.assertEqual(o.get_class(), MiTestModel)


class TestGetClassName(TestCase):

    def test_devuelve_una_cadena_con_el_nombre_de_la_clase_del_objeto(self):
        ro = MiTestRelatedModel.crear(nombre='ro2')
        o = MiTestModel(
                nombre='nuevo nombre',
                numero=567,
                fecha=datetime.date(2020, 2, 2),
                related=ro
            )
        clase = ro.get_class_name()
        clase2 = o.get_class_name()
        self.assertEqual(type(clase), str)
        self.assertEqual(clase, 'MiTestRelatedModel')
        self.assertEqual(clase2, 'MiTestModel')


class TestGetRelatedClass(TestCase):

    def test_devuelve_clase_del_modelo_relacionado_con_un_campo_foreign(self):
        self.assertEqual(
            MiTestModel.get_related_class('related'),
            MiTestRelatedModel
        )

    def test_devuelve_none_si_el_campo_no_es_foreign(self):
        self.assertIsNone(MiTestModel.get_related_class('nombre'))


class TestGetLowerClassName(TestCase):

    def test_devuelve_una_cadena_con_el_nombre_de_la_clase_en_minusculas(self):
        ro = MiTestRelatedModel.crear(nombre='ro2')
        clase = ro.get_lower_class_name()
        self.assertEqual(clase, ro.get_class_name().lower())


class TestTomarDeBd(TestCase):

    def test_devuelve_la_version_guardada_de_un_objeto(self):
        objeto = MiTestRelatedModel.crear(nombre='objeto guardado')
        obj_guardado = MiTestRelatedModel.tomar(nombre='objeto guardado')

        objeto.nombre = 'objeto modificado y no guardado'

        self.assertEqual(objeto.tomar_de_bd(), obj_guardado)

    def test_si_no_hay_version_guardada_de_un_objeto_devuelve_none(self):
        objeto = MiTestRelatedModel(nombre='objeto nuevo')
        self.assertIsNone(objeto.tomar_de_bd())


class TestGetMaxLength(TestCase):

    def test_devuelve_longitud_maxima_de_campo(self):
        self.assertEqual(MiTestModel.get_max_length('nombre'), 50)


class TestHasNotNoneAttr(TestCase):

    def test_devuelve_false_si_no_existe_el_atributo(self):
        instance = MiTestRelatedModel.crear(nombre='objeto sin atributo')
        self.assertFalse(instance.has_not_none_attr('cuadrado'))

    def test_devuelve_true_si_el_atributo_existe_y_no_es_none(self):
        instance = MiTestRelatedModel.crear(nombre='objeto sin atributo')
        instance.cuadrado = 'contenido'
        self.assertTrue(instance.has_not_none_attr('cuadrado'))

    def test_devuelve_false_si_el_atributo_es_none(self):
        instance = MiTestRelatedModel.crear(nombre='objeto sin atributo')
        instance.cuadrado = None
        self.assertFalse(instance.has_not_none_attr('cuadrado'))


class TestAnyFieldChanged(TestCase):

    def test_devuelve_false_si_ningun_campo_es_distinto_de_la_version_guardada(self):
        instance = MiTestRelatedModel.crear(nombre='objeto')
        self.assertFalse(instance.any_field_changed())

    def test_devuelve_true_si_algun_campo_es_distinto_de_la_version_guardada(self):
        instance = MiTestRelatedModel.crear(nombre='objeto')
        instance.nombre = 'ocjeto'
        self.assertTrue(instance.any_field_changed())


class TestEsLeMismeQue(TestCase):

    def setUp(self):
        self.obj = MiTestPolymorphModel.crear(nombre='objeto', numero=1)
        self.obj_sub = MiTestPolymorphSubmodel.crear(
            nombre='subobjeto', numero=2, detalle='cosas')

    def test_es_le_misme_que_devuelve_true_para_elementos_iguales_tomados_como_clases_distintas(self):
        obj = MiTestPolymorphModel.tomar(numero=2, polymorphic=False)
        obj_sub = MiTestPolymorphSubmodel.tomar(numero=2)

        self.assertTrue(obj_sub.es_le_misme_que(obj))
        self.assertTrue(obj.es_le_misme_que(obj_sub))

    def test_es_le_misme_que_devuelve_false_para_elementos_distintos_tomados_como_clases_distintas(self):
        obj = MiTestPolymorphModel.tomar(numero=2, polymorphic=False)
        obj_sub = MiTestPolymorphSubmodel.crear(
            nombre='subobjeto distinto', numero=3, detalle='detalle')

        self.assertFalse(obj_sub.es_le_misme_que(obj))

    def test_es_le_misme_que_devuelve_false_para_elementos_distintos_tomados_como_la_misma_clase(self):
        obj_s1 = MiTestPolymorphSubmodel.tomar(numero=2, polymorphic=False)
        obj_s2 = MiTestPolymorphSubmodel.crear(
            nombre='subobjeto distinto', numero=3, detalle='detalle')

        self.assertFalse(obj_s1.es_le_misme_que(obj_s2))

    def test_es_le_misme_que_devuelve_false_si_uno_de_los_objetos_no_esta_en_la_base_de_datos(self):
        obj = MiTestPolymorphModel(nombre='objeto', numero=1)
        subobj = MiTestPolymorphSubmodel(
            nombre='subobjeto', numero=2, detalle='cosas')

        self.assertFalse(self.obj.es_le_misme_que(obj))
        self.assertFalse(obj.es_le_misme_que(self.obj))
        self.assertFalse(self.obj_sub.es_le_misme_que(subobj))
        self.assertFalse(subobj.es_le_misme_que(self.obj_sub))

    def test_es_le_misme_que_devuelve_false_si_no_son_submodelos_del_mismo_modelo(self):
        mov = MiTestRelatedModel.crear(nombre='otro modelo')
        self.assertFalse(self.obj.es_le_misme_que(mov))


class TestPrimerAncestre(TestCase):

    def test_primer_ancestre_devuelve_el_primer_modelo_del_que_deriva_el_de_un_objeto(self):
        subsubobj = MiTestPolymorphSubSubModel(nombre='subsub', numero=3, detalle='cosas')
        self.assertEqual(subsubobj.primer_ancestre(), MiTestPolymorphModel)

    def test_primer_ancestre_devuelve_el_propio_modelo_si_no_tiene_ancestros(self):
        obj = MiTestPolymorphModel(nombre='test', numero=3)
        self.assertEqual(obj.primer_ancestre(), MiTestPolymorphModel)


@patch('vvmodel.models.MiModel.es_le_misme_que', autospec=True)
class TestMantieneForeignField(TestCase):

    def setUp(self):
        self.relatedobject = MiTestRelatedModel.crear(nombre='objeto rel')
        self.object = MiTestModel.crear(
            nombre='objeto',
            numero=1,
            related=self.relatedobject
        )

    def test_llama_a_es_le_misme_que_con_campo_y_otro_objeto(self, mock_es_le_misme_que):
        obj_guardado = self.object
        self.object.mantiene_foreignfield('related', obj_guardado)
        mock_es_le_misme_que.assert_called_once_with(
            self.object.related,
            obj_guardado.related
        )

    def test_devuelve_true_si_campo_es_igual_al_de_otro(self, mock_es_le_misme_que):
        mock_otro = MagicMock()
        mock_es_le_misme_que.return_value = True
        self.assertTrue(
            self.object.mantiene_foreignfield('related', mock_otro)
        )

    def test_devuelve_false_si_campo_es_distinto_al_de_otro(self, mock_es_le_misme_que):
        mock_otro = MagicMock()
        mock_es_le_misme_que.return_value = False
        self.assertFalse(self.object.mantiene_foreignfield('related', mock_otro))

    def test_devuelve_false_si_campo_es_none(self, mock_es_le_misme_que):
        mock_otro = MagicMock()
        self.object.related = None
        self.assertFalse(self.object.mantiene_foreignfield('related', mock_otro))

    def test_tira_error_si_campo_no_es_foreignfield(self, mock_es_le_misme_que):
        mock_mov = MagicMock()
        with self.assertRaisesMessage(
                AttributeError,
                'El campo nombre debe ser de tipo ForeignField'
        ):
            self.object.mantiene_foreignfield('nombre', mock_mov)
