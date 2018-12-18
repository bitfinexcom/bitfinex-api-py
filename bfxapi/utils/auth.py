"""
This module is used to house all of the functions which are used
to handle the http authentication of the client
"""

import hashlib
import hmac
import time

def generate_auth_payload(API_KEY, API_SECRET):
  """
  Generate a signed payload

  @return json Oject headers
  """
  nonce = _gen_nonce()
  authMsg, sig = _gen_signature(API_KEY, API_SECRET, nonce)

  return {
    'apiKey': API_KEY,
    'authSig': sig,
    'authNonce': nonce,
    'authPayload': authMsg,
    'event': 'auth'
  }

def generate_auth_headers(API_KEY, API_SECRET, path, body):
  """
  Generate headers for a signed payload
  """
  nonce = str(_gen_nonce())
  signature = "/api/v2/{}{}{}".format(path, nonce, body)
  h = hmac.new(API_SECRET.encode('utf8'), signature.encode('utf8'), hashlib.sha384)
  signature = h.hexdigest()

  return {
    "bfx-nonce": nonce,
    "bfx-apikey": API_KEY,
    "bfx-signature": signature
  }

def _gen_signature(API_KEY, API_SECRET, nonce):
  authMsg = 'AUTH{}'.format(nonce)
  secret = API_SECRET.encode('utf8')
  sig = hmac.new(secret, authMsg.encode('utf8'), hashlib.sha384).hexdigest()

  return authMsg, sig

def _gen_nonce():
  return int(round(time.time() * 1000000))
