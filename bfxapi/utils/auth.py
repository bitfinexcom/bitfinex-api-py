"""
This module is used to house all of the functions which are used
to handle the http authentication of the client
"""

import hashlib
import hmac
import time
from ..models import Order

def generate_auth_payload(API_KEY, API_SECRET):
  """
  Generate a signed payload

  @return json Object headers
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

def gen_unique_cid():
  return int(round(time.time() * 1000))

def calculate_order_flags(hidden, close, reduce_only, post_only, oco):
  flags = 0
  flags = flags + Order.Flags.HIDDEN if hidden else flags
  flags = flags + Order.Flags.CLOSE if close else flags
  flags = flags + Order.Flags.REDUCE_ONLY if reduce_only else flags
  flags = flags + Order.Flags.POST_ONLY if post_only else flags
  flags = flags + Order.Flags.OCO if oco else flags
  return flags
