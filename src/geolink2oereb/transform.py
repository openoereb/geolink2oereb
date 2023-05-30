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
    """
    Lads documents from ÖREBlex and transforms it to OeREBKRMtrsfr objects.

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
    c2ctemplate_style=False,
):
    """
    Lads documents from ÖREBlex and transforms it to OeREBKRMtrsfr objects.

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
