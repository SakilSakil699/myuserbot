from core.session_vault import SessionVault

# Original session (from env)
_raw_session = os.getenv("SESSION_STRING", "")

# If encrypted (starts with 'gAAAAA'), decrypt
if _raw_session.startswith("gAAAAA"):
    SESSION_STRING = SessionVault().unlock(_raw_session)
else:
    SESSION_STRING = _raw_session