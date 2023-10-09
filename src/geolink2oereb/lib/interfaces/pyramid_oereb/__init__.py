"""
This module offers the interface to the `pyramid_oereb <https://github.com/openoereb/pyramid_oereb>`_ library.
All usage of ``pyramid_oereb`` elements should be implemented here and proxied through this part
of geolink2oereb. That makes it easier to adapt once changes occur.
"""

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


def merge_attribute(master_attribute, merger_attribute):
    """
    A helper method to merge attributes which can be a dict or None.

    Args:
        master_attribute (dict or None): The master attribute.
        merger_attribute (dict or None): The merger attribute.

    Returns:
        dict or None: The merged Attribute
    """

    if master_attribute is None and merger_attribute is None:
        # both attributes are None, we can return None here
        return None
    if master_attribute is None and isinstance(merger_attribute, dict):
        # one attribute is None the other is a dict, we return the dict
        return merger_attribute
    if merger_attribute is None and isinstance(master_attribute, dict):
        # one attribute is None the other is a dict, we return the dict
        return master_attribute
    if isinstance(master_attribute, dict) and isinstance(merger_attribute, dict):
        # both attributes are dicts, we return the merged dict
        return {**master_attribute, **merger_attribute}
    # in all other cases we simply return None
    return None


class OEREBlexSourceCustom(OEREBlexSource):
    """
    This subclass is basically used to manipulate the behaviour of the normal OEREBlexSource as it is used
    in ``pyramid_oereb``.

    Main changes are:
    - adaption of _get_document_title to be able to manipulate title of documents more easy
    - adaption of _get_document_records to add a filter for federal documents because they are provided
      in another way and can be omitted.
    """
    @property
    def filter_federal_documents(self):
        """
        A list to filter documents. It can be adopted to manipulate how the filter should work. In the default
        implementation it comletely skip federal documents because they should be added via official sources:
        https://models.geo.admin.ch/V_D/OeREB/OeREBKRM_V2_0_Gesetze.xml

        The strings in the list are applied to the ``federal_level`` of a ÖEREBlex document.

        Returns:
            list of str: The filter strings which are applied to ``federal_level`` of a ÖEREBlex document.
        """
        # TODO: add french identifier of federal docs
        return ['Bund', 'Cancelleria federale', 'Confederaziun', 'Confederazione']

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

    def _get_document_records(self, document, language):
        """
        Converts the received documents into records. This subclass filters configured objects.

        Args:
            document (geolink_formatter.entity.Document): The geoLink document to be returned as document
                record.
            language (str): The language of the returned documents.

        Returns:
            list of pyramid_oereb.core.records.documents.DocumentRecord: The converted record.
        """
        if document.federal_level:
            if document.federal_level in self.filter_federal_documents:
                logging.info(
                    f'filtering {document} because its federal level is '
                    f'in the filter list {self.filter_federal_documents}'
                )
                return []
        return super(OEREBlexSourceCustom, self)._get_document_records(document, language)


def oerebkrm_v2_0_dokument_typ_2_document_type_records():
    """
    Translates all OeREBKRM_V2_0_DokumentTyp to actual DocumentTypeRecord.

    Returns:
        list of pyramid_oereb.core.records.document_types.DocumentTypeRecord
    """
    document_type_records = []
    for document_type_enum in list(OeREBKRM_V2_0_DokumentTyp):
        document_type_records.append(DocumentTypeRecord(document_type_enum.value, {}))
    return document_type_records


def create_document_source(
    source_config, theme_code, language, oereb_lex_document_source_class=OEREBlexSource
):
    """
    Interface method to ``pyramid_oereb``, to complete the config of the used ``pyramid_oereb`` source
    with missing elements and create the actual data source.

    Args:
        source_config (dict): The config dict which is used to instanciate the ÖEREBlex Source.
        theme_code (str): The theme code matching the ``pyramid_oereb`` configuration.
        language (str): The language code (de, it, fr, ...).
        oereb_lex_document_source_class (pyramid_oereb.contrib.data_sources.oereblex.sources.document.OEREBlexSource):  # noqa: E501
            The class which is used to produce the document records.

    Returns:
        pyramid_oereb.contrib.data_sources.oereblex.sources.document.OEREBlexSource: The source to read
            the documents.
    """

    source_config.update({"code": theme_code, "language": language})
    return oereb_lex_document_source_class(**source_config)


