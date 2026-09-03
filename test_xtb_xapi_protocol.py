import ast
import json
from pathlib import Path

source = Path("monitor_app.py").read_text(encoding="utf-8")
tree = ast.parse(source)
selected = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in {"_xtb_error", "_xtb_request"}]
namespace = {"json": json}
exec(compile(ast.Module(body=selected, type_ignores=[]), "monitor_app.py", "exec"), namespace)

class FakeWebSocket:
    def __init__(self):
        self.sent = []
        self.responses = iter([
            '{"status":true,"streamSessionId":"session"}\n\n',
            '{"status":true,"returnData":{"bid":100.0,"ask":101.0}}\n\n',
        ])
        self.timeout = None

    def settimeout(self, timeout):
        self.timeout = timeout

    def send(self, payload):
        self.sent.append(json.loads(payload))

    def recv(self):
        return next(self.responses)

ws = FakeWebSocket()
login = namespace["_xtb_request"](ws, {"command": "login", "arguments": {"userId": "hidden", "password": "hidden"}})
tick = namespace["_xtb_request"](ws, {"command": "getTickPrices", "arguments": {"symbols": ["USDJPY"]}})
assert login["streamSessionId"] == "session"
assert tick["returnData"]["ask"] == 101.0
assert ws.timeout == 10
assert ws.sent[0]["command"] == "login"
assert ws.sent[1]["command"] == "getTickPrices"
print("xAPI request parser: OK")

import numpy as np
import pandas as pd

feature_node = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "strategy_features")
pressure_node = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "pressure_confluence")
ratings_node = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "technical_ratings")
vote_node = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "_vote")
label_node = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "_rating_label")
feature_namespace = {"np": np, "pd": pd}
exec(compile(ast.Module(body=[vote_node, label_node, feature_node, ratings_node, pressure_node], type_ignores=[]), "monitor_app.py", "exec"), feature_namespace)
index = pd.date_range("2026-01-01", periods=60, freq="h")
close = np.linspace(100.0, 112.0, 60)
data = pd.DataFrame({
    "time": index,
    "open": close - 0.4,
    "high": close + 0.8,
    "low": close - 0.8,
    "close": close,
    "volume": np.linspace(100.0, 220.0, 60),
})
pressure = feature_namespace["pressure_confluence"](data, 106.0, 109.0, 103.0)
assert -1.0 <= pressure["score"] <= 1.0
assert pressure["buy"] + pressure["sell"] == 100
assert set(pressure["components"]) == {"Resumo dos termômetros", "Osciladores", "Médias Móveis", "POC / Área de Valor", "Volume relativo"}
assert np.sign(pressure["score"]) == np.sign(pressure["summary_score"])
print("pressure confluence aligned with gauges: OK")
