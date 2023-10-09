
CLI
===

The command line interface of geolink2oereb.

Once installed as python package geolink2oereb offers a command line
interface to issue the transformation of one lexlink id to the
OEREB transfer structure. To get info about the parameters the cli programm
needs, you can issue the execution as follows:

.. code-block:: shell

  load_documents --help

You can call the tool like this:

.. code-block:: shell

  load_documents -l 4304 -t ch.Planungszonen -p <absolute-path-to-your-config>/config.yaml

Please keep in mind, that the binary executable is available only in the
python path where you installed it. If you installed it with
a VENV you might prefix it with the path to you VENV's bin directory.

