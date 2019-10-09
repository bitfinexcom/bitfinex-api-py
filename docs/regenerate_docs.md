For development purposes, these are the commands used to generate the doc files.

Install pydocmd:

```
pip3 install pydoc-markdown
```

Generate REST V2 docs:

```
pydocmd simple bfxapi bfxapi.client+ bfxapi.rest.bfx_rest.BfxRest+ > ./docs/rest_v2.md
```

Generate Websocket V2 docs:

```
pydocmd simple bfxapi bfxapi.client+ bfxapi.websockets.bfx_websocket.BfxWebsocket+ > ./docs/ws_v2.md
```
