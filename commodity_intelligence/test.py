# -*- coding: utf-8 -*-
# @Author: Frank Hasdorf
# @Date:   07-05-2026 12:24:34
# @Last Modified by:   Frank Hasdorf
# @Last Modified time: 07-05-2026 12:25:00
import os
from dotenv import load_dotenv

# Wir definieren den Pfad zur .env Datei explizit relativ zum Projekt-Root
env_path = os.path.join(os.getcwd(), 'Docs', '.env')
load_dotenv(dotenv_path=env_path)
    
news_key = os.getenv("NEWSAPI_ORG_KEY")
    
if news_key:
        print(f"✅ Erfolg: API-Key geladen (Anfang: {news_key[:5]}...)")
else:
        print(f"❌ Fehler: .env Datei unter {env_path} nicht gefunden oder Key fehlt.")

if __name__ == "__main__":
    test_key_loading()