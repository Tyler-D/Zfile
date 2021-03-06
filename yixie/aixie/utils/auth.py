#!/usr/bin/env python
# -*- coding: utf-8 -*-

import simplejson as json
from aixie.utils import crypto

# crypto
import hashlib
import base64
import datetime
import time
import pickle

# auth
def get_hashed_password(password, salt):
    """hashing with salt included
    """
    result_hash = hashlib.sha512(password.encode('utf-8') +
            salt.encode('utf-8'))
    return base64.urlsafe_b64encode(result_hash.digest())

# auth
def is_password_match(hashed_password, password, salt):
    return get_hashed_password(password, salt) == hashed_password

# auth
def create_token(userid):
    token_obj = {
            'time': time.time(),
            'userid': userid,
            'uuid': crypto.get_base64_uuid4()
            }

    json_token = str(json.dumps(token_obj))
    token = base64.urlsafe_b64encode(json_token)
    return token

# auth
def decode_token(token):
    json_token = base64.urlsafe_b64decode(token)
    token_obj = json.loads(json_token)
    return token_obj

# auth
def is_token_expired(token, token_lifetime):
    time_created = get_token_time(token)
    if (datetime.datetime.now() - time_created).microseconds > token_lifetime:
        return False
    return True

# auth
def get_token_time(token):
    token_obj = decode_token(token)
    return datetime.datetime.fromtimestamp(token_obj['time'])
