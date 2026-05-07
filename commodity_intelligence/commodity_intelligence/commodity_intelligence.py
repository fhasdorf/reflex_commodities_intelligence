# -*- coding: utf-8 -*-
# @Author: Frank Hasdorf
# @Date:   07-05-2026 14:41:21
# @Last Modified by:   Frank Hasdorf
# @Last Modified time: 07-05-2026 15:08:57

import reflex as rx
import asyncio
import os
import glob
import pandas as pd
# Import des NewsFetchers aus derselben Ebene
from .news_fetcher import NewsFetcher 

# --- DESIGN KONSTANTEN ---
BG_DARK = "#12100E"
CARD_BG = "#1A1814"
GOLD = "#C8A850"
TEXT_MUTE = "#6B6560"
TEXT_LIGHT = "#E8E0D0"

class State(rx.State):
    """Das Gehirn der App für Capital Market Intelligence."""
    processing: bool = False
    progress_value: int = 0
    status_text: str = "Bereit für Marktanalyse"
    last_report: str = ""
    news_data: list[dict] = []  # Speicher für die News-Liste

    async def run_market_intelligence(self):
        """Führt die echte API-Abfrage aus und zeigt den Fortschritt an."""
        self.processing = True
        self.progress_value = 10
        self.status_text = "Initialisiere Kapitalmarkt-Schnittstellen..."
        yield
        await asyncio.sleep(1)

        try:
            # 1. API Abfrage starten
            self.status_text = "Abfrage NewsAPI & MarketAux läuft..."
            self.progress_value = 40
            yield
            
            fetcher = NewsFetcher()
            # Führt dein Skript aus und speichert die CSV
            result_msg = fetcher.aggregate_and_save()
            
            # 2. Daten laden und harmonisieren
            self.status_text = "Harmonisiere Datenströme..."
            self.progress_value = 70
            yield
            
            # Neueste CSV im data/raw Ordner suchen
            files = glob.glob("data/raw/*.csv")
            if files:
                latest_file = max(files, key=os.path.getctime)
                df = pd.read_csv(latest_file)
                # Die Top 10 Signale für die Anzeige vorbereiten
                self.news_data = df.head(10).to_dict("records")
            
            self.last_report = result_msg
            self.status_text = "Analyse abgeschlossen."
            self.progress_value = 100
            yield
            await asyncio.sleep(1)

        except Exception as e:
            self.status_text = f"Fehler bei Abfrage: {str(e)}"
            self.progress_value = 0
        
        finally:
            self.processing = False

def news_row(article: dict) -> rx.Component:
    """Styling für eine einzelne News-Zeile in der Ergebnisliste."""
    return rx.box(
        rx.hstack(
            rx.vstack(
                rx.text(article.get("publishedAt", "Datum")[:10], size="1", color=GOLD),
                rx.heading(article.get("title", "Kein Titel"), size="3", color=TEXT_LIGHT),
                rx.text(article.get("description", "")[:160] + "...", size="2", color=TEXT_MUTE),
                align="start",
                spacing="1",
            ),
            rx.spacer(),
            rx.link(
                rx.icon(tag="external_link", size=20, color=GOLD),
                href=article.get("url", "#"),
                is_external=True,
            ),
            width="100%",
            padding="20px",
            border_bottom=f"1px solid #1E1C18",
            _hover={"background": "#161412"},
        ),
        width="100%",
    )

def app_card(icon: str, title: str, desc: str, status: str, help_url: str = None, is_news: bool = False) -> rx.Component:
    """Erstellt eine interaktive Kachel im Dashboard."""
    
    help_icon = rx.cond(
        help_url,
        rx.link(
            rx.icon(tag="circle_help", size=18, color=TEXT_MUTE, _hover={"color": GOLD}, margin_left="8px"),
            href=help_url,
            is_external=True,
        ),
        rx.fragment(),
    )

    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.center(
                    rx.text(icon, font_size="20px"),
                    width="40px", height="40px",
                    background="#2A2520", border_radius="6px",
                ),
                rx.vstack(
                    rx.hstack(
                        rx.heading(title, size="3", color=TEXT_LIGHT),
                        help_icon,
                        align="center",
                    ),
                    rx.text(status, size="1", color=GOLD, letter_spacing="0.05em"),
                    spacing="0", align="start",
                ),
                spacing="3", align="center", width="100%",
            ),
            rx.text(desc, size="2", color=TEXT_MUTE, margin_top="10px"),
            
            rx.cond(
                is_news & State.processing,
                rx.vstack(
                    rx.progress(value=State.progress_value, width="100%", color_scheme="gold"),
                    rx.text(State.status_text, size="1", color=GOLD, width="100%", text_align="center"),
                    width="100%", margin_top="15px", spacing="1",
                ),
                rx.vstack(
                    rx.button(
                        "Intelligence Update" if is_news else "Tool öffnen",
                        on_click=State.run_market_intelligence if is_news else None,
                        variant="ghost",
                        width="100%",
                        margin_top="15px",
                        border="1px solid #2A2520",
                        color=TEXT_LIGHT,
                        _hover={"background": "#2A2520", "color": GOLD},
                    ),
                    rx.cond(
                        is_news & (State.last_report != ""),
                        rx.text(State.last_report, size="1", color=TEXT_MUTE, margin_top="5px"),
                        rx.fragment()
                    ),
                    width="100%"
                ),
            ),
            align="start", spacing="1",
        ),
        background=CARD_BG, border="1px solid #2A2520", border_radius="8px",
        padding="24px", width="100%", transition="all 0.2s ease",
        _hover={"border_color": "#3D352D", "transform": "translateY(-2px)"},
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

            # --- TOOL GRID ---
            rx.grid(
                app_card("📰", "News-Intelligence", "API-Monitoring von Weltmarkttrends.", "AKTIV", is_news=True),
                app_card("🏢", "Registry-Audit", "Analyse von Besitzstrukturen.", "IN PLANUNG"),
                app_card("⚖️", "EU Raw Materials Act", "Regulatorisches Monitoring.", "IN PLANUNG"),
                app_card("📈", "Trend-Algorithmus", "NLP-basierte Mustererkennung.", "KONZEPT", help_url="/faq/trend_algorithmus_konzept.html"),
                columns="2", spacing="5", width="100%",
            ),

            # --- ERGEBNIS LISTE (Erscheint nach Analyse) ---
            rx.cond(
                State.news_data,
                rx.vstack(
                    rx.hstack(
                        rx.heading("Aktuelle Marktsignale", size="6", color=TEXT_LIGHT),
                        rx.badge(f"{len(State.news_data)} Signale", color_scheme="gold", variant="soft"),
                        margin_top="60px", margin_bottom="20px", width="100%", align="end",
                    ),
                    rx.box(
                        rx.vstack(rx.foreach(State.news_data, news_row), spacing="0"),
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

app = rx.App(theme=rx.theme(appearance="dark", accent_color="gold")
)
app.add_page(index, title="Commodity Intelligence Dashboard")