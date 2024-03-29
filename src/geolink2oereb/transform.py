"""
The basic entry module. It offers methods to be used right away:

* run
* run_batch
"""

from uuid import uuid4
from geolink2oereb.lib.interfaces.pyramid_oereb import load
from geolink2oereb.lib.interfaces.oerebkrmtrsfr.v2_0.generators import (
    document_record_to_oerebkrmtrsfr,
)


def run(
    geolink_id,
    theme_code,
    pyramid_oereb_config_path,
    section,
    source_class_path="geolink2oereb.lib.interfaces.pyramid_oereb.OEREBlexSourceCustom",
    c2ctemplate_style=False,
):
    """Loads documents from one ÖREBlex geolink and transforms it to OeREBKRMtrsfr objects.

    Args:
        geolink_id (int): The lexlink/geolink of the ÖREBlex document to download.
        theme_code (str): The theme code which is used to read the ÖREBlex specific config from the
            pyramid_oereb yml configuration.
        pyramid_oereb_config_path (str): The absolute path to the pyramid_oereb yml configuration file.
        section (str): The section inside the yml configuration where the pyramid_oereb configuration can be
            found.
        source_class_path (str): The pythonic dotted path to the ÖREBlex Source class definition which is used
            to construct pyramid_oereb DocumentRecords.
        c2ctemplate_style (bool): If the C2C way of parsing a yml should be used or not.

    Returns:
        list of geolink2oereb.lib.interfaces.oerebkrmtrsfr.v2_0.classes.OeREBKRM_V2_0_Dokumente_Dokument
    """
    document_records = load(
        geolink_id,
        theme_code,
        pyramid_oereb_config_path,
        section,
        source_class_path,
        c2ctemplate_style,
    )
    return [document_record_to_oerebkrmtrsfr(record) for record in document_records]


def run_batch(
    geolink_ids,
    theme_code,
    pyramid_oereb_config_path,
    section,
    source_class_path="geolink2oereb.lib.interfaces.pyramid_oereb.OEREBlexSourceCustom",
    c2ctemplate_style=False
):
    """
    Loads documents from multiple ÖREBlex geolinks and transforms it to OeREBKRMtrsfr objects.

    Args:
        geolink_id (list of int): A list of the lexlinks/geolinks of the ÖREBlex document to download.
        theme_code (str): The theme code which is used to read the ÖREBlex specific config from the
            pyramid_oereb yml configuration.
        pyramid_oereb_config_path (str): The absolute path to the pyramid_oereb yml configuration file.
        section (str): The section inside the yml configuration where the pyramid_oereb configuration can be
            found.
        source_class_path (str): The pythonic dotted path to the ÖREBlex Source class definition which is used
            to construct pyramid_oereb DocumentRecords.
        c2ctemplate_style (bool): If the C2C way of parsing a yml should be used or not.

    Returns:
        list of geolink2oereb.lib.interfaces.oerebkrmtrsfr.v2_0.classes.OeREBKRM_V2_0_Dokumente_Dokument
    """
    gathered = []
    for geolink_id in geolink_ids:
        gathered = gathered + run(
            geolink_id,
            theme_code,
            pyramid_oereb_config_path,
            section,
            source_class_path,
            c2ctemplate_style,
        )
    return gathered


def unify_gathered(gathered):
    """add docs

    Args:
        gathered (list):
            consists of (tuple):
                geolink2oereb.lib.interfaces.oerebkrmtrsfr.v2_0.classes.OeREBKRM_V2_0_Dokumente_Dokument:
                    The Dokument
                geolink2oereb.lib.interfaces.oerebkrmtrsfr.v2_0.classes.OeREBKRM_V2_0_Amt_Amt:
                    The Amt
    Returns:
        (tuple): tuple containing:
            list of geolink2oereb.lib.interfaces.oerebkrmtrsfr.v2_0.classes.OeREBKRM_V2_0_Dokumente_Dokument:
                The list of unified Dokumente.
            list of geolink2oereb.lib.interfaces.oerebkrmtrsfr.v2_0.classes.OeREBKRM_V2_0_Amt_Amt:
                The list of unified Ämter.
    """
    unique_amt_tids = []
    unique_amt = []
    unique_dokument_tids = []
    unique_dokument = []
    for dokument, amt in gathered:
        if str(amt) not in unique_amt_tids:
            unique_amt_tids.append(str(amt))
            unique_amt.append(amt)
        if dokument.TID not in unique_dokument_tids:
            unique_dokument_tids.append(dokument.TID)
            unique_dokument.append(dokument)
    return unique_dokument, unique_amt


def assign_uuids(unique_dokumente, unique_aemter):
    """
    Assigns UUIDs to a list of unique Aemter and Dokumente. It needs the lists to be in predefined order
    to match the correct objects.

    Args:
        unique_dokumente (list of geolink2oereb.lib.interfaces.oerebkrmtrsfr.v2_0.classes.OeREBKRM_V2_0_Dokumente_Dokument):  # noqa: E501
            List of unique dokumente where each dokument should receive a UUID.
        unique_aemter (list of geolink2oereb.lib.interfaces.oerebkrmtrsfr.v2_0.classes.OeREBKRM_V2_0_Amt_Amt):
            List of unique aemter where each amt should receive a UUID.
    Returns:
        (tuple): tuple containing:
            list of geolink2oereb.lib.interfaces.oerebkrmtrsfr.v2_0.classes.OeREBKRM_V2_0_Dokumente_Dokument:
                The list of unique Dokumente where each Dokument has a valid UUID assigned.
            list of geolink2oereb.lib.interfaces.oerebkrmtrsfr.v2_0.classes.OeREBKRM_V2_0_Amt_Amt):
                The list of unique Ämter where each Amt has a valid UUID assigned.
    """
    uuid_aemter = []
    uuid_dokumente = []
    for amt in unique_aemter:
        new_amt_uuid = str(uuid4())
        for dokument in unique_dokumente:
            if dokument.ZustaendigeStelle.REF == str(amt):
                dokument.ZustaendigeStelle.set_REF(new_amt_uuid)
                uuid_dokumente.append(dokument)
                dokument.set_TID(str(uuid4()))
        amt.set_TID(new_amt_uuid)
        uuid_aemter.append(amt)
    return uuid_dokumente, uuid_aemter
