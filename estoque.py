"""API local de estoque com dados fictícios."""
import json
import sqlite3
from contextlib import closing
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


def initialize(db):
    with closing(sqlite3.connect(db)) as connection, connection:
        connection.executescript("""
            CREATE TABLE IF NOT EXISTS products (
                sku TEXT PRIMARY KEY, quantity INTEGER CHECK (quantity >= 0)
            );
            CREATE TABLE IF NOT EXISTS movements (
                id INTEGER PRIMARY KEY, sku TEXT, delta INTEGER, balance INTEGER
            );
            INSERT OR IGNORE INTO products VALUES ('CABO-01', 10);
        """)


def move(db, sku, delta):
    with closing(sqlite3.connect(db)) as connection, connection:
        connection.execute("BEGIN IMMEDIATE")
        product = connection.execute(
            "SELECT quantity FROM products WHERE sku = ?", (sku,)
        ).fetchone()
        if product is None:
            return 404, {"erro": "produto_nao_encontrado"}
        balance = product[0] + delta
        if balance < 0:
            return 409, {"erro": "estoque_insuficiente", "saldo": product[0]}
        connection.execute("UPDATE products SET quantity = ? WHERE sku = ?", (balance, sku))
        connection.execute(
            "INSERT INTO movements (sku, delta, balance) VALUES (?, ?, ?)",
            (sku, delta, balance),
        )
        return 201, {"sku": sku, "saldo": balance}


class Handler(BaseHTTPRequestHandler):
    def respond(self, status, data):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        queries = {
            "/produtos": "SELECT sku, quantity FROM products ORDER BY sku",
            "/movimentos": "SELECT sku, delta, balance FROM movements ORDER BY id",
        }
        query = queries.get(self.path)
        if query is None:
            self.respond(404, {"erro": "rota_nao_encontrada"})
            return
        with closing(sqlite3.connect(self.server.db)) as connection:
            connection.row_factory = sqlite3.Row
            rows = connection.execute(query).fetchall()
        self.respond(200, [dict(row) for row in rows])

    def do_POST(self):
        if self.path != "/movimentos":
            self.respond(404, {"erro": "rota_nao_encontrada"})
            return
        try:
            length = int(self.headers.get("Content-Length", 0))
            if not 0 < length <= 4096:
                raise ValueError
            data = json.loads(self.rfile.read(length))
            if not isinstance(data, dict):
                raise ValueError
            sku, delta = data.get("sku"), data.get("quantidade")
            if not isinstance(sku, str) or not sku.strip():
                raise ValueError
            if type(delta) is not int or not 0 < abs(delta) <= 1_000_000:
                raise ValueError
        except ValueError:
            self.respond(400, {"erro": "sku_e_quantidade_inteira_nao_zero_obrigatorios"})
            return
        self.respond(*move(self.server.db, sku.strip(), delta))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", default="estoque.db")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    initialize(args.db)
    with ThreadingHTTPServer(("127.0.0.1", args.port), Handler) as server:
        server.db = args.db
        print(f"API local: http://127.0.0.1:{server.server_port}", flush=True)
        server.serve_forever()
