import datetime

import pytest
from geolink_formatter.entity import Document, File
from pyramid_oereb.contrib.data_sources.oereblex.sources.document import OEREBlexSource
from pyramid_oereb.core.records.document_types import DocumentTypeRecord
from pyramid_oereb.core.records.documents import DocumentRecord
from pyramid_oereb.core.records.law_status import LawStatusRecord
from pyramid_oereb.core.records.office import OfficeRecord

from geolink2oereb.lib.interfaces.pyramid_oereb import oerebkrm_v2_0_dokument_typ_2_document_type_records, \
    create_document_source, OEREBlexSourceCustom, get_document_type_code_by_extract_value, \
    get_law_status_code_by_extract_value, merge_office, merge_document_type, merge_document, \
    merge_attribute, make_office_at_web_multilingual


@pytest.fixture
def pyramid_oereb_config():
    yield {
        "language": ["de", "it", "rm"],
        "default_language": "de",
        "flavour": ["REDUCED"],
        "srid": 2056,
        "plrs": [{
            "code": "ch.Planungszonen",
            "geometry_type": "GEOMETRYCOLLECTION",
            "thresholds": {
                "length": {
                    "limit": 1.0,
                    "unit": "m",
                    "precision": 2
                },
                "area": {
                    "limit": 1.0,
                    "unit": "m²",
                    "precision": 2
                },
                "percentage": {
                    "precision": 1
                }
            },
            "language": "de",
            "federal": False,
            "view_service": {
                "layer_index": 1,
                "layer_opacity": 0.75
            },
            "source": {
                "class": "pyramid_oereb.contrib.data_sources.interlis_2_3.sources.plr.DatabaseSource",
                "params": {
                    "db_connection": "main_db_connection",
                    "model_factory": "pyramid_oereb.contrib.data_sources.interlis_2_3.models.theme.model_factory_integer_pk",  # noqa: E501
                    "schema_name": "planungszonen"
                }
            },
            "hooks": {
                "get_symbol": "pyramid_oereb.contrib.data_sources.interlis_2_3.hook_methods.get_symbol",
                "get_symbol_ref": "pyramid_oereb.core.hook_methods.get_symbol_ref"
            },
            "law_status_lookup": [{
                "data_code": "inKraft",
                "transfer_code": "inKraft",
                "extract_code": "inForce"
            }, {
                "data_code": "AenderungMitVorwirkung",
                "transfer_code": "AenderungMitVorwirkung",
                "extract_code": "changeWithPreEffect"
            }, {
                "data_code": "AenderungOhneVorwirkung",
                "transfer_code": "AenderungOhneVorwirkung",
                "extract_code": "changeWithoutPreEffect"
            }],
            "document_types_lookup": [{
                "data_code": "decree",
                "transfer_code": "Rechtsvorschrift",
                "extract_code": "LegalProvision"
            }, {
                "data_code": "edict",
                "transfer_code": "GesetzlicheGrundlage",
                "extract_code": "Law"
            }, {
                "data_code": "notice",
                "transfer_code": "Hinweis",
                "extract_code": "Hint"
            }]
        }],
        "static_error_message": {
            "de": "Ein oder mehrere ÖREB-Themen stehen momentan nicht zur Verfügung. Daher kann kein Auszug erstellt werden. Versuchen Sie es zu einem späteren Zeitpunkt erneut. Wir entschuldigen uns für die Unannehmlichkeiten.",  # noqa: E501
            "rm": "Ein oder mehrere ÖREB-Themen stehen momentan nicht zur Verfügung. Daher kann kein Auszug erstellt werden. Versuchen Sie es zu einem späteren Zeitpunkt erneut. Wir entschuldigen uns für die Unannehmlichkeiten.",  # noqa: E501
            "it": "Uno o più temi relativi alle RDPP non sono attualmente disponibili. Non è pertanto possibile allestire alcun estratto. Vi preghiamo di riprovare più tardi. Ci scusiamo per l’inconveniente."  # noqa: E501
        }
    }


