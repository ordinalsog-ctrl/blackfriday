# ADR-0001: Modularer Python-Monolith vor Microservices

**Status:** Accepted, 2026-11-12

**Kontext:** 20er-Pilot, 500 Kandidaten, kostenloses Budget und kurzer Vorlauf. Zusätzliche Microservices erzeugen unnötige Infrastruktur- und Betriebsrisiken.

**Entscheidung:** Python + SQLite + Streamlit mit strikt getrennten Provider-Adaptern, Review und Analytics; offline CI. PostgreSQL erst bei Parallelität/Teamzugriff.

**Konsequenzen:** leicht testbar und lokal startbar; SQLite-Write-Concurrency und interaktives CLI sind Grenzen. Einzelne Module können ohne Vertragsbruch später ersetzt werden.
