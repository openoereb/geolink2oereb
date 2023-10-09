import datetime
from uuid import UUID

import pytest
from unittest.mock import patch

from pyramid_oereb.core.records.document_types import DocumentTypeRecord
from pyramid_oereb.core.records.documents import DocumentRecord
from pyramid_oereb.core.records.law_status import LawStatusRecord
from pyramid_oereb.core.records.office import OfficeRecord


@pytest.fixture
def law_status_record():
    yield LawStatusRecord(
        'inKraft', {
            "de": "Rechtskräftig",
            "fr": "En vigueur",
            "it": "In vigore",
            "rm": "En vigur",
            "en": "In force"
        }
    )


@pytest.fixture
def document_type_record():
    yield DocumentTypeRecord(
        'GesetzlicheGrundlage',
        {'de': 'Gesetzliche Grundlage'}
    )


@pytest.fixture
def office_record():
    yield OfficeRecord(
        {'de': 'Test'},
        office_at_web={'de': 'www.example.com'},
        uid='ch99',
        postal_code=4123,
        line1='Adresszeile 1',
        line2='Adresszeile 2',
        street='Straße',
        number='999',
        city='Basel'
    )


@pytest.fixture
def document_record(office_record, document_type_record, law_status_record):
    yield DocumentRecord(
        document_type_record,
        1,
        law_status_record,
        {'de': 'Title'},
        office_record,
        datetime.date(1985, 8, 29),
        text_at_web={'de': 'http://mein.dokument.ch'},
        abbreviation={'de': 'abkrzg'},
        official_number={'de': '123 BGB'},
        only_in_municipality=2345,
        published_until=datetime.date(2999, 8, 29)
    )


def test_run(document_record):
    with patch('geolink2oereb.lib.interfaces.pyramid_oereb.load', return_value=[document_record]):
        from geolink2oereb.transform import run
        from geolink2oereb.lib.interfaces.oerebkrmtrsfr.v2_0.classes import OeREBKRM_V2_0_Dokumente_Dokument
        result = run(
            4304,
            'ch.Planungszonen',
            '/a/b/c',
            'pyramid_oereb'
        )
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], tuple)
        assert isinstance(list(result[0])[0], OeREBKRM_V2_0_Dokumente_Dokument)


@pytest.fixture
def gathered_documents():
    office_master = OfficeRecord(
        {'de': 'Das ist ein Testname'},
        office_at_web={'de': 'https://test.de'}
    )
    document_type_master = DocumentTypeRecord(
        'GesetzlicheGrundlage',
        {'de': 'Gesetzliche Grundlage'}
    )
    document_type_merger = DocumentTypeRecord(
        'GesetzlicheGrundlage',
        {'en': 'Legal Base'}
    )
    law_status_master = LawStatusRecord(
        'inKraft',
        {
            "de": "Rechtskräftig"
        }
    )
    law_status_merger = LawStatusRecord(
        'inKraft',
        {
            "en": "In force"
        }
    )
    document_master = DocumentRecord(
        document_type_master,
        1,
        law_status_master,
        {'de': 'Der Titel'},
        office_master,
        datetime.date(1986, 8, 29),
        text_at_web={'de': 'https://dokument.de'},
        abbreviation={'de': 'abkrzg'},
        official_number={'de': 'RPG 1234'}
    )
    document_merger = DocumentRecord(
        document_type_merger,
        1,
        law_status_merger,
        {'en': 'The Title'},
        office_master,
        datetime.date(1986, 8, 29),
        text_at_web={'en': 'https://document.com'},
        abbreviation={'en': 'abbrv'},
        official_number={'en': 'legal 1234'}
    )
    yield [document_merger, document_master]


def test_run_batch(gathered_documents):
    with patch('geolink2oereb.lib.interfaces.pyramid_oereb.load', return_value=gathered_documents):
        from geolink2oereb.transform import run_batch
        from geolink2oereb.lib.interfaces.oerebkrmtrsfr.v2_0.classes import (
            OeREBKRM_V2_0_Dokumente_Dokument, OeREBKRM_V2_0_Amt_Amt)
        result = run_batch(
            [4304, 4305],
            'ch.Planungszonen',
            '/a/b/c',
            'pyramid_oereb'
        )
        assert isinstance(result, list)
        assert len(result) == 2
        assert len(list(result[0])) == 2
        assert isinstance(list(result[0])[0], OeREBKRM_V2_0_Dokumente_Dokument)
        assert isinstance(list(result[0])[1], OeREBKRM_V2_0_Amt_Amt)
        assert isinstance(list(result[1])[0], OeREBKRM_V2_0_Dokumente_Dokument)
        assert isinstance(list(result[1])[1], OeREBKRM_V2_0_Amt_Amt)


@pytest.fixture
def gathered_oerebkrm(gathered_documents):
    from geolink2oereb.lib.interfaces.oerebkrmtrsfr.v2_0.generators import document_record_to_oerebkrmtrsfr
    yield [
        document_record_to_oerebkrmtrsfr(gathered_documents[0]),
        document_record_to_oerebkrmtrsfr(gathered_documents[1])
    ]


def test_unify_gathered(gathered_oerebkrm):
    from geolink2oereb.transform import unify_gathered
    result = unify_gathered(gathered_oerebkrm)
    assert isinstance(result, tuple)
    assert len(list(result)[0]) == 2
    assert len(list(result)[1]) == 1


def test_assign_uuids(gathered_oerebkrm):
    from geolink2oereb.transform import unify_gathered, assign_uuids
    result = assign_uuids(*unify_gathered(gathered_oerebkrm))
    assert isinstance(result, tuple)
    assert len(list(result)[0]) == 2
    assert len(list(result)[1]) == 1
    assert UUID(list(result)[1][0].TID, version=4)
    assert UUID(list(result)[0][0].TID, version=4)
    assert UUID(list(result)[0][1].TID, version=4)
    assert list(result)[0][0].ZustaendigeStelle.REF == list(result)[1][0].TID
    assert list(result)[0][1].ZustaendigeStelle.REF == list(result)[1][0].TID
