from distutils.core import setup

setup(
    name="bitfinex-api-py",
    version="3.0.0",
    packages=[ "bfxapi", "bfxapi.websocket", "bfxapi.rest", "bfxapi.utils" ],
    url="https://github.com/bitfinexcom/bitfinex-api-py",
    license="OSI Approved :: Apache Software License",
    author="Bitfinex",
    author_email="support@bitfinex.com",
    description="Official Bitfinex Python API",
    keywords="bitfinex,api,trading",
    install_requires=[
        "certifi~=2022.12.7",
        "charset-normalizer~=2.1.1",
        "idna~=3.4",
        "mypy~=0.991",
        "mypy-extensions~=0.4.3",
        "pyee~=9.0.4",
        "requests~=2.28.1",
        "tomli~=2.0.1",
        "types-requests~=2.28.11.5",
        "types-urllib3~=1.26.25.4",
        "typing_extensions~=4.4.0",
        "urllib3~=1.26.13",
        "websockets~=10.4",
    ],
    project_urls={
        "Bug Reports": "https://github.com/bitfinexcom/bitfinex-api-py/issues",
        "Source": "https://github.com/bitfinexcom/bitfinex-api-py",
    }
)