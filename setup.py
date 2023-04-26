from distutils.core import setup

version = {}
with open("bfxapi/version.py", encoding="utf-8") as fp:
    exec(fp.read(), version) #pylint: disable=exec-used

setup(
    name="bitfinex-api-py",
    version=version["__version__"],
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

        "License :: OSI Approved :: Apache Software License",

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
        "pyee~=9.0.4",
        "websockets~=10.4",
        "requests~=2.28.1"
    ],
    python_requires=">=3.8"
)
