# -*- coding: utf-8 -*-
# @Author: Frank Hasdorf
# @Date:   07-05-2026 10:47:06
# @Last Modified by:   Frank Hasdorf
# @Last Modified time: 08-05-2026 21:51:17


# -*- coding: utf-8 -*-
import os
import requests
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

class NewsFetcher:
    def __init__(self, query=""):  # Jetzt mit Parameter
        current_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(current_dir) 
        env_path = os.path.join(root_dir, 'Docs', '.env')
        
        load_dotenv(dotenv_path=env_path)
        
        self.keys = {
            "newsapi_org": os.getenv("NEWSAPI_ORG_KEY"),
            "newsapi_ai": os.getenv("NEWSAPI_AI_KEY"),
            "marketaux": os.getenv("MARKETAUX_KEY"),
            "alphavantage":os.getenv("ALPHAVANTAGE_KEY")
        }
        
        self.query = query  # Das Keyword wird hier gespeichert
        
        # Kleiner Sicherheits-Check fürs Terminal
        if not self.keys["newsapi_org"]:
            print("ACHTUNG: API Keys wurden nicht gefunden! Pfad:", env_path)

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
        
        # Sicherer Pandas-Import (verhindert Abstürze bei leeren APIs)
        cols = ['publishedAt', 'title', 'description', 'url']
        
        if org_data:
            df_org = pd.DataFrame(org_data)
            for c in cols:
                if c not in df_org.columns: df_org[c] = ""
            df_org = df_org[cols]
        else:
            df_org = pd.DataFrame(columns=cols)
            
        if aux_data:
            df_aux = pd.DataFrame(aux_data)
            if 'published_at' in df_aux.columns:
                df_aux = df_aux.rename(columns={'published_at': 'publishedAt'})
            for c in cols:
                if c not in df_aux.columns: df_aux[c] = ""
            df_aux = df_aux[cols]
        else:
            df_aux = pd.DataFrame(columns=cols)

        combined_df = pd.concat([df_org, df_aux], ignore_index=True)
        if combined_df.empty:
            return "Keine neuen Signale gefunden."

        combined_df = combined_df.drop_duplicates(subset=['title'])
        
        # --- DER FIX: Speichert die CSV im versteckten ".data" Ordner ---
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_dir = os.path.join(".data", "raw")
        os.makedirs(save_dir, exist_ok=True)
        path = os.path.join(save_dir, f"market_intel_{timestamp}.csv")
        
        combined_df.to_csv(path, index=False, encoding='utf-8')
        
        return f"Erfolg: {len(combined_df)} Meldungen gesichert."