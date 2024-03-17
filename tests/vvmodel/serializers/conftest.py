import json
from io import StringIO
from pathlib import Path
from typing import Union, TextIO, Generator

import pytest
from django.core.management import call_command

from vvmodel.serializers import SerializedDb, SerializedObject
from vvmodel.tests.models import MiTestModel, MiTestRelatedModel, MiTestPolymorphModel

TestModel = Union[MiTestModel, MiTestRelatedModel, MiTestPolymorphModel]


@pytest.fixture
def elementos(
        miobjeto: MiTestRelatedModel,
        miotroobjeto: MiTestRelatedModel,
        miobjetocomplejo: MiTestModel,
        miobjetopolimorfico: MiTestPolymorphModel
) -> list[TestModel]:
    return [miobjeto, miotroobjeto, miobjetocomplejo, miobjetopolimorfico]


@pytest.fixture
def serialized_file(elementos) -> Generator[TextIO, None, None]:
    serialized_db = StringIO()
    call_command("dumpdata", "tests", indent=2, stdout=serialized_db)
    with open('db.json', 'w') as sf:
        sf.write(serialized_db.getvalue())
    with open('db.json', 'r') as sf:
        yield sf
    Path('db.json').unlink()


@pytest.fixture
def serialized_db(elementos: list[TestModel]) -> SerializedDb:
    serialization = StringIO()
    call_command('dumpdata', indent=2, stdout=serialization)
    serialized_db = SerializedDb()
    for obj in json.loads(serialization.getvalue()):
        serialized_db.append(SerializedObject(obj, container=serialized_db))
    return serialized_db
