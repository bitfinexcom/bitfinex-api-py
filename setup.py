from distutils.core import setup

setup(
    name="bitfinex-api-py",
    version="3.0.2",
    description="Official Bitfinex Python API",
    long_description=(
        "A Python reference implementation of the Bitfinex API "
        "for both REST and websocket interaction."
    ),
    long_description_content_type="text/markdown",
    url="https://github.com/bitfinexcom/bitfinex-api-py",
    author="Bitfinex",
    author_email="support@bitfinex.com",
    license="Apache-2.0",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    keywords="bitfinex,api,trading",
    project_urls={
        "Bug Reports": "https://github.com/bitfinexcom/bitfinex-api-py/issues",
        "Source": "https://github.com/bitfinexcom/bitfinex-api-py",
    },
    packages=[
        "bfxapi",
        "bfxapi._utils",
        "bfxapi.types",
        "bfxapi.websocket",
        "bfxapi.websocket._client",
        "bfxapi.websocket._handlers",
        "bfxapi.websocket._event_emitter",
        "bfxapi.rest",
        "bfxapi.rest._interface",
        "bfxapi.rest._interfaces",
    ],
    install_requires=[
        "pyee~=9.0.4",
        "websockets~=11.0.3",
        "requests~=2.28.1",
        "urllib3~=1.26.14",
    ],
    python_requires=">=3.8",
)
