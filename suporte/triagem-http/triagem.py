"""Resume ocorrências de um export CSV fictício de monitoramento HTTP."""
import argparse
import csv
import statistics


def analyze(rows, latency_limit):
    if latency_limit <= 0:
        raise ValueError("O limite em milissegundos deve ser positivo.")
    samples = []
    for line, row in enumerate(rows, start=2):
        try:
            status = int(row["status"])
            latency = int(row["latency_ms"])
        except (KeyError, TypeError, ValueError) as error:
            raise ValueError(f"Linha {line}: status e latency_ms devem ser inteiros.") from error
        if (status != 0 and not 100 <= status <= 599) or latency < 0:
            raise ValueError(f"Linha {line}: status inválido ou latência negativa.")
        samples.append((status, latency))
    if not samples:
        raise ValueError("O arquivo não contém medições.")
    errors = sum(500 <= status < 600 for status, _ in samples)
    timeouts = sum(status == 0 for status, _ in samples)
    slow = sum(latency >= latency_limit for status, latency in samples if status != 0)
    median = statistics.median(latency for _, latency in samples)
    return len(samples), errors, timeouts, slow, median


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv")
    parser.add_argument("--limite-ms", type=int, default=800)
    args = parser.parse_args()
    try:
        with open(args.csv, encoding="utf-8-sig", newline="") as source:
            total, errors, timeouts, slow, median = analyze(csv.DictReader(source), args.limite_ms)
    except (OSError, KeyError, ValueError) as error:
        parser.exit(2, f"Arquivo inválido: {error}\n")
    print(f"Medições: {total} | HTTP 5xx: {errors} | Timeouts: {timeouts}")
    print(f"Respostas lentas: {slow} | Mediana geral: {median:g} ms")

