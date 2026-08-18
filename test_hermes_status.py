import sys
import types

fake_streamlit = types.ModuleType("streamlit")
sys.modules["streamlit"] = fake_streamlit

import hermes_engine

assert hermes_engine._status_ok({"success": True}) is True
assert hermes_engine._status_ok({"success": False, "skipped": True}) is True
assert hermes_engine._status_ok({"success": False, "skipped": False}) is False
assert hermes_engine._status_label({"success": False, "skipped": True, "detail": "não configurado"}).startswith("IGNORADO")
assert hermes_engine._status_label({"success": False, "error": "HTTP 401"}).startswith("FALHA")
print("HERMES_STATUS_TEST_OK")