@pytest.fixture
def document_type_records():
    yield [
        DocumentTypeRecord(
            'GesetzlicheGrundlage',
            {'de': 'Gesetzliche Grundlage'}
        ),
        DocumentTypeRecord(
            'Rechtsvorschrift',
            {'de': 'Rechtsvorschrift'}
        ),
        DocumentTypeRecord(
            'Hinweis',
            {'de': 'Hinweis'}
        )
    ]


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
def source_config():
    yield {
        "host": "https://oereblex.gr.ch",
        "version": "1.2.2",
        "pass_version": True,
        "validation": True,
        "language": "de",
        "canton": "GR",
        "mapping": {
            "official_number": "number",
            "abbreviation": "abbreviation"
        },
        "related_decree_as_main": False,
        "related_notice_as_main": False,
        "proxy": None,
        "url_param_config": [{
            "code": "ch.StatischeWaldgrenzen",
            "url_param": "oereb_id=24"
        }, {
            "code": "ch.Waldabstandslinien",
            "url_param": "oereb_id=25"
        }, {
            "code": "ch.Laermempfindlichkeitsstufen",
            "url_param": "oereb_id=26"
        }, {
            "code": "ch.GR.NutzungsplanungZpGgp",
            "url_param": "oereb_id=11"
        }, {
            "code": "ch.GR.NutzungsplanungGep",
            "url_param": "oereb_id=11"
        }, {
            "code": "ch.GR.NutzungsplanungFp",
            "url_param": "oereb_id=11"
        }]
    }


@pytest.fixture
def geolinkformatter_document_decree():
    file = File(
        "main",
        "/api/attachments/17906",
        "3619_B_Prüfung_red_Bauzonen_WMZ_Anpassung_de.pdf",
        "3619_B_Prüfung_red_Bauzonen_WMZ_Anpassung_de.pdf"
    )
    yield Document(
        [file],
        "5",
        "related",
        "decree",
        "Gemeinde",
        "Gemeindeverwaltung",
        "www.ilanz-glion.ch",
        "Prüfung einer Reduktion von Bauzonen WMZ (Anpassung)",
        "00.075.963",
        None,
        None,
        "Planungszonen",
        None,
        None,
        datetime.date(2022, 12, 23),
        datetime.date(2024, 2, 12),
        None,
        "Ilanz/Glion",
        None,
        None,
        None,
        None
    )


@pytest.fixture
def geolinkformatter_document_edict():
    file = File(
        "main",
        "https://www.lexfind.ch/tolv/220739/de",
        "700.de.pdf",
        "700.de.pdf"
    )
    yield Document(
        [file],
        "5",
        "related",
        "edict",
        "Bund",
        "Bundeskanzlei",
        "https://www.bk.admin.ch/",
        "Bundesgesetz über die Raumplanung",
        "SR 700",
        "Raumplanungsgesetz, RPG",
        None,
        None,
        None,
        None,
        datetime.date(2019, 1, 1),
        None,
        None,
        None,
        10,
        None,
        None,
        None
    )


@pytest.mark.parametrize('master,merger,output', [
    (None, None, None),
    ({'de': 'test'}, None, {'de': 'test'}),
    (None, {'de': 'test'}, {'de': 'test'}),
    ({'en': 'test'}, {'de': 'test'}, {'de': 'test', 'en': 'test'}),
    ('test', {'de': 'test'}, None)
])
def test_merge_attribute(master, merger, output):
    assert merge_attribute(master, merger) == output


def test_oerebkrm_v2_0_dokument_typ_2_document_type_records():
    result = oerebkrm_v2_0_dokument_typ_2_document_type_records()
    assert len(result) == 3
    for document_type in result:
        assert isinstance(document_type, DocumentTypeRecord)


def test_create_document_source(source_config):
    result = create_document_source(
        source_config,
        'ch.Planungszonen',
        'de',
        oereb_lex_document_source_class=OEREBlexSource
    )
    assert isinstance(result, OEREBlexSource)


def test_oereblex_source_custom(source_config):
    result = create_document_source(
        source_config,
        'ch.Planungszonen',
        'de',
        oereb_lex_document_source_class=OEREBlexSourceCustom
    )
    assert isinstance(result, OEREBlexSourceCustom)


