from geolink2oereb.lib.interfaces.oerebkrmtrsfr.v2_0.classes import LocalisationCH_V1_MultilingualText
from geolink2oereb.lib.interfaces.oerebkrmtrsfr.v2_0.generators import multilingual_text_from_dict


def test_multilingual_text_from_dict():
    result = multilingual_text_from_dict({'de': 'Hallo', 'en': 'Hello'})
    assert isinstance(result, LocalisationCH_V1_MultilingualText)
