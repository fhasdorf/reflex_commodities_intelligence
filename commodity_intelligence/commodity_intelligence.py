# -*- coding: utf-8 -*-
# @Author: Frank Hasdorf
# @Date:   07-05-2026 14:41:21
# @Last Modified by:   Frank Hasdorf
# @Last Modified time: 07-05-2026 17:27:57


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

CARD_STYLE = {
    "background": BRAND_COLORS["card"],
    "border": f"1px solid {BRAND_COLORS['bg']}",
    "border_radius": "12px",
    "padding": "24px",
    "width": "100%",
    "transition": "all 0.2s ease-in-out",
    "_hover": {
        "border_color": BRAND_COLORS["accent"],
        "background": "#1E293B", 
        "transform": "translateY(-4px)", 
    }
}

class MarketState(rx.State):
    search_query: str = ""  # Startet mit leerem Feld
    processing: bool = False
    progress_value: int = 0
    status_text: str = "Bereit für Marktanalyse"
    last_report: str = ""
    news_data: list[dict] = []
    # --- NEU: Expliziter Setter, damit Reflex nicht stolpert ---
    def set_search_query(self, value: str):
        self.search_query = value
    async def run_market_intelligence(self):
        # Sicherheits-Check: Kein Start ohne Keyword
        if not self.search_query.strip():
            self.status_text = "Bitte gib zuerst ein Keyword ein!"
            yield
            await asyncio.sleep(2)
            self.status_text = "Bereit für Marktanalyse"
            return

        self.processing = True
        self.progress_value = 10
        self.status_text = f"Suche nach '{self.search_query}'..."
        yield
        
        try:
            # Übergabe an den Fetcher
            fetcher = NewsFetcher(query=self.search_query) 
            result_msg = fetcher.aggregate_and_save()
            
            self.status_text = "Lade neueste Signale..."
            self.progress_value = 70
            yield

            files = glob.glob(os.path.join(".data", "raw", "*.csv"))
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
                rx.text(article["publishedAt"], size="1", color=BRAND_COLORS["accent"]),
                rx.heading(article["title"], size="3", color=BRAND_COLORS["text_main"]),
                rx.text(article["description"], size="2", color=BRAND_COLORS["text_dim"]),
                align="start", spacing="1",
            ),
            rx.spacer(),
            rx.link(rx.icon(tag="external_link", size=20, color=BRAND_COLORS["accent"]), href=article["url"], is_external=True),
            width="100%", padding="20px", border_bottom=f"1px solid {BRAND_COLORS['bg']}",
            _hover={"background": "#1E293B"},
        ),
        width="100%",
    )

def app_card(icon: str, title: str, desc: str, status: str, help_url: str = None, is_news: bool = False) -> rx.Component:
    help_icon = rx.cond(
        help_url,
        rx.link(rx.icon(tag="circle_help", size=18, color=BRAND_COLORS["text_dim"], _hover={"color": BRAND_COLORS["accent"]}, margin_left="8px"), href=help_url, is_external=True),
        rx.fragment(),
    )

    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.center(rx.text(icon, font_size="20px"), width="40px", height="40px", background="#1E293B", border_radius="6px"),
                rx.vstack(
                    rx.hstack(rx.heading(title, size="3", color=BRAND_COLORS["text_main"]), help_icon, align="center"),
                    rx.text(status, size="1", color=BRAND_COLORS["accent"], letter_spacing="0.05em"),
                    spacing="0", align="start",
                ),
                spacing="3", align="center", width="100%",
            ),
            rx.text(desc, size="2", color=BRAND_COLORS["text_dim"], margin_top="10px"),
            rx.cond(
                is_news & MarketState.processing,
                rx.vstack(rx.progress(value=MarketState.progress_value, width="100%", color_scheme="blue"), rx.text(MarketState.status_text, size="1", color=BRAND_COLORS["accent"], text_align="center"), width="100%", margin_top="15px"),
                rx.vstack(
                    rx.button(
                        "Intelligence Update" if is_news else "Tool öffnen",
                        on_click=MarketState.run_market_intelligence if is_news else None,
                        variant="ghost", width="100%", margin_top="15px",
                        border=f"1px solid {BRAND_COLORS['bg']}", 
                        color=BRAND_COLORS["accent"], # <-- BLAUE SCHRIFT!
                        font_family="'Inter', sans-serif", weight="medium", letter_spacing="0.05em",
                        _hover={"background": BRAND_COLORS["bg"], "color": BRAND_COLORS["text_main"]},
                    ),
                    rx.cond(is_news & (MarketState.last_report != ""), rx.text(MarketState.last_report, size="1", color=BRAND_COLORS["text_dim"]), rx.fragment()),
                    width="100%"
                ),
            ),
            align="start", spacing="1",
        ),
        style=CARD_STYLE,
    )

