from distutils.core import setup

setup(
    name="bitfinex-api-py",
    version="3.0.0b1",
    description="Official Bitfinex Python API",
    long_description="A Python reference implementation of the Bitfinex API for both REST and websocket interaction",
    long_description_content_type="text/markdown",
    url="https://github.com/bitfinexcom/bitfinex-api-py",
    author="Bitfinex",
    author_email="support@bitfinex.com",
    license="Apache-2.0",
    classifiers=[
        "Development Status :: 4 - Beta",

        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",

        "License :: OSI Approved :: Apache-2.0",

        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    keywords="bitfinex,api,trading",
    project_urls={
        "Bug Reports": "https://github.com/bitfinexcom/bitfinex-api-py/issues",
        "Source": "https://github.com/bitfinexcom/bitfinex-api-py",
    },
    packages=[ 
        "bfxapi", "bfxapi.utils",
        "bfxapi.websocket", "bfxapi.websocket.client", "bfxapi.websocket.handlers", 
        "bfxapi.rest", "bfxapi.rest.endpoints", "bfxapi.rest.middleware",
    ],
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
    python_requires=">=3.8"
)