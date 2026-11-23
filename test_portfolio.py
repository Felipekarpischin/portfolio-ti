"""Testes do fluxo HTTP e da validação do relatório de suporte."""
import importlib.util
import json
import tempfile
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from estoque import Handler, ThreadingHTTPServer, initialize

triage_path = Path(__file__).parent / "suporte/triagem-http/triagem.py"
spec = importlib.util.spec_from_file_location("triagem", triage_path)
triage = importlib.util.module_from_spec(spec)
spec.loader.exec_module(triage)


class StockTests(unittest.TestCase):
    def setUp(self):
        folder = self.enterContext(tempfile.TemporaryDirectory())
        self.server = self.enterContext(ThreadingHTTPServer(("127.0.0.1", 0), Handler))
        self.server.db = Path(folder) / "test.db"
        initialize(self.server.db)
        worker = threading.Thread(target=self.server.serve_forever)
        worker.start()
        self.addCleanup(worker.join)
        self.addCleanup(self.server.shutdown)

    def request(self, route, payload=None):
        body = None if payload is None else json.dumps(payload).encode()
        request = Request(f"http://127.0.0.1:{self.server.server_port}{route}", data=body)
        try:
            response = urlopen(request, timeout=5)
        except HTTPError as error:
            response = error
        with response:
            return response.code, json.load(response)

    def test_rejected_movement_preserves_stock_and_history(self):
        self.assertEqual(self.request("/movimentos", {"sku": "CABO-01", "quantidade": -12})[0], 409)
        self.assertEqual(self.request("/movimentos"), (200, []))
        self.assertEqual(self.request("/produtos")[1][0]["quantity"], 10)

    def test_invalid_payload_and_unknown_sku(self):
        self.assertEqual(self.request("/movimentos", {"sku": "CABO-01", "quantidade": True})[0], 400)
        self.assertEqual(self.request("/movimentos", {"sku": "INEXISTENTE", "quantidade": 1})[0], 404)

    def test_concurrent_withdrawals_allow_only_one(self):
        payload = {"sku": "CABO-01", "quantidade": -7}
        with ThreadPoolExecutor(max_workers=2) as pool:
            requests = [pool.submit(self.request, "/movimentos", payload) for _ in range(2)]
        self.assertEqual(sorted(request.result()[0] for request in requests), [201, 409])
        initialize(self.server.db)
        self.assertEqual(self.request("/produtos")[1][0]["quantity"], 3)
        self.assertEqual(self.request("/movimentos")[1], [{"sku": "CABO-01", "delta": -7, "balance": 3}])


class TriageTests(unittest.TestCase):
    def test_classifies_slow_errors_and_timeouts(self):
        rows = [
            {"status": "200", "latency_ms": "800"},
            {"status": "503", "latency_ms": "90"},
            {"status": "0", "latency_ms": "2500"},
        ]
        self.assertEqual(triage.analyze(rows, 800), (3, 1, 1, 1, 800))

    def test_rejects_invalid_measurements(self):
        for status, latency in [("999", "100"), ("200", "-5"), ("200", None)]:
            with self.subTest(status=status, latency=latency):
                with self.assertRaisesRegex(ValueError, "Linha 2"):
                    triage.analyze([{"status": status, "latency_ms": latency}], 800)

    def test_rejects_negative_threshold(self):
        with self.assertRaisesRegex(ValueError, "limite"):
            triage.analyze([], -1)
