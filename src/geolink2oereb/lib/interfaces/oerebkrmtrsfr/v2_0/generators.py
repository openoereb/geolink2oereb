"""
This interface offers methods to access python classes matching the ``OeREBKRMtrsfr_V2_0`` INTERLIS model. It
is used mainly for translation and handling between ``pyramid_oereb`` and ``OeREBKRMtrsfr_V2_0``.
"""

import logging
from geolink2oereb.lib.interfaces.oerebkrmtrsfr.v2_0.classes import (
    OeREBKRM_V2_0_Dokumente_Dokument,
    LocalisationCH_V1_MultilingualText,
    LocalisationCH_V1_LocalisedText,
    LocalisedTextType,
    OeREBKRM_V2_0_Amt_Amt,
    ZustaendigeStelleType,
    TitelType,
    LocalisedTextType86,
    OeREBKRM_V2_0_LocalisedUri,
    TextImWebType,
    OeREBKRM_V2_0_MultilingualUri
)

logging.basicConfig(level="DEBUG", format="%(asctime)s [%(levelname)s] %(message)s")


def fix_url(url):
    """
    Helper method to hotfix an often occurring problem with urls not being valid in the ili sense. The URLs
    out of ÖREBlex are missing the http/https part often. So we try to fix this on the fly.

    Args:
        url (str): The URL string which might be fixed.

    Returns:
        The maybe fixed URL.
    """
    if not url.startswith('http'):
        new_url = 'https://{}'.format(url)
        logging.info(f"Fixing url from {url} to {new_url}")
        return new_url
    return url


def multilingual_text_from_dict(multilingual_dict):
    """
    Produces a MultilingualText object out of a dict in the form:

    .. code-block:: python

        {
          "de": "Test",
          "it": "Testo"
        }

    Args:
        multilingual_dict (dict or None): The definition of the multilingual element or None.

    Returns:
        geolink2oereb.lib.interfaces.oerebkrmtrsfr.v2_0.classes.TitelType
    """

    if multilingual_dict is None:
        return multilingual_dict
    localized_texts = LocalisedTextType()
    for language in multilingual_dict:
        localized_texts.LocalisationCH_V1_LocalisedText.append(
            LocalisationCH_V1_LocalisedText(language, multilingual_dict[language])
        )
    return TitelType(LocalisationCH_V1_MultilingualText(localized_texts))


def multilingual_uri_from_dict(multilingual_dict):
    """
    Produces a MultilingualText object out of a dict in the form:

    .. code-block:: python

        {
          "de": "Test",
          "it": "Testo"
        }

    Args:
        multilingual_dict (dict or None): The definition of the multilingual element or None.

    Returns:
        geolink2oereb.lib.interfaces.oerebkrmtrsfr.v2_0.classes.TextImWebType
    """
    if multilingual_dict is None:
        return multilingual_dict
    localized_texts = LocalisedTextType86()
    for language in multilingual_dict:
        localized_texts.OeREBKRM_V2_0_LocalisedUri.append(
            OeREBKRM_V2_0_LocalisedUri(language, fix_url(multilingual_dict[language]))
        )
    return TextImWebType(OeREBKRM_V2_0_MultilingualUri(localized_texts))


def office_record_to_oerebkrmtrsfr(office_record):
    """
    Translates a ``pyramid_oereb`` office record object to an OeREBKRM_V2_0_Amt_Amt object.

    Args:
        office_record (pyramid_oereb.core.records.office.OfficeRecord): The office record to translate.
    Returns:
        geolink2oereb.lib.interfaces.oerebkrmtrsfr.v2_0.classes.OeREBKRM_V2_0_Amt_Amt
    """
    amt = OeREBKRM_V2_0_Amt_Amt(
        Name=multilingual_text_from_dict(office_record.name),
        AmtImWeb=multilingual_uri_from_dict(office_record.office_at_web),
        UID=office_record.uid,
        Zeile1=office_record.line1,
        Zeile2=office_record.line2,
        Strasse=office_record.street,
        Hausnr=office_record.number,
        PLZ=office_record.postal_code,
        Ort=office_record.city,
    )
    return amt


def document_record_to_oerebkrmtrsfr(document_record):
    """
    Translates a ``pyramid_oereb`` document record object to an OeREBKRM_V2_0_Dokumente_Dokument object.

    Args:
        document_record (pyramid_oereb.core.records.documents.DocumentRecord): The record to translate.

    Returns:
        (tuple): tuple containing:

            geolink2oereb.lib.interfaces.oerebkrmtrsfr.v2_0.classes.OeREBKRM_V2_0_Amt_Amt:
                The office which belongs to the document (responsible office).
            geolink2oereb.lib.interfaces.oerebkrmtrsfr.v2_0.classes.OeREBKRM_V2_0_Dokumente_Dokument:
                The document.
    """
    amt = office_record_to_oerebkrmtrsfr(document_record.responsible_office)
    dokument = OeREBKRM_V2_0_Dokumente_Dokument(
        Typ=document_record.document_type.code,
        Titel=multilingual_text_from_dict(document_record.title),
        Abkuerzung=multilingual_text_from_dict(document_record.abbreviation),
        OffizielleNr=multilingual_text_from_dict(document_record.official_number),
        NurInGemeinde=document_record.only_in_municipality,
        TextImWeb=multilingual_uri_from_dict(document_record.text_at_web),
        # Dokument=multilingual_text_from_dict(document_record.file),
        AuszugIndex=document_record.index,
        Rechtsstatus=document_record.law_status.code,
        publiziertAb=document_record.published_from,
        publiziertBis=document_record.published_until,
        ZustaendigeStelle=ZustaendigeStelleType(REF=str(amt))
    )
    dokument.set_TID(str(dokument))
    return dokument, amt
