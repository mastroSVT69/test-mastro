#!/usr/bin/env python3
"""Convertit un fichier CSV en XLSX sans pandas (utilise openpyxl).

Usage:
  python tools/convert_csv_to_xlsx.py [infile.csv] [outfile.xlsx]

Par défaut : `src/tests/fixtures/mapping.csv -> src/tests/fixtures/mapping.xlsx`.
"""

import csv
import sys
import argparse

try:
    from openpyxl import Workbook
except Exception:
    print("Erreur: la bibliothèque 'openpyxl' n'est pas installée. Installez-la avec:\n  pip install openpyxl")
    sys.exit(2)


def convert_csv_to_xlsx(infile: str, outfile: str) -> None:
    wb = Workbook()
    ws = wb.active
    with open(infile, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            ws.append(row)
    wb.save(outfile)


def main():
    parser = argparse.ArgumentParser(description='Convert CSV en XLSX (fixtures)')
    parser.add_argument('infile', nargs='?', default='src/tests/fixtures/mapping.csv', help='Chemin du fichier CSV source')
    parser.add_argument('outfile', nargs='?', default='src/tests/fixtures/mapping.xlsx', help='Chemin du fichier XLSX de sortie')
    args = parser.parse_args()

    try:
        convert_csv_to_xlsx(args.infile, args.outfile)
        print(f'Converti: {args.infile} -> {args.outfile}')
    except FileNotFoundError:
        print(f"Fichier introuvable: {args.infile}")
        sys.exit(1)
    except Exception as e:
        print('Erreur lors de la conversion:', e)
        sys.exit(3)


if __name__ == '__main__':
    main()
