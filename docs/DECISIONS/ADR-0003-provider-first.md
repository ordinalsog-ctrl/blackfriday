# ADR-0003: Provider-Adapter als Erweiterungspunkt

**Status:** Accepted, 2026-11-12

**Kontext:** Geizhals, idealo, Händlerfeeds, Keepa und Open-Data-Projekte liefern verschiedene Arten von Datensätzen.

**Entscheidung:** Jede Quelle durch Adaptervertrag mit explicit `capabilities`, Preisart, Identity-Herkunft, Quota und Lizenz. Quellen schreiben nur ins Staging. Ein gemeinsamer Review-Prozess entscheidet über Veröffentlichung und Analyse.

**Konsequenzen:** weitere APIs ergänzbar ohne Kernlogik zu vervielfältigen; höherer Aufwand für präzises Mapping, bewusst akzeptiert.
