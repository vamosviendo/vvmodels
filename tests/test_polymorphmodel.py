from django.test import TestCase

from vvmodel.tests.models import MiTestPolymorphModel, MiTestPolymorphSubmodel, \
    MiTestRelatedModel, MiTestPolymorphSubSubModel


class PolymorphModelMetodos(TestCase):

    def setUp(self):
        self.obj = MiTestPolymorphModel.crear(nombre='objeto', numero=1)
        self.obj_sub = MiTestPolymorphSubmodel.crear(
            nombre='subobjeto', numero=2, detalle='cosas')

    def test_tomar_devuelve_objeto_polimorfico(self):
        self.assertEqual(
            MiTestPolymorphModel.tomar(numero=2).get_class(),
            MiTestPolymorphSubmodel
        )
        self.assertNotEqual(
            MiTestPolymorphModel.tomar(numero=2).get_class(),
            MiTestPolymorphModel
        )

    def test_tomar_devuelve_objeto_no_polimorfico_con_polymorphic_false(self):
        self.assertEqual(
            MiTestPolymorphModel.tomar(numero=2, polymorphic=False).get_class(),
            MiTestPolymorphModel
        )
        self.assertNotEqual(
            MiTestPolymorphModel.tomar(numero=2, polymorphic=False).get_class(),
            MiTestPolymorphSubmodel
        )

    def test_como_subclase_devuelve_objeto_como_instancia_del_submodelo(self):
        obj = MiTestPolymorphModel.tomar(numero=2, polymorphic=False)
        self.assertEqual(
            obj.como_subclase().get_class(),
            MiTestPolymorphSubmodel
        )
        self.assertNotEqual(
            obj.como_subclase().get_class(),
            MiTestPolymorphModel
        )

    def test_save_guarda_app_en_campo_content_type(self):
        obj = MiTestPolymorphModel(nombre='objeto polimórfico', numero=3)
        obj.save()
        self.assertEqual(obj.content_type.app_label, 'tests')

    def test_save_guarda_modelo_en_campo_content_type(self):
        obj = MiTestPolymorphModel(nombre='objeto polimórfico', numero=3)
        objsub = MiTestPolymorphSubmodel(
            nombre='subobjeto polimórfico', numero=4)

        obj.save()
        self.assertEqual(obj.content_type.model, 'mitestpolymorphmodel')

        objsub.save()
        self.assertEqual(
            objsub.content_type.model, 'mitestpolymorphsubmodel')

    def test_actualizar_subclase_devuelve_el_mismo_objeto_actualizado_como_subclase(self):
        obj = MiTestPolymorphSubmodel.crear(
            nombre="subobject", numero=1, detalle="detalles")
        superobj = MiTestPolymorphModel.tomar(pk=obj.pk, polymorphic=False)
        self.assertEqual(type(superobj.actualizar_subclase()), MiTestPolymorphSubmodel)
