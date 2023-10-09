Basic info
==========


This is a small library, meant to be used in combination with an *OEREBlex* instance.
It is capable of parsing a received *lexlink* response (XML) and transforming it to the
`OeREBKRMtrsfr_V2_0 <https://models.geo.admin.ch/V_D/OeREB/OeREBKRMtrsfr_V2_0.ili>`_ structure for further
usage.

To make the configuration more easy it is using the pyramid_oereb library to reuse the
complex ÖREBlex
`configuration <https://github.com/openoereb/pyramid_oereb/blob/master/dev/config/pyramid_oereb.yml.mako#L185-L223>`_
and ÖREBlex
`parsing <https://github.com/openoereb/pyramid_oereb/blob/master/pyramid_oereb/contrib/data_sources/oereblex/sources/document.py>`_
already developed there.

For development and integration purposes geolink2oereb offers a :ref:`CLI` executable. But its
main use case is to be utilized as a library in another python libraries context.

See the mgdm2oereb implementation as an example:

`mgdm2oereb => oereblex.geolink2oereb <https://github.com/openoereb/mgdm2oereb/blob/master/xsl/oereblex.geolink2oereb.py>`_

