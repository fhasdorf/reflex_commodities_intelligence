# -*- coding: utf-8 -*-
# @Author: Frank Hasdorf
# @Date:   07-05-2026 09:42:01
# @Last Modified by:   Frank Hasdorf
# @Last Modified time: 07-05-2026 16:03:36
import reflex as rx
# Das importiert das SitemapPlugin als echte Klasse
from reflex_base.plugins.sitemap import SitemapPlugin 

config = rx.Config(
    app_name="commodity_intelligence",
    disable_plugins=[SitemapPlugin], # Warnung 1 beheben
    # Theme Warnung beheben: Theme wird nun hier definiert
    plugins=[
        rx.plugins.RadixThemesPlugin(theme=rx.theme(appearance="dark", accent_color="gold"))
    ]
)