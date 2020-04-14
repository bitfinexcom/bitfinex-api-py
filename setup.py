"""A setuptools based setup module.
See:
https://packaging.python.org/guides/distributing-packages-using-setuptools/
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))
setup(
    name='bitfinex-api-py',
    version='1.1.6',
    description='Official Bitfinex Python API',
    long_description='A Python reference implementation of the Bitfinex API for both REST and websocket interaction',
    long_description_content_type='text/markdown',
    url='https://github.com/bitfinexcom/bitfinex-api-py',
    author='Bitfinex',
    author_email='support@bitfinex.com',
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 5 - Production/Stable',

        # Project Audience
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        # Project License
        'License :: OSI Approved :: Apache Software License',

        # Python versions (not enforced)
        'Programming Language :: Python :: 3.0',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    keywords='bitfinex,api,trading',
    packages=find_packages(exclude=['examples', 'tests', 'docs']),
    # Python versions (enforced)
    python_requires='>=3.0.0, <4',
    # deps installed by pip
    install_requires=['eventemitter', 'asyncio', 'websockets', 'pylint', 'six', 'pyee', 'aiohttp'],
    project_urls={
        'Bug Reports': 'https://github.com/bitfinexcom/bitfinex-api-py/issues',
        'Source': 'https://github.com/bitfinexcom/bitfinex-api-py',
    },
)