def test_oereblex_source_custom_filter_federal_documents(source_config):
    result = create_document_source(
        source_config,
        'ch.Planungszonen',
        'de',
        oereb_lex_document_source_class=OEREBlexSourceCustom
    )
    assert isinstance(result.filter_federal_documents, list)
    for item in result.filter_federal_documents:
        assert isinstance(item, str)


def test_oereblex_source_custom_get_document_title_edict(source_config, geolinkformatter_document_edict):
    result = create_document_source(
        source_config,
        'ch.Planungszonen',
        'de',
        oereb_lex_document_source_class=OEREBlexSourceCustom
    )
    title = result._get_document_title(
        geolinkformatter_document_edict,
        geolinkformatter_document_edict.files[0],
        'de'
    )
    assert isinstance(title, dict)
    assert title['de'] == geolinkformatter_document_edict.title


def test_oereblex_source_custom_get_document_title_decree(source_config, geolinkformatter_document_decree):
    result = create_document_source(
        source_config,
        'ch.Planungszonen',
        'de',
        oereb_lex_document_source_class=OEREBlexSourceCustom
    )
    title = result._get_document_title(
        geolinkformatter_document_decree,
        geolinkformatter_document_decree.files[0],
        'de'
    )
    assert isinstance(title, dict)
    assert title['de'] == (f'{geolinkformatter_document_decree.title} '
                           f'({geolinkformatter_document_decree.files[0]._title})')


def test_oereblex_source_custom_get_document_records_filtered(source_config, geolinkformatter_document_edict):
    result = create_document_source(
        source_config,
        'ch.Planungszonen',
        'de',
        oereb_lex_document_source_class=OEREBlexSourceCustom
    )
    document_records = result._get_document_records(geolinkformatter_document_edict, 'de')
    assert isinstance(document_records, list)
    assert len(document_records) == 0


def test_oereblex_source_custom_get_document_records_not_filtered(
    source_config,
    geolinkformatter_document_decree,
    pyramid_oereb_config,
    document_type_records,
    law_status_record
):
    from pyramid_oereb.core.config import Config
    Config._config = pyramid_oereb_config
    Config.document_types = document_type_records
    Config.law_status = [law_status_record]
    result = create_document_source(
        source_config,
        'ch.Planungszonen',
        'de',
        oereb_lex_document_source_class=OEREBlexSourceCustom
    )
    document_records = result._get_document_records(geolinkformatter_document_decree, 'de')
    assert isinstance(document_records, list)
    assert len(document_records) == 1
    assert isinstance(document_records[0], DocumentRecord)


@pytest.mark.parametrize('input,output', [
    ('LegalProvision', 'Rechtsvorschrift'),
    ('Law', 'GesetzlicheGrundlage'),
    ('Hint', 'Hinweis'),
    ('NotConfigured', None)
])
def test_get_document_type_code_by_extract_value(input, output, pyramid_oereb_config):
    from pyramid_oereb.core.config import Config
    Config._config = pyramid_oereb_config
    result = get_document_type_code_by_extract_value(
        'ch.Planungszonen',
        input
    )
    assert result == output


@pytest.mark.parametrize('input,output', [
    ('inForce', 'inKraft'),
    ('changeWithPreEffect', 'AenderungMitVorwirkung'),
    ('changeWithoutPreEffect', 'AenderungOhneVorwirkung'),
    ('NotConfigured', None)
])
def test_get_law_status_code_by_extract_value(input, output, pyramid_oereb_config):
    from pyramid_oereb.core.config import Config
    Config._config = pyramid_oereb_config
    result = get_law_status_code_by_extract_value(
        'ch.Planungszonen',
        input
    )
    assert result == output


def test_merge_office_updated_name():
    office_master = OfficeRecord({'de': 'Das ist ein Testname'})
    office_merger = OfficeRecord({'en': 'This is a test name'})
    result = merge_office(office_master, office_merger)
    assert result.name == {'de': 'Das ist ein Testname', 'en': 'This is a test name'}


def test_merge_office_updated_update_url_merger_none():
    office_master = OfficeRecord(
        {'de': 'Das ist ein Testname'},
        office_at_web={'de': 'https://test.de'}
    )
    office_merger = OfficeRecord(
        {'en': 'This is a test name'}
    )
    result = merge_office(office_master, office_merger)
    assert result.office_at_web == office_master.office_at_web


