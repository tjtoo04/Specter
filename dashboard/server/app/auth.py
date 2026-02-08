import os
from propelauth_fastapi import init_auth

PROPEL_AUTH_URL = os.getenv("PROPEL_AUTH_URL")
PROPEL_AUTH_API_KEY = os.getenv("PROPEL_AUTH")

if not PROPEL_AUTH_URL or not PROPEL_AUTH_API_KEY:
    raise RuntimeError("Missing PropelAuth environment variables!")

auth = init_auth(PROPEL_AUTH_URL, PROPEL_AUTH_API_KEY)
