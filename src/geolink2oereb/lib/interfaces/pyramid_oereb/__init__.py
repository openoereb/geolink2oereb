import logging
from pyramid_oereb.core.records.law_status import LawStatusRecord
from pyramid_oereb.core.config import Config
from geolink2oereb.lib.interfaces.oerebkrmtrsfr.v2_0.classes import (
    OeREBKRM_V2_0_DokumentTyp,
)
from pyramid_oereb.core.records.document_types import DocumentTypeRecord
from pyramid_oereb.contrib.data_sources.oereblex.sources.document import OEREBlexSource
from pyramid_oereb.core.views.webservice import Parameter
from pyramid.path import DottedNameResolver

logging.basicConfig(level="DEBUG", format="%(asctime)s [%(levelname)s] %(message)s")

__version__ = "1.0.0"


class OEREBlexSourceCustom(OEREBlexSource):
    def _get_document_title(self, document, current_file, language):
        """
        Starting with V2, pyramid_oereb uses the file title instead of the document title by default.
        In this project, we always want to use the document title, so this overrides that.
        return {language: u'{title} ({file_name})'.format(title=document.title, file_name=current_file.title)}
        file_name=current_file.title

        Args:
            document (geolink_formatter.entity.Document): The document entity.
            current_file (geolink_formatter.entity.File): The file, which gets annotated with a title.
            language (str): The language of the document title.

        Returns:
            str: Title of document.

        """

        if document.doctype == "decree":
            user_title = document.title + " (" + current_file._title + ")"
        else:
            user_title = document.title

        return {language: "{user_title}".format(user_title=user_title)}


def oerebkrm_v2_0_dokument_typ_2_document_type_records():
    """
    Returns: list of pyramid_oereb.core.records.document_types.DocumentTypeRecord
    """
    document_type_records = []
    for document_type_enum in list(OeREBKRM_V2_0_DokumentTyp):
        document_type_records.append(DocumentTypeRecord(document_type_enum.value, {}))
    return document_type_records


def create_document_source(
    source_config, theme_code, language, oereb_lex_document_source_class=OEREBlexSource
):
    """

    Args:
        source_config (dict):
        theme_code (str):
        language (str):
        oereb_lex_document_source_class (pyramid_oereb.contrib.data_sources.oereblex.sources.document.OEREBlexSource):  # noqa: E501
            The class which is used to produce the document records.

    Returns:
        pyramid_oereb.contrib.data_sources.oereblex.sources.document.OEREBlexSource: The source to read
            the documents.
    """

    source_config.update({"code": theme_code, "language": language})
    return oereb_lex_document_source_class(**source_config)


def get_document_type_code_by_extract_value(theme_code, extract_value):
    for lookup in Config.get_document_types_lookups(theme_code):
        if lookup["extract_code"] == extract_value:
            return lookup["transfer_code"]
    return None


def get_law_status_code_by_extract_value(theme_code, extract_value):
    for lookup in Config.get_law_status_lookups(theme_code):
        if lookup["extract_code"] == extract_value:
            return lookup["transfer_code"]
    return None


def merge_office(master, merger):
    """

    Args:
        master (pyramid_oereb.core.records.office.OfficeRecord): The record all date will be added to.
        merger (pyramid_oereb.core.records.office.OfficeRecord): The record all date will be taken from.
    Returns (pyramid_oereb.core.records.office.OfficeRecord): the updated master record.
    """

    master.name.update(merger.name)
    if master.office_at_web is None:
        master.office_at_web = merger.office_at_web
    else:
        master.office_at_web.update(merger.office_at_web)
    return master


def merge_document_type(master, merger):
    """

    Args:
        master (pyramid_oereb.core.records.document_types.DocumentTypeRecord): The record all date will be
            added to.
        merger (pyramid_oereb.core.records.document_types.DocumentTypeRecord): The record all date will be
            taken from.
    Returns (pyramid_oereb.core.records.document_types.DocumentTypeRecord): the updated master record.
    """
    master.title.update(merger.title)
    return DocumentTypeRecord(master.code, master.title)


def merge_document(master, merger):
    """

    Args:
        master (pyramid_oereb.core.records.documents.DocumentRecord): The record all date will be added to.
        merger (pyramid_oereb.core.records.documents.DocumentRecord): The record all date will be taken from.
    Returns (pyramid_oereb.core.records.documents.DocumentRecord): the updated master record.
    """
    master.document_type = merge_document_type(master.document_type, merger.document_type)
    master.law_status = LawStatusRecord(master.law_status.code, master.law_status.title)
    master.responsible_office = merge_office(master.responsible_office, merger.responsible_office)
    master.title.update(merger.title)
    if master.text_at_web is None:
        master.text_at_web = merger.text_at_web
    else:
        master.text_at_web.update(merger.text_at_web)
    if master.abbreviation is None:
        master.abbreviation = merger.abbreviation
    else:
        master.abbreviation.update(merger.abbreviation)
    if master.official_number is None:
        master.official_number = merger.official_number
    else:
        master.official_number.update(merger.official_number)
    return master


def make_office_at_web_multilingual(documents, language):
    """

    Args:
        documents (list of pyramid_oereb.core.records.documents.DocumentRecord): The records to change the
            office.
        language (str): the language code which will be used to make it multilingual.
    Returns (list of pyramid_oereb.core.records.documents.DocumentRecord): the updated records.
    """
    for record in documents:
        if not isinstance(record.responsible_office.office_at_web, dict):
            record.responsible_office.office_at_web = {language: record.responsible_office.office_at_web}
    return documents


def load(
    geolink_id,
    theme_code,
    pyramid_oereb_config_path,
    pyramid_config_section,
    source_class_path="geolink2oereb.lib.interfaces.pyramid_oereb.OEREBlexSourceCustom",
    c2ctemplate_style=False,
):
    Config._config = None
    Config.init(
        pyramid_oereb_config_path,
        pyramid_config_section,
        c2ctemplate_style=c2ctemplate_style,
        init_data=False,
    )
    Config.document_types = oerebkrm_v2_0_dokument_typ_2_document_type_records()
    lst = LawStatusRecord(
        "inKraft",
        {
            "de": "in Kraft",
            "fr": "En vigueur",
            "it": "In vigore",
            "rm": "En vigur",
            "en": "In force",
        },
    )
    Config.law_status = [lst]
    p = Parameter("xml")

    resolver = DottedNameResolver()
    oereblex_source_class = resolver.resolve(source_class_path)
    source = create_document_source(
        Config.get_oereblex_config(),
        theme_code,
        Config._config["default_language"],
        oereb_lex_document_source_class=oereblex_source_class,
    )

    master_language = Config.get_language()[0]
    p.set_language(master_language)
    source.read(p, geolink_id, lst)
    result = make_office_at_web_multilingual(source.records, master_language)

    for language in Config.get_language():
        if language != master_language:
            p.set_language(language)
            source.read(p, geolink_id, lst)
            mergers = make_office_at_web_multilingual(source.records, language)
            for index, record in enumerate(mergers):
                merge_document(result[index], record)

    for record in result:
        new_code = get_document_type_code_by_extract_value(theme_code, record.document_type.code)
        logging.debug(f"Old document code: {record.document_type.code}")
        logging.debug(f"New document code: {new_code}")
        record.document_type.code = new_code

        new_code = get_law_status_code_by_extract_value(theme_code, record.law_status.code)
        logging.debug(f"Old law status code: {record.law_status.code}")
        logging.debug(f"New law status code: {new_code}")
        record.law_status.code = new_code

    return result
