# GEDCOM-TAG-Checker

**Prüft genealogische GEDCOM-Dateien auf Struktur- und Tag-Fehler. Die geprüften Syntaxfehler werden als deutschsprachige CSV-Datei ausgegeben, wodurch eine schnelle Qualitätskontrolle genealogischer Datenbestände möglich ist.**

***

## Übersicht

Dieses Tool analysiert GEDCOM-Dateien (UTF-8, Standard 5.5/5.5.1), indem es für jeden INDI- und FAM-Datensatz typische Formfehler und Verstöße gegen festgelegte Ordnungsregeln erkennt. Das Programm gibt eine CSV-Datei mit den detektierten Problemen aus und eignet sich insbesondere für die Vorprüfung großer Genealogiebestände oder die Migration alter Datenbestände auf neue Softwareumgebungen.

***

## Features

- **Prüft individuelle Personendatensätze (INDI) und Familiendatensätze (FAM) nach grundlegenden GEDCOM-Regeln**
- **Validiert häufige Fehler, z.B. Mehrfache NAME-Tags, doppelte Ereignisse, ungültige MARR-Typen**
- **Erweiterte FAM-Prüfung: Erlaubt nur je ein WIFE- und HUSB-Tag, mindestens einer davon ist Pflicht**
- **Intuitive Fehlerausgabe in deutscher Sprache im CSV-Format für weitere Verarbeitung**
- **Quelloffen, vollständig in Python 3 geschrieben**
- **Einfache Erweiterbarkeit für eigene Prüfregeln**

***

## Voraussetzungen

- **Python 3.6 oder neuer**
- Keine externen Abhängigkeiten

***

## Installation

Kopiere das Script `ged_tagcheck.py` in ein beliebiges Verzeichnis oder klone dieses Repository:

```bash
git clone https://github.com/DEIN_GITHUB_USERNAME/gedcom-syntax-checker.git
cd gedcom-syntax-checker
```

Im Verzeichnis `/dist` ist eine compilierte Windows-exe abgelegt
Kompiliert mit 
`pyinstaller.exe --onefile .\ged_tagcheck.py`
***

## Anwendung

Führe das Script mit einer GEDCOM-Datei als Argument aus:

```bash
python ged_tagcheck.py meinefamilie.ged
```

Daraufhin werden die Prüfungen durchgeführt und eine CSV-Datei namens `meinefamilie_syntaxcheck.csv` im selben Verzeichnis erzeugt.

***

## CSV-Format

Die Ergebnisdatei besteht aus folgenden Spalten:

| Datensatz-Typ | Datensatz-ID | Fehlerbeschreibung                     |
|---------------|--------------|----------------------------------------|
| INDI / FAM    | I1 / F2  | Deutschsprachige Beschreibung des Fehlers |

Beispiel:

```csv
Datensatz-Typ,Datensatz-ID,Fehler
INDI,I5,BIRT kommt mehrfach vor (2).
FAM,F2,Es gibt 3 MARR-Tags – maximal 2 erlaubt.
FAM,F3,Mindestens ein WIFE- oder ein HUSB-Tag muss vorhanden sein.
```

***

## Validierte Fehlerarten

### Personen-Datensätze (INDI)
- **Mehrfaches Auftreten von BIRT-, DEAT-, NAME-Tags**
- **NAME-Tag ohne TYPE muss zuerst stehen und darf nur einmal vorkommen**
- **Mehrfache DATE/PLAC-Einträge bei Ereignissen BIRT, DEAT**

### Familiendatensätze (FAM)
- **Mehr als zwei MARR-Tags**
- **Mehr als ein HUSB- bzw. ein WIFE-Tag**
- **Weder HUSB noch WIFE-Tag vorhanden**
- **Mehrfache DATE/PLAC-Tags pro MARR**
- **Ungültige TYPE-Werte bei MARR**
- **Mehr als ein CIVIL oder RELIGIOUS TYPE pro Familie**

Alle Fehlermeldungen erfolgen auf Deutsch.

***

## Erweiterbarkeit und Anpassung

Das Script ist modular aufgebaut:
- Zusätzliche Prüfungen können einfach in die Funktionen `validate_individual` bzw. `validate_family` integriert werden.
- Die Ausgabe kann bei Bedarf auf weitere Formate (z.B. JSON) erweitert werden.

***

## Bekannte Einschränkungen

- Es werden ausschließlich die Syntaxstruktur und Tag-Regeln geprüft, keine semantische Konsistenz (z.B. Plausibilität von Lebensdaten).
- Für sehr große GEDCOM-Dateien kann die Laufzeit steigen; bisher in Tests jedoch performant bis >100.000 Datensätze.

***

## Lizenz

[MIT-Lizenz](LICENSE)

***

## Beispiel

Eine Beispiel-GEDCOM-Datei und das zugehörige Syntaxcheck-Ergebnis finden sich im Ordner `testfiles` dieses Repos.

***

**Projekt von [Dieter Eckstein]**  
Saarbrücken, 2025
