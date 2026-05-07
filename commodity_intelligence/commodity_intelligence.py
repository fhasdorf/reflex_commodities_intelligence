# -*- coding: utf-8 -*-
# @Author: Frank Hasdorf
# @Date:   07-05-2026 14:41:21
# @Last Modified by:   Frank Hasdorf
# @Last Modified time: 07-05-2026 16:40:08

import reflex as rx
import asyncio
import os
import glob
import pandas as pd

try:
    from .news_fetcher import NewsFetcher
except (ImportError, ValueError):
    import sys
    sys.path.append(os.path.dirname(__file__))
    from news_fetcher import NewsFetcher

# --- GLOBALER STYLE GUIDE ---
BRAND_COLORS = {
    "bg": "#0B1120",        # Banking Blau Dunkel
    "card": "#111827",      # Kachel-Hintergrund
    "accent": "#38BDF8",    # Banking Hellblau
    "text_main": "#F8FAFC", # Weiß
    "text_dim": "#94A3B8",  # Grau-Blau
}

# Zentrale Definition für das Kachel-Verhalten
CARD_STYLE = {
    "background": BRAND_COLORS["card"],
    "border": f"1px solid {BRAND_COLORS['bg']}",
    "border_radius": "12px",
    "padding": "24px",
    "width": "100%",
    "transition": "all 0.2s ease-in-out",
    "_hover": {
        "border_color": BRAND_COLORS["accent"],
        "background": "#1E293B", # Etwas helleres Blau beim Hovern
        "transform": "translateY(-4px)", # Kleiner "Lift"-Effekt
    }
}

# UMBENANNT: Von 'State' zu 'MarketState', um Namenskonflikte zu lösen
class MarketState(rx.State):
    processing: bool = False
    progress_value: int = 0
    status_text: str = "Bereit für Marktanalyse"
    last_report: str = ""
    news_data: list[dict] = []

    async def run_market_intelligence(self):
        self.processing = True
        self.progress_value = 10
        self.status_text = "Verbindung zu APIs..."
        yield
        
        try:
            fetcher = NewsFetcher()
            result_msg = fetcher.aggregate_and_save()
            
            self.status_text = "Lade neueste Signale..."
            self.progress_value = 70
            yield

            files = glob.glob(os.path.join("data", "raw", "*.csv"))
            if files:
                latest_file = max(files, key=os.path.getctime)
                df = pd.read_csv(latest_file)
                
                df = df.fillna("") 
                df['publishedAt'] = df['publishedAt'].astype(str).str[:10]
                df['description'] = df['description'].astype(str).str[:160] + "..."
                df['title'] = df['title'].astype(str)
                df['url'] = df['url'].astype(str)
                
                self.news_data = df.head(10).to_dict("records")
            
            self.last_report = result_msg
            self.status_text = "Analyse abgeschlossen."
            self.progress_value = 100
            yield
            await asyncio.sleep(1)
        except Exception as e:
            self.status_text = f"Fehler: {str(e)}"
        finally:
            self.processing = False

def news_row(article: dict) -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.vstack(
                rx.text(article["publishedAt"], size="1", color=GOLD),
                rx.heading(article["title"], size="3", color=TEXT_LIGHT),
                rx.text(article["description"], size="2", color=TEXT_MUTE),
                align="start", spacing="1",
            ),
            rx.spacer(),
            rx.link(rx.icon(tag="external_link", size=20, color=GOLD), href=article["url"], is_external=True),
            width="100%", padding="20px", border_bottom="1px solid #1E1C18",
            _hover={"background": "#161412"},
        ),
        width="100%",
    )

def app_card(icon: str, title: str, desc: str, status: str, is_news: bool = False) -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.center(rx.text(icon, font_size="20px"), width="40px", height="40px", background="#1E293B", border_radius="6px"),
                rx.vstack(
                    rx.heading(title, size="3", color=BRAND_COLORS["text_main"]),
                    rx.text(status, size="1", color=BRAND_COLORS["accent"], letter_spacing="0.05em"),
                    spacing="0", align="start",
                ),
                width="100%",
            ),
            rx.text(desc, size="2", color=BRAND_COLORS["text_dim"], margin_top="10px"),
            # ... Button Logik bleibt gleich ...
        ),
        # HIER wird der globale Style angewendet:
        style=CARD_STYLE, 
    )

def index() -> rx.Component:
    return rx.box(
        rx.vstack(
            # --- HEADER ---
            rx.hstack(
                rx.vstack(
                    rx.heading("Commodity Intelligence", size="8", color=TEXT_LIGHT),
                    rx.text("Capital Market Advisory & Strategic CRM Monitoring", color=TEXT_MUTE),
                    align="start",
                ),
                rx.spacer(),
                rx.badge("V 0.1 ALPHA", variant="outline", border_radius="full", padding_x="12px"),
                width="100%", padding_bottom="40px",
            ),

            # --- KACHELN (Alle 4 wieder da!) ---
            rx.grid(
                app_card("📰", "News-Intelligence", "Echtzeit-Monitoring von Kapitalmarkt-Events und Rohstoff-Deals.", "AKTIV", is_news=True),
                app_card("🏢", "Registry-Audit", "Analyse von Besitzstrukturen und wirtschaftlich Berechtigten.", "IN PLANUNG"),
                app_card("⚖️", "EU Raw Materials Act", "Überwachung regulatorischer Hürden für Investitionsprojekte.", "IN PLANUNG"),
                app_card("📈", "Trend-Algorithmus", "NLP-basierte Mustererkennung in Markt-Datenströmen.", "KONZEPT", help_url="/faq/trend_algorithmus_konzept.html"),
                columns="2", spacing="5", width="100%",
            ),

            # --- ERGEBNIS LISTE ---
            rx.cond(
                MarketState.news_data,
                rx.vstack(
                    rx.hstack(
                        rx.heading("Aktuelle Marktsignale", size="6", color=TEXT_LIGHT),
                        rx.badge(f"{MarketState.news_data.length()} Signale", color_scheme="gold", variant="soft"),
                        margin_top="60px", margin_bottom="20px", width="100%", align="end",
                    ),
                    rx.box(
                        rx.vstack(rx.foreach(MarketState.news_data, news_row), spacing="0"),
                        width="100%", background=CARD_BG, border="1px solid #2A2520", border_radius="12px", overflow="hidden",
                    ),
                    width="100%",
                ),
                rx.fragment(),
            ),

            # --- FOOTER ---
            rx.hstack(
                rx.text("Reflex Intelligence Engine · Capital Market Unit", size="1", color=TEXT_MUTE),
                rx.spacer(),
                rx.text("© 2026 EMIAG Intelligence", size="1", color=TEXT_MUTE),
                width="100%", margin_top="60px", padding_top="20px",
                border_top=f"1px solid #1E1C18",
            ),
            max_width="1100px", margin="0 auto", padding="40px 24px",
        ),
        background=BG_DARK, min_height="100vh",
    )

app = rx.App(
    theme=rx.theme(
        appearance="dark", 
        accent_color="blue", # Dein Banking-Blau für Radix-Elemente
        font_family="Inter, sans-serif", # Globaler Font
    ),
    stylesheets=[
        "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap",
    ],
)
app.add_page(index, title="Commodity Intelligence Dashboard")
