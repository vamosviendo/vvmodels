from io import TextIOWrapper

from vvmodel.serializers import load_serialized_file, load_serialized_filename, SerializedDb


def test_devuelve_una_instancia_de_SerializedDb(serialized_file):
    assert isinstance(load_serialized_file(serialized_file), SerializedDb)


def test_instancia_devuelta_contiene_objetos_en_la_base_de_datos(elementos, serialized_file):
    serialized_db = load_serialized_file(serialized_file)
    nombres = [x["fields"]["nombre"] for x in serialized_db]
    for elemento in elementos:
        assert elemento.nombre in nombres


def test_load_serialized_filename_carga_archivo_serializado_a_partir_de_nombre_de_archivo(serialized_file, mocker):
    mock_load_serialized_file = mocker.patch("vvmodel.serializers.load_serialized_file")
    load_serialized_filename("db.json")
    mock_load_serialized_file.assert_called_once()
    arg = mock_load_serialized_file.call_args.args[0]
    assert isinstance(arg, TextIOWrapper)
    assert arg.name == "db.json"
    assert arg.mode == "r"
