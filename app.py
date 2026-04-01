import streamlit as st
from groq import Groq
import urllib.parse
import requests
import pandas as pd
from datetime import datetime
import os
import json

# --- 1. CONFIGURAÇÃO E ENGINE ---
st.set_page_config(page_title="Nexus Absolute V51", layout="wide", page_icon="🔱")
DATA_PATH = "dataset_nexus.csv"

def carregar_dados():
    if not os.path.exists(DATA_PATH):
        df = pd.DataFrame(columns=["data", "produto", "roteiro", "status", "link_afiliado", "copy_funil"])
        df.to_csv(DATA_PATH, index=False)
    return pd.read_csv(DATA_PATH)

client = Groq(api_key=st.secrets.get("GROQ_API_KEY"))

def gerar_ia(prompt):
    return client.chat.completions.create(
        model="llama-3.3-70b-versatile", 
        messages=[{"role":"user","content": prompt}]
    ).choices[0].message.content

# --- 2. INTERFACE PENSANTE ---
st.title("🔱 Nexus Brain V51: O Fluxo Perfeito")

tabs = st.tabs(["🔎 Mineração & Seleção", "🚀 Arsenal (Auto-Process)", "🕹️ Central de Disparo"])

# Inicializa estados de seleção
if 'sel_nome' not in st.session_state: st.session_state.sel_nome = ""
if 'sel_link' not in st.session_state: st.session_state.sel_link = ""

with tabs[0]:
    st.header("🎯 Inteligência de Mercado")
    nicho = st.text_input("Defina o Nicho:", value="Utilidades Criativas")
    
    if st.button("🔄 Minerar Oportunidades"):
        with st.status("Varrendo mercado..."):
            # Pedimos para a IA formatar como JSON para o seletor funcionar
            prompt = f"Liste 5 produtos virais de {nicho} na Shopee. Retorne APENAS um JSON: [{{'nome': 'item', 'link': 'url'}}, ...]"
            res = gerar_ia(prompt)
            try:
                # Tenta limpar o texto caso a IA mande conversa fora do JSON
                json_start = res.find('[')
                json_end = res.rfind(']') + 1
                st.session_state['lista_bruta'] = json.loads(res[json_start:json_end])
            except:
                st.error("Erro ao processar lista. Tente minerar novamente.")

    if 'lista_bruta' in st.session_state:
        for prod in st.session_state['lista_bruta']:
            col_txt, col_btn = st.columns([4, 1])
            col_txt.write(f"📦 **{prod['nome']}**")
            if col_btn.button("Selecionar", key=prod['nome']):
                st.session_state.sel_nome = prod['nome']
                st.session_state.sel_link = prod['link']
                st.success(f"{prod['nome']} enviado para o Arsenal!")

with tabs[1]:
    st.header("🚀 Processamento de Arsenal Automático")
    
    # Preenchimento automático vindo da aba 1
    c1, c2 = st.columns(2)
    p_nome = c1.text_input("Produto:", value=st.session_state.sel_nome)
    p_link = c2.text_input("Link Original:", value=st.session_state.sel_link)
    
    if st.button("⚡ INICIAR FLUXO TOTAL (Arsenal + Vídeos + Links)"):
        if p_nome and p_link:
            with st.status("Nexus processando 4 variações únicas..."):
                aff_id = st.secrets.get("SHOPEE_ID", "ID_AFILIADO")
                link_final = f"https://shope.ee/api/v1/deeplink?url={urllib.parse.quote(p_link)}&aff_id={aff_id}"
                
                # Gera 4 roteiros com estilos diferentes para não dar plágio
                prompt_rot = f"Crie 4 roteiros de 15s para {p_nome}. Varie os ganchos (Curiosidade, Medo de Perder, ASMR, Benefício). Separe por ###"
                roteiros = gerar_ia(prompt_rot).split("###")
                
                df = carregar_dados()
                for i, rot in enumerate(roteiros):
                    if len(rot) > 10:
                        copy = gerar_ia(f"Crie legenda viral e hashtags para este vídeo: {rot}")
                        novo = {
                            "data": datetime.now().strftime("%d/%m"),
                            "produto": f"{p_nome} (Var {i+1})",
                            "roteiro": rot.strip(),
                            "copy_funil": copy,
                            "link_afiliado": link_final,
                            "status": "PRONTO PARA POSTAGEM"
                        }
                        df = pd.concat([df, pd.DataFrame([novo])], ignore_index=True)
                df.to_csv(DATA_PATH, index=False)
                st.success("✅ VÍDEOS OK! Arsenal carregado na Central de Disparo.")
        else:
            st.warning("Selecione um produto na aba anterior ou digite os dados.")

with tabs[2]:
    st.header("🕹️ Central de Disparo (Fix Make/TikTok)")
    df_disparo = carregar_dados()
    fila = df_disparo[df_disparo["status"] == "PRONTO PARA POSTAGEM"]
    
    if not fila.empty:
        st.write(f"Você tem **{len(fila)}** vídeos prontos.")
        if st.button("🚀 DISPARAR TUDO PARA MAKE/BUFFER", type="primary"):
            webhook = st.secrets.get("WEBHOOK_POSTAGEM")
            headers = {"Content-Type": "application/json"}
            
            sucessos = 0
            for i, row in fila.iterrows():
                payload = {
                    "produto": row['produto'],
                    "roteiro": row['roteiro'],
                    "legenda": row['copy_funil'],
                    "link": row['link_afiliado'],
                    "instante": datetime.now().strftime("%H:%M:%S")
                }
                try:
                    r = requests.post(webhook, data=json.dumps(payload), headers=headers, timeout=10)
                    if r.status_code in [200, 201]:
                        df_disparo.at[i, "status"] = "ENVIADO"
                        sucessos += 1
                except:
                    continue
            
            df_disparo.to_csv(DATA_PATH, index=False)
            st.success(f"🔥 {sucessos} itens enviados com sucesso!")
            st.rerun()
    else:
        st.info("Nenhum item pronto para disparo.")
