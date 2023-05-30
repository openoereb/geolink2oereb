import re
from glob import glob
import os
from os.path import splitext, basename

from setuptools import setup, find_packages
import sys
sys.path.insert(0, os.path.abspath(os.path.join('src')))
from geolink2oereb import __version__

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.md')) as f:
    readme = f.read()
with open(os.path.join(here, 'CHANGELOG.md')) as f:
    changelog = f.read()

with open(os.path.join(here, 'requirements.txt')) as f:
    re_ = a = re.compile(r'(.+)==')
    recommend = f.read().splitlines()
    requires = [re_.match(r).group(1) for r in recommend]

tests_require = [
    'WebTest >= 1.3.1',  # py3 compat
    'pytest',  # includes virtualenv
    'pytest-cov'
]

setup(
    name='geolink2oereb',
    version=__version__,
    description='Transforms a geolink to OeREBKRMtrsfr_V2_0 document entities',
    license='BSD',
    long_description='{readme}\n\n{changelog}'.format(readme=readme, changelog=changelog),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: GIS",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    author='Clemens Rudert',
    author_email='rudert-geoinformatik@posteo.ch',
    url='https://github.com/openoereb/geolink2oereb',
    keywords='oereb lex geolink formatter html OeREBKRMtrsfr_V2_0',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    include_package_data=True,
    zip_safe=False,
    extras_require={
        'recommend': recommend,
        'no-version': requires,
        'testing': tests_require,
    },
    entry_points={
        'console_scripts': [
            'load_documents = geolink2oereb.cli.load_documents'
        ]
    }
)
