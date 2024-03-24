from vvmodel.serializers import SerializedObject


class SerializedMiTestModel(SerializedObject):
    @classmethod
    def model_string(cls):
        return "tests.mitestmodel"
