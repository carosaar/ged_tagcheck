#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GEDCOM‑Syntax‑Checker

Prüft INDI‑ und FAM‑Datensätze in einer UTF‑8‑kodierten GEDCOM‑Datei auf die
spezifischen Regeln und erzeugt eine deutschsprachige CSV‑Protokolldatei.
Beispielaufruf:
python ged_tagcheck.py meinefamilie.ged
"""

import csv
import sys
import re
from collections import defaultdict
from pathlib import Path

# ----------------------------------------------------------------------
# 1. Datenstruktur
# ----------------------------------------------------------------------

class Node:
    """Knoten eines gedcom‑Baums."""
    __slots__ = ("level", "tag", "value", "children")
    def __init__(self, level: int, tag: str, value: str = ""):
        self.level = level
        self.tag = tag.strip().upper()
        self.value = value.strip()
        self.children = []
    def __repr__(self):
        return f"<Node {self.level} {self.tag} {self.value} {len(self.children)} Kinder>"

# ----------------------------------------------------------------------
# 2. Parser
# ----------------------------------------------------------------------

def parse_gedcom(path: Path):
    """Gibt eine Liste der Root‑Nodes (INDI / FAM) zurück."""
    roots = []
    stack = []
    level_pat = re.compile(r"^\s*(\d+)\s+([^\s]+)(?:\s+(.*))?$")
    with path.open(encoding="utf-8") as fp:
        for lineno, raw_line in enumerate(fp, 1):
            line = raw_line.rstrip("\n")
            m = level_pat.match(line)
            if not m:
                continue
            level, tag, value = int(m.group(1)), m.group(2), (m.group(3) or "")
            node = Node(level, tag, value)
            while stack and stack[-1].level >= level:
                stack.pop()
            if stack:
                stack[-1].children.append(node)
            else:
                # Root-Knoten anhand des value ("INDI"/"FAM")
                if node.value in ("INDI", "FAM"):
                    roots.append(node)
            stack.append(node)
    return roots

# ----------------------------------------------------------------------
# 3. Validierungsfunktionen
# ----------------------------------------------------------------------

def validate_individual(ind_node: Node):
    """Prüft die INDI‑Regeln, gibt Fehlerliste (deutsch) zurück."""
    errors = []
    def check_event(tag):
        ev = [c for c in ind_node.children if c.tag == tag]
        if len(ev) > 1:
            errors.append(f"{tag} kommt mehrfach vor ({len(ev)}).")
        for e in ev:
            dates = [c for c in e.children if c.tag == "DATE"]
            plats = [c for c in e.children if c.tag == "PLAC"]
            if len(dates) > 1:
                errors.append(f"{tag}.DATE kommt mehrfach vor ({len(dates)}).")
            if len(plats) > 1:
                errors.append(f"{tag}.PLAC kommt mehrfach vor ({len(plats)}).")
    check_event("BIRT")
    check_event("DEAT")
    # NAME-Tags
    name_nodes = [c for c in ind_node.children if c.tag == "NAME"]
    untyped = [n for n in name_nodes if not any(ch.tag == "TYPE" for ch in n.children)]
    if len(untyped) > 1:
        errors.append(f"Mehr als ein untypisierter NAME-Tag ({len(untyped)}).")
    elif len(untyped) == 1 and name_nodes[0] != untyped[0]:
        errors.append("Untypisierter NAME-Tag ist nicht der erste NAME-Tag.")
    return errors

def validate_family(fam_node: Node):
    """Prüft die FAM-Regeln, gibt Fehlerliste (deutsch) zurück."""
    errors = []

    # WIFE/HUSB-Prüfung
    wife_nodes = [c for c in fam_node.children if c.tag == "WIFE"]
    husb_nodes = [c for c in fam_node.children if c.tag == "HUSB"]

    if len(wife_nodes) > 1:
        errors.append(f"Es gibt mehr als einen WIFE-Tag ({len(wife_nodes)}).")
    if len(husb_nodes) > 1:
        errors.append(f"Es gibt mehr als einen HUSB-Tag ({len(husb_nodes)}).")
    if (len(wife_nodes) == 0 and len(husb_nodes) == 0):
        errors.append("Mindestens ein WIFE- oder ein HUSB-Tag muss vorhanden sein.")

    # MARR-Prüfung
    marr_nodes = [c for c in fam_node.children if c.tag == "MARR"]
    if len(marr_nodes) > 2:
        errors.append(f"Es gibt {len(marr_nodes)} MARR-Tags – maximal 2 erlaubt.")
    type_counts = defaultdict(int)
    for idx, marr in enumerate(marr_nodes, 1):
        typ = None
        for ch in marr.children:
            if ch.tag == "TYPE":
                typ = ch.value.upper()
                break
        if typ:
            if typ not in ("CIVIL", "RELIGIOUS"):
                errors.append(f"MARR #{idx} hat einen nicht unterstützten TYPE '{typ}'.")
            else:
                type_counts[typ] += 1
        dates = [c for c in marr.children if c.tag == "DATE"]
        plats = [c for c in marr.children if c.tag == "PLAC"]
        if len(dates) > 1:
            errors.append(f"MARR #{idx}.DATE kommt mehrfach vor ({len(dates)}).")
        if len(plats) > 1:
            errors.append(f"MARR #{idx}.PLAC kommt mehrfach vor ({len(plats)}).")
    if type_counts["CIVIL"] > 1:
        errors.append(f"{type_counts['CIVIL']} CIVIL-MARR-Tags – maximal 1 erlaubt.")
    if type_counts["RELIGIOUS"] > 1:
        errors.append(f"{type_counts['RELIGIOUS']} RELIGIOUS-MARR-Tags – maximal 1 erlaubt.")
    return errors

# ----------------------------------------------------------------------
# 4. Hauptfunktion
# ----------------------------------------------------------------------

def main(argv):
    if len(argv) != 2:
        print(f"Aufruf: {argv[0]} <gedcom_datei>", file=sys.stderr)
        sys.exit(1)
    ged_path = Path(argv[1])
    if not ged_path.is_file():
        print(f"Datei nicht gefunden: {ged_path}", file=sys.stderr)
        sys.exit(1)
    roots = parse_gedcom(ged_path)
    csv_name = f"{ged_path.stem}_syntaxcheck.csv"
    csv_path = Path.cwd() / csv_name
    error_rows = [] # (Datensatz-Typ, ID, Fehler)
    total_errors = 0
    total_ind = total_fam = 0
    for node in roots:
        rec_type = node.value  # "INDI" oder "FAM"
        rec_id = node.tag      # z.B. "@I1@"
        if rec_type == "INDI":
            total_ind += 1
            errs = validate_individual(node)
        elif rec_type == "FAM":
            total_fam += 1
            errs = validate_family(node)
        else:
            continue
        for e in errs:
            error_rows.append((rec_type, rec_id, e))
        total_errors += len(errs)
    with csv_path.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.writer(fp)
        writer.writerow(["Datensatz-Typ", "Datensatz-ID", "Fehler"])
        writer.writerows(error_rows)
    print(f"Syntax-Check abgeschlossen.")
    print(f"Datei: {csv_path}")
    print(f"INDI-Datensätze: {total_ind}")
    print(f"FAM-Datensätze: {total_fam}")
    print(f"Gefundene Fehler: {total_errors}")

if __name__ == "__main__":
    main(sys.argv)