def get_document_type_code_by_extract_value(theme_code, extract_value):
    """
    Interface method to ``pyramid_oereb``. Shortcut method to access the translation of ``document_types`` as
    defined in ``pyramid_oereb`` configuration yaml.

    Args:
        theme_code (str): The theme code matching the ``pyramid_oereb`` configuration.
        extract_value (str): The ``document_type`` as it is expected in the extract.
    Returns:
        None or str: The translated ``document_type`` or None if no match was found.
    """
    for lookup in Config.get_document_types_lookups(theme_code):
        if lookup["extract_code"] == extract_value:
            return lookup["transfer_code"]
    return None


def get_law_status_code_by_extract_value(theme_code, extract_value):
    """
    Interface method to ``pyramid_oereb``. Shortcut method to access the translation of ``law_status_codes``
    as defined in ``pyramid_oereb`` configuration yaml.

    Args:
        theme_code (str): The theme code matching the ``pyramid_oereb`` configuration.
        extract_value (str): The ``law_status_code`` as it is expected in the extract.
    Returns:
        None or str: The translated ``law_status_code`` or None if no match was found.
    """
    for lookup in Config.get_law_status_lookups(theme_code):
        if lookup["extract_code"] == extract_value:
            return lookup["transfer_code"]
    return None


def merge_office(master, merger):
    """
    Merge multiple ``OfficeRecords`` to one. While processing ÖREBlex there can occur different versions
    of the same office in different languages. We try to solve that problem here.

    Args:
        master (pyramid_oereb.core.records.office.OfficeRecord): The record all date will be added to.
        merger (pyramid_oereb.core.records.office.OfficeRecord): The record all date will be taken from.
    Returns (pyramid_oereb.core.records.office.OfficeRecord): the updated master record.
    """

    master.name = merge_attribute(master.name, merger.name)
    master.office_at_web = merge_attribute(master.office_at_web, merger.office_at_web)
    return master


def merge_document_type(master, merger):
    """
    Merge multiple ``DocumentTypeRecord`` to one. While processing ÖREBlex there can occur different versions
    of the same document type in different languages. We try to solve that problem here.

    Args:
        master (pyramid_oereb.core.records.document_types.DocumentTypeRecord): The record all date will be
            added to.
        merger (pyramid_oereb.core.records.document_types.DocumentTypeRecord): The record all date will be
            taken from.
    Returns (pyramid_oereb.core.records.document_types.DocumentTypeRecord): the updated master record.
    """

    master.title = merge_attribute(master.title, merger.title)
    return DocumentTypeRecord(master.code, master.title)


def merge_document(master, merger):
    """
    Merge multiple ``DocumentRecord`` to one. While processing ÖREBlex there can occur different versions
    of the same document in different languages. We try to solve that problem here.

    Args:
        master (pyramid_oereb.core.records.documents.DocumentRecord): The record all date will be added to.
        merger (pyramid_oereb.core.records.documents.DocumentRecord): The record all date will be taken from.
    Returns (pyramid_oereb.core.records.documents.DocumentRecord): the updated master record.
    """
    master.document_type = merge_document_type(master.document_type, merger.document_type)
    master.law_status = LawStatusRecord(master.law_status.code, master.law_status.title)
    master.responsible_office = merge_office(master.responsible_office, merger.responsible_office)
    master.title = merge_attribute(master.title, merger.title)
    master.text_at_web = merge_attribute(master.text_at_web, merger.text_at_web)
    master.abbreviation = merge_attribute(master.abbreviation, merger.abbreviation)
    master.official_number = merge_attribute(master.official_number, merger.official_number)
    return master


def make_office_at_web_multilingual(documents, language):
    """
    ÖEREBlex offers multilingual elements via different URLS. With this method we combine all available
    languages into one multilingual element.

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
    """
    Interface method to ``pyramid_oereb``. It utilizes the lib to obtain a set of records from ÖREBlex.

    Args:
        geolink_id (int): The geoLink ID (lexlink ID).
        theme_code (str): The theme code matching the ``pyramid_oereb`` configuration.
        pyramid_oereb_config_path (str): The configuration yaml file path.
        pyramid_config_section (str): The section within the yaml file.
        source_class_path (str): The point separated path to the class which is used to produce the document
            records (Default: ``geolink2oereb.lib.interfaces.pyramid_oereb.OEREBlexSourceCustom``).
        c2ctemplate_style (bool): If set to true, c2c.template library will be used
            to load config file (Default: False).

    Returns:
        list of pyramid_oereb.core.records.documents.DocumentRecord: The collected and corrected
            documents, with types and offices.
    """
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