def test_merge_office_updated_update_url_master_none():
    office_master = OfficeRecord(
        {'de': 'Das ist ein Testname'}
    )
    office_merger = OfficeRecord(
        {'en': 'This is a test name'},
        office_at_web={'en': 'https://test.com'}
    )
    result = merge_office(office_master, office_merger)
    assert result.office_at_web == office_merger.office_at_web


def test_merge_office_updated_update_url():
    office_master = OfficeRecord(
        {'de': 'Das ist ein Testname'},
        office_at_web={'de': 'https://test.de'}
    )
    office_merger = OfficeRecord(
        {'en': 'This is a test name'},
        office_at_web={'en': 'https://test.com'}
    )
    result = merge_office(office_master, office_merger)
    assert result.office_at_web == {'de': 'https://test.de', 'en': 'https://test.com'}


def test_merge_document_type():
    document_type_master = DocumentTypeRecord(
        'GesetzlicheGrundlage',
        {'de': 'Gesetzliche Grundlage'}
    )
    document_type_merger = DocumentTypeRecord(
        'GesetzlicheGrundlage',
        {'en': 'Legal Base'}
    )
    result = merge_document_type(document_type_master, document_type_merger)
    assert result.title == {'de': 'Gesetzliche Grundlage', 'en': 'Legal Base'}


def test_merge_document():
    office_master = OfficeRecord(
        {'de': 'Das ist ein Testname'},
        office_at_web={'de': 'https://test.de'}
    )
    office_merger = OfficeRecord(
        {'en': 'This is a test name'},
        office_at_web={'en': 'https://test.com'}
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
        office_merger,
        datetime.date(1986, 8, 29),
        text_at_web={'en': 'https://document.com'},
        abbreviation={'en': 'abbrv'},
        official_number={'en': 'legal 1234'}
    )
    result = merge_document(document_master, document_merger)
    assert isinstance(result, DocumentRecord)
    assert result.law_status.code == document_master.law_status.code
    assert result.law_status.title == document_master.law_status.title
    assert result.title == {'de': 'Der Titel', 'en': 'The Title'}
    assert result.text_at_web == {'de': 'https://dokument.de', 'en': 'https://document.com'}
    assert result.abbreviation == {'de': 'abkrzg', 'en': 'abbrv'}
    assert result.official_number == {'de': 'RPG 1234', 'en': 'legal 1234'}


def test_make_office_at_web_multilingual_pass():
    office = OfficeRecord(
        {'de': 'Das ist ein Testname'},
        office_at_web={'de': 'https://test.de'}
    )
    document_type = DocumentTypeRecord(
        'GesetzlicheGrundlage',
        {'de': 'Gesetzliche Grundlage'}
    )
    law_status = LawStatusRecord(
        'inKraft',
        {
            "de": "Rechtskräftig"
        }
    )
    document = DocumentRecord(
        document_type,
        1,
        law_status,
        {'de': 'Der Titel'},
        office,
        datetime.date(1986, 8, 29),
        text_at_web={'de': 'https://dokument.de'},
        abbreviation={'de': 'abkrzg'},
        official_number={'de': 'RPG 1234'}
    )
    result = make_office_at_web_multilingual([document], 'de')
    assert result[0].responsible_office.office_at_web == office.office_at_web


def test_make_office_at_web_multilingual_not_pass():
    office = OfficeRecord(
        {'de': 'Das ist ein Testname'},
        office_at_web='https://test.de'
    )
    document_type = DocumentTypeRecord(
        'GesetzlicheGrundlage',
        {'de': 'Gesetzliche Grundlage'}
    )
    law_status = LawStatusRecord(
        'inKraft',
        {
            "de": "Rechtskräftig"
        }
    )
    document = DocumentRecord(
        document_type,
        1,
        law_status,
        {'de': 'Der Titel'},
        office,
        datetime.date(1986, 8, 29),
        text_at_web={'de': 'https://dokument.de'},
        abbreviation={'de': 'abkrzg'},
        official_number={'de': 'RPG 1234'}
    )
    result = make_office_at_web_multilingual([document], 'de')
    assert result[0].responsible_office.office_at_web == {'de': 'https://test.de'}
