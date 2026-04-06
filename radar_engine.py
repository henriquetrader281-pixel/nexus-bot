import streamlit as st

def obter_trends_globais(regiao="USA"):
    """
    Simula ou conecta com APIs de tendências.
    """
    if regiao == "USA":
        return "🇺🇸 [RADAR EUA]: 1. Smart Watch V9 | 2. Protetor Solar UV-C | 3. Mini Seladora Pro"
    else:
        return "🇧🇷 [TRENDS BR]: 1. Mop Giratório | 2. Fone Bluetooth Gamer | 3. Utensílios de Silicone"
