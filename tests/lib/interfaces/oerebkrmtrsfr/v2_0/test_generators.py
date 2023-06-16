from geolink2oereb.lib.interfaces.oerebkrmtrsfr.v2_0.classes import TitelType
from geolink2oereb.lib.interfaces.oerebkrmtrsfr.v2_0.generators import multilingual_text_from_dict


def test_multilingual_text_from_dict():
    result = multilingual_text_from_dict({'de': 'Hallo', 'en': 'Hello'})
    assert isinstance(result, TitelType)
