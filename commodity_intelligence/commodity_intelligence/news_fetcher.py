# -*- coding: utf-8 -*-
# @Author: Frank Hasdorf
# @Date:   07-05-2026 10:47:06
# @Last Modified by:   Frank Hasdorf
# @Last Modified time: 07-05-2026 15:15:27


def main():
    print("Hello, World!")


if __name__ == "__main__":
    main()
# -*- coding: utf-8 -*-
import reflex as rx
import asyncio
import os
import glob
import pandas as pd

# Sicherer Import des NewsFetchers innerhalb der Reflex-Struktur
try:
    from .news_fetcher import NewsFetcher
except (ImportError, ValueError):
    import sys
    sys.path.append(os.path.dirname(__file__))
    from news_fetcher import NewsFetcher

# --- DESIGN KONSTANTEN ---
BG_DARK = "#12100E"
CARD_BG = "#1A1814"
GOLD = "#C8A850"
TEXT_MUTE = "#6B6560"
TEXT_LIGHT = "#E8E0D0"

class State(rx.State):
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

            # Daten aus der neuesten CSV laden
            files = glob.glob(os.path.join("data", "raw", "*.csv"))
            if files:
                latest_file = max(files, key=os.path.getctime)
                df = pd.read_csv(latest_file)
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
                rx.text(article.get("publishedAt", "Datum")[:10], size="1", color=GOLD),
                rx.heading(article.get("title", "Kein Titel"), size="3", color=TEXT_LIGHT),
                rx.text(article.get("description", "")[:160] + "...", size="2", color=TEXT_MUTE),
                align="start", spacing="1",
            ),
            rx.spacer(),
            rx.link(rx.icon(tag="external_link", size=20, color=GOLD), href=article.get("url", "#"), is_external=True),
            width="100%", padding="20px", border_bottom="1px solid #1E1C18",
            _hover={"background": "#161412"},
        ),
        width="100%",
    )

def app_card(icon: str, title: str, desc: str, status: str, help_url: str = None, is_news: bool = False) -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.center(rx.text(icon, font_size="20px"), width="40px", height="40px", background="#2A2520", border_radius="6px"),
                rx.vstack(
                    rx.hstack(rx.heading(title, size="3", color=TEXT_LIGHT), rx.cond(help_url, rx.link(rx.icon(tag="circle_help", size=18, color=TEXT_MUTE), href=help_url, is_external=True), rx.fragment())),
                    rx.text(status, size="1", color=GOLD, letter_spacing="0.05em"),
                    spacing="0", align="start",
                ),
                spacing="3", align="center", width="100%",
            ),
            rx.text(desc, size="2", color=TEXT_MUTE, margin_top="10px"),
            rx.cond(
                is_news & State.processing,
                rx.vstack(rx.progress(value=State.progress_value, width="100%", color_scheme="gold"), rx.text(State.status_text, size="1", color=GOLD, text_align="center"), width="100%", margin_top="15px"),
                rx.vstack(
                    rx.button("Intelligence Update" if is_news else "Tool öffnen", on_click=State.run_market_intelligence if is_news else None, variant="ghost", width="100%", margin_top="15px", border="1px solid #2A2520", color=TEXT_LIGHT),
                    rx.cond(is_news & (State.last_report != ""), rx.text(State.last_report, size="1", color=TEXT_MUTE), rx.fragment()),
                    width="100%"
                ),
            ),
        ),
        background=CARD_BG, border="1px solid #2A2520", border_radius="8px", padding="24px", width="100%",
    )

def index() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.heading("Commodity Intelligence", size="8", color=TEXT_LIGHT),
            rx.grid(
                app_card("📰", "News-Intelligence", "Echtzeit-Monitoring.", "AKTIV", is_news=True),
                app_card("🏢", "Registry-Audit", "Besitzstrukturen.", "IN PLANUNG"),
                columns="2", spacing="5", width="100%",
            ),
            rx.cond(
                State.news_data,
                rx.vstack(rx.heading("Aktuelle Marktsignale", size="6", color=TEXT_LIGHT), rx.box(rx.vstack(rx.foreach(State.news_data, news_row)), width="100%", background=CARD_BG, border="1px solid #2A2520", border_radius="12px"), width="100%", margin_top="40px"),
                rx.fragment(),
            ),
            max_width="1100px", margin="0 auto", padding="40px 24px",
        ),
        background=BG_DARK, min_height="100vh",
    )

# KRITISCH: Diese Zeilen müssen am Ende der Datei stehen!
app = rx.App(theme=rx.theme(appearance="dark", accent_color="gold"))
app.add_page(index, title="Commodity Intelligence Dashboard")