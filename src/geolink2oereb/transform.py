from geolink2oereb.lib.interfaces.pyramid_oereb import load
from geolink2oereb.lib.interfaces.oerebkrmtrsfr.v2_0.generators import document_record_to_oerebkrmtrsfr


def run(
        geolink_id,
        theme_code,
        pyramid_oereb_config_path,
        section,
        source_class_path='geolink2oereb.lib.interfaces.pyramid_oereb.OEREBlexSourceCustom',
        c2ctemplate_style=False
):
    document_records = load(
        geolink_id,
        theme_code,
        pyramid_oereb_config_path,
        section,
        source_class_path,
        c2ctemplate_style
    )
    return [document_record_to_oerebkrmtrsfr(record) for record in document_records]


def run_batch(
        geolink_ids,
        theme_code,
        pyramid_oereb_config_path,
        section,
        source_class_path='geolink2oereb.lib.interfaces.pyramid_oereb.OEREBlexSourceCustom',
        c2ctemplate_style=False
):
    gathered = []
    for geolink_id in geolink_ids:
        gathered = gathered + run(
            geolink_id,
            theme_code,
            pyramid_oereb_config_path,
            section,
            source_class_path,
            c2ctemplate_style
        )
    return gathered
