import optparse
import logging
import uuid

from geolink2oereb.transform import run

logging.basicConfig(level="DEBUG", format="%(asctime)s [%(levelname)s] %(message)s")

log = logging.getLogger(__name__)


def geolink2oereb():
    parser = optparse.OptionParser(
        usage="usage: %prog [options]",
        description="Download all documents to a oereblex geolinkID",
    )
    parser.add_option(
        "-l",
        "--geolink_id",
        dest="geolink_id",
        metavar="GEOLINKID",
        type="integer",
        help="The the ID to load the documents for.",
    )
    parser.add_option(
        "-t",
        "--themecode",
        dest="theme_code",
        metavar="THEMECODE",
        type="string",
        help="The theme code which the documents are loaded for. That need to fit the passed pyramid_oereb"
             "config YML.",
    )
    parser.add_option(
        "-p",
        "--pyramid-oereb-config-path",
        dest="pyramid_oereb_config_path",
        help="The absolute path to the pyramid_oereb.yml config file to read all the settings for ÖREBlex "
             "and the translations of codes.",
    )
    parser.add_option(
        "-c",
        "--source-class-path",
        dest="source_class_path",
        metavar="SOURCECLASSPATH",
        type="string",
        default="geolink2oereb.lib.interfaces.pyramid_oereb.OEREBlexSourceCustom",
        help="The dotted python path to the class which is used for the ÖREBlex handling.",
    )
    parser.add_option(
        "-s",
        "--section",
        dest="section",
        metavar="SECTION",
        type="string",
        default="pyramid_oereb",
        help="The section which contains configuration (default is: pyramid_oereb).",
    )
    parser.add_option(
        "--c2ctemplate-style",
        dest="c2ctemplate_style",
        default=False,
        help="Is the yaml file using a c2ctemplate style (starting with vars)",
    )
    parser.add_option(
        "-o",
        "--outfile-path",
        dest="outfile_path",
        default=f"/tmp/{str(uuid.uuid4())}.xml",
        help="The absolute path where the output will be written to.",
    )

    options, args = parser.parse_args()
    oerebkrmtrsfr = run(
        options.geolink_id,
        options.theme_code,
        options.pyramid_oereb_config_path,
        options.section,
        options.source_class_path,
        options.c2ctemplate_style,
    )
    with open(options.outfile_path) as fh:
        for element in oerebkrmtrsfr:
            fh.write(str(element))
