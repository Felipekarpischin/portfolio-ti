"""Compara contagem física e saldo registrado e gera relatório de divergências."""
import argparse
import csv


def read_stock(path):
    stock = {}
    with open(path, encoding="utf-8-sig", newline="") as source:
        rows = csv.DictReader(source)
        if not {"sku", "quantidade"} <= set(rows.fieldnames or []):
            raise ValueError(f"{path}: colunas esperadas: sku, quantidade.")
        for row in rows:
            sku = row["sku"].strip().upper()
            quantity = int(row["quantidade"])
            if not sku or sku in stock or quantity < 0:
                raise ValueError(f"{path}:{rows.line_num}: SKU vazio, duplicado ou saldo negativo.")
            stock[sku] = quantity
    return stock


def reconcile(system, physical):
    for sku in sorted(system.keys() | physical.keys()):
        if sku not in system:
            yield sku, "", physical[sku], "", "ausente_no_sistema"
        elif sku not in physical:
            yield sku, system[sku], "", "", "sem_contagem"
        elif system[sku] != physical[sku]:
            yield sku, system[sku], physical[sku], physical[sku] - system[sku], "divergente"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sistema")
    parser.add_argument("contagem")
    parser.add_argument("relatorio")
    args = parser.parse_args()
    try:
        differences = list(reconcile(read_stock(args.sistema), read_stock(args.contagem)))
        with open(args.relatorio, "x", encoding="utf-8-sig", newline="") as target:
            writer = csv.writer(target)
            writer.writerow(["sku", "sistema", "contagem", "diferenca", "status"])
            writer.writerows(differences)
    except (OSError, ValueError, AttributeError, TypeError) as error:
        parser.exit(2, f"Não foi possível gerar o relatório: {error}\n")
    print(f"{len(differences)} divergência(s). Relatório: {args.relatorio}")
