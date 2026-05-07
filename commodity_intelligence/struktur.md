commodity-intel-dashboard/
├── .github/                # GitHub Actions für CI/CD
├── data/
│   ├── raw/                # Unverarbeitete API-Antworten (JSON/CSV)
│   └── processed/          # Bereinigte Daten für den Trend-Algorithmus
├── modules/
│   ├── news_fetcher.py     # Logik für NewsAPI
│   ├── registry_lookup.py  # Abfragen von Handelsregistern
│   ├── act_tracker.py      # Monitoring für European Raw Materials Act
│   └── trend_engine.py     # Der Algorithmus zur Trend-Analyse
├── assets/                 # CSS, Bilder oder statische Files
├── app.py                  # Haupteinstiegspunkt (Reflex Dashboard)
├── requirements.txt        # Abhängigkeiten (reflex, pandas, requests, etc.)
└── README.md               # Dokumentation des Projekts