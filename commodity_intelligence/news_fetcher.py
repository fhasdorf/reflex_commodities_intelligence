# -*- coding: utf-8 -*-
# @Author: Frank Hasdorf
# @Date:   07-05-2026 10:47:06
# @Last Modified by:   Frank Hasdorf
# @Last Modified time: 07-05-2026 15:44:03


def main():
    print("Hello, World!")


if __name__ == "__main__":
    main()
# -*- coding: utf-8 -*-
import os
import requests
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

class NewsFetcher:
    def __init__(self):
        # Geht vom aktuellen Ordner hoch zum Hauptordner, um die Docs/.env zu finden
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        env_path = os.path.join(root_dir, 'Docs', '.env')
        load_dotenv(dotenv_path=env_path)
        
        self.keys = {
            "newsapi_org": os.getenv("NEWSAPI_ORG_KEY"),
            "newsapi_ai": os.getenv("NEWSAPI_AI_KEY"),
            "marketaux": os.getenv("MARKETAUX_KEY")
        }
        
        # Etwas breitere Query für die Präsentation, damit sicher Daten kommen
        self.query = "Mining OR Norway OR Investment"

    def fetch_newsapi_org(self):
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": self.query,
            "apiKey": self.keys.get("newsapi_org"),
            "language": "en",
            "sortBy": "publishedAt"
        }
        if not params["apiKey"]: return []
        response = requests.get(url, params=params)
        return response.json().get("articles", []) if response.status_code == 200 else []

    def fetch_marketaux(self):
        url = "https://api.marketaux.com/v1/news/all"
        params = {
            "search": self.query,
            "api_token": self.keys.get("marketaux"),
            "language": "en",
            "filter_entities": "true"
        }
        if not params["api_token"]: return []
        response = requests.get(url, params=params)
        return response.json().get("data", []) if response.status_code == 200 else []

    def aggregate_and_save(self):
        org_data = self.fetch_newsapi_org()
        aux_data = self.fetch_marketaux()
        
        df_org = pd.DataFrame(org_data)[['publishedAt', 'title', 'description', 'url']] if org_data else pd.DataFrame()
        df_aux = pd.DataFrame(aux_data)[['published_at', 'title', 'description', 'url']] if aux_data else pd.DataFrame()
        
        if not df_aux.empty and 'published_at' in df_aux.columns:
            df_aux = df_aux.rename(columns={'published_at': 'publishedAt'})

        combined_df = pd.concat([df_org, df_aux], ignore_index=True)
        if combined_df.empty:
            return "Keine neuen Signale gefunden."

        combined_df = combined_df.drop_duplicates(subset=['title'])
        
        # Speichert die CSV im data/raw Ordner des Projekts
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        os.makedirs(os.path.join("data", "raw"), exist_ok=True)
        path = os.path.join("data", "raw", f"market_intel_{timestamp}.csv")
        
        combined_df.to_csv(path, index=False, encoding='utf-8')
        
        return f"Erfolg: {len(combined_df)} Meldungen gesichert."