def index() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.vstack(
                    rx.heading("Commodity Intelligence", size="8", color=BRAND_COLORS["text_main"]),
                    rx.text("Capital Market Advisory & Strategic CRM Monitoring", color=BRAND_COLORS["text_dim"]),
                    align="start",
                ),
                rx.spacer(),
                rx.badge("V 0.1 ALPHA", variant="outline", border_radius="full", padding_x="12px", color_scheme="blue"),
                width="100%", padding_bottom="40px",
            ),
            
            # --- DAS NEUE SUCHFELD ---
            rx.hstack(
                rx.input(
                    placeholder="Keywords (z.B. Kupfer, Gold, Lithium)...",
                    on_change=MarketState.set_search_query, 
                    value=MarketState.search_query,
                    width="400px",
                    background=BRAND_COLORS["card"],
                    border=f"1px solid {BRAND_COLORS['bg']}",
                    color=BRAND_COLORS["text_main"],
                    _focus={"border_color": BRAND_COLORS["accent"]},
                ),
                rx.button(
                    rx.icon(tag="search", size=18),
                    "Analyse starten",
                    on_click=MarketState.run_market_intelligence,
                    background=BRAND_COLORS["accent"],
                    color=BRAND_COLORS["bg"],
                    _hover={"opacity": 0.8, "transform": "scale(1.02)"},
                ),
                spacing="3",
                margin_bottom="30px",
                align="center",
                width="100%"
            ),

            rx.grid(
                app_card("📰", "News-Intelligence", "Echtzeit-Monitoring von Kapitalmarkt-Events und Rohstoff-Deals.", "AKTIV", is_news=True),
                app_card("🏢", "Registry-Audit", "Analyse von Besitzstrukturen und wirtschaftlich Berechtigten.", "IN PLANUNG"),
                app_card("⚖️", "EU Raw Materials Act", "Überwachung regulatorischer Hürden für Investitionsprojekte.", "IN PLANUNG"),
                app_card("📈", "Trend-Algorithmus", "NLP-basierte Mustererkennung in Markt-Datenströmen.", "KONZEPT", help_url="/faq/trend_algorithmus_konzept.html"),
                columns="2", spacing="5", width="100%",
            ),
            rx.cond(
                MarketState.news_data,
                rx.vstack(
                    rx.hstack(
                        rx.heading("Aktuelle Marktsignale", size="6", color=BRAND_COLORS["text_main"]),
                        rx.badge(f"{MarketState.news_data.length()} Signale", color_scheme="blue", variant="soft"),
                        margin_top="60px", margin_bottom="20px", width="100%", align="end",
                    ),
                    rx.box(
                        rx.vstack(rx.foreach(MarketState.news_data, news_row), spacing="0"),
                        width="100%", background=BRAND_COLORS["card"], border=f"1px solid {BRAND_COLORS['bg']}", border_radius="12px", overflow="hidden",
                    ),
                    width="100%",
                ),
                rx.fragment(),
            ),
            rx.hstack(
                rx.text("Reflex Intelligence Engine · Capital Market Unit", size="1", color=BRAND_COLORS["text_dim"]),
                rx.spacer(),
                rx.text("© 2026 EMIAG Intelligence", size="1", color=BRAND_COLORS["text_dim"]),
                width="100%", margin_top="60px", padding_top="20px", border_top=f"1px solid {BRAND_COLORS['bg']}",
            ),
            max_width="1100px", margin="0 auto", padding="40px 24px",
        ),
        background=BRAND_COLORS["bg"], min_height="100vh", font_family="'Inter', sans-serif",
    )

app = rx.App(
    stylesheets=[
        "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap",
    ],
)
app.add_page(index, title="Commodity Intelligence Dashboard")