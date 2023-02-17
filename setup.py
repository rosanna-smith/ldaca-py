from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'requirements.txt'), encoding='utf-8') as f:
    required = f.read().splitlines()

version = 'v1.0.0'

setup(
    name='ldaca',
    packages=find_packages(exclude=['test']),
    version=version,
    description='LDaCA API Wrapper',
    author=", ".join((
        'Moises Sacal Bonequi'
    )),
    python_requires='>=3.6',
    license="gplv2",
    url='https://github.com/Language-Research-Technology/ldaca-py.git',
    download_url=('https://github.com/Language-Research-Technology/ldaca-py/archive/'
                  f'{version}.tar.gz'),
    keywords="atap ldaca rocrates",
    install_requires=[required]
)
