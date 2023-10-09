import datetime
import pytest

from pyramid_oereb.core.records.document_types import DocumentTypeRecord
from pyramid_oereb.core.records.documents import DocumentRecord
from pyramid_oereb.core.records.law_status import LawStatusRecord
from pyramid_oereb.core.records.office import OfficeRecord

from geolink2oereb.lib.interfaces.oerebkrmtrsfr.v2_0.classes import TitelType, TextImWebType, \
    OeREBKRM_V2_0_Amt_Amt, OeREBKRM_V2_0_Dokumente_Dokument, ZustaendigeStelleType
from geolink2oereb.lib.interfaces.oerebkrmtrsfr.v2_0.generators import (
    multilingual_text_from_dict,
    fix_url,
    multilingual_uri_from_dict,
    office_record_to_oerebkrmtrsfr,
    document_record_to_oerebkrmtrsfr
)


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


@pytest.mark.parametrize(
    'input,expected', [
        ('www.test.ch', 'https://www.test.ch'),
        ('http://test.ch', 'http://test.ch'),
        ('test.ch', 'https://test.ch'),
        ('https://test.ch', 'https://test.ch')
    ])
def test_fix_url(input, expected):
    result = fix_url(input)
    assert result == expected


def test_multilingual_text_from_dict():
    result = multilingual_text_from_dict({'de': 'Hallo', 'en': 'Hello'})
    assert isinstance(result, TitelType)


def test_test_multilingual_text_from_dict_none():
    assert multilingual_text_from_dict(None) is None


def test_multilingual_uri_from_dict():
    result = multilingual_uri_from_dict({'de': 'Hallo', 'en': 'Hello'})
    assert isinstance(result, TextImWebType)


def test_multilingual_uri_from_dict_none():
    assert multilingual_uri_from_dict(None) is None


def test_office_record_to_oerebkrmtrsfr(office_record):
    result = office_record_to_oerebkrmtrsfr(office_record)
    assert isinstance(result, OeREBKRM_V2_0_Amt_Amt)
    assert isinstance(result.Name, TitelType)
    assert isinstance(result.AmtImWeb, TextImWebType)
    assert result.UID == office_record.uid
    assert result.Zeile1 == office_record.line1
    assert result.Zeile2 == office_record.line2
    assert result.Strasse == office_record.street
    assert result.Hausnr == office_record.number
    assert result.PLZ == office_record.postal_code
    assert result.Ort == office_record.city


def test_document_record_to_oerebkrmtrsfr(document_record):
    dokument, amt = document_record_to_oerebkrmtrsfr(document_record)
    assert isinstance(dokument, OeREBKRM_V2_0_Dokumente_Dokument)
    assert dokument.Typ == document_record.document_type.code
    assert isinstance(dokument.Titel, TitelType)
    assert isinstance(dokument.Abkuerzung, TitelType)
    assert isinstance(dokument.OffizielleNr, TitelType)
    assert dokument.NurInGemeinde == document_record.only_in_municipality
    assert isinstance(dokument.TextImWeb, TextImWebType)
    assert dokument.AuszugIndex == document_record.index
    assert dokument.Rechtsstatus == document_record.law_status.code
    assert dokument.publiziertAb == document_record.published_from
    assert dokument.publiziertBis == document_record.published_until
    assert isinstance(dokument.ZustaendigeStelle, ZustaendigeStelleType)
