from geolink2oereb.lib.interfaces.oerebkrmtrsfr.v2_0.classes import (
    OeREBKRM_V2_0_Dokumente_Dokument,
    LocalisationCH_V1_MultilingualText,
    LocalisationCH_V1_LocalisedText,
    LocalisedTextType,
    OeREBKRM_V2_0_Amt_Amt,
)


def multilingual_text_from_dict(multilingual_dict):
    localized_texts = LocalisedTextType()
    for language in multilingual_dict:
        localized_texts.LocalisationCH_V1_LocalisedText.append(
            LocalisationCH_V1_LocalisedText(language, multilingual_dict[language])
        )
    return LocalisationCH_V1_MultilingualText(localized_texts)


def office_record_to_oerebkrmtrsfr(office_record):
    """

    Args:
        office_record (pyramid_oereb.core.records.office.OfficeRecord): The office record to translate.
    Returns:
        geolink2oereb.lib.interfaces.oerebkrmtrsfr.v2_0.classes.OeREBKRM_V2_0_Amt_Amt
    """
    return OeREBKRM_V2_0_Amt_Amt(
        Name=multilingual_text_from_dict(office_record.name),
        AmtImWeb=multilingual_text_from_dict(office_record.office_at_web),
        UID=office_record.uid,
        Zeile1=office_record.line1,
        Zeile2=office_record.line2,
        Strasse=office_record.street,
        Hausnr=office_record.number,
        PLZ=office_record.postal_code,
        Ort=office_record.city,
    )


def document_record_to_oerebkrmtrsfr(document_record):
    """

    Args:
        document_record (pyramid_oereb.core.records.documents.DocumentRecord): The record to translate.

    Returns:
        geolink2oereb.lib.interfaces.oerebkrmtrsfr.v2_0.classes.OeREBKRM_V2_0_Dokumente_Dokument
    """

    return OeREBKRM_V2_0_Dokumente_Dokument(
        Typ=document_record.document_type.code,
        Titel=multilingual_text_from_dict(document_record.title),
        Abkuerzung=document_record.abbreviation,
        OffizielleNr=multilingual_text_from_dict(document_record.official_number),
        NurInGemeinde=document_record.only_in_municipality,
        TextImWeb=multilingual_text_from_dict(document_record.text_at_web),
        # Dokument=multilingual_text_from_dict(document_record.file),
        AuszugIndex=document_record.index,
        Rechtsstatus=document_record.law_status.code,
        publiziertAb=document_record.published_from,
        publiziertBis=document_record.published_until,
        ZustaendigeStelle=office_record_to_oerebkrmtrsfr(document_record.responsible_office),
    )
