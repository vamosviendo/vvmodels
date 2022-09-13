from django.test import TestCase

from vvmodel.managers import PolymorphManager, PolymorphQuerySet
from vvmodel.tests.models import MiTestPolymorphModel


class TestPolymorphManager(TestCase):

    def setUp(self):
        self.poly_manager = PolymorphManager()
        self.poly_manager.model = MiTestPolymorphModel

    def test_get_queryset_devuelve_polymorphic_queryset(self):
        """ Produce querysets del tipo PolymorphicQueryset."""
        self.assertEqual(type(self.poly_manager.get_queryset()), PolymorphQuerySet)

    def test_polymorphic_queryset_devuelve_item_con_clase_correcta(self):
        """ Dentro de un PolymorphicQueryset cada obra conserva su subclase."""
        for o in self.poly_manager.get_queryset().__iter__():
            self.assertEqual(type(o), o.content_type.model_class())
