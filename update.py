import pandas as pd
import os
import streamlit as st
from datetime import datetime

# MANTENDO SEUS NOMES DE ARQUIVOS ORIGINAIS
PATH_LOG = "nexus_performance.csv"    # O que aparece no Raio-X
PATH_ROTEIROS = "nexus_roteiros.csv"  # Onde a IA guarda os textos longos

def exibir_dashboard():
    """Função principal para renderizar o Dashboard na aba correspondente"""
    st.markdown("""
        <div style="background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%); padding: 20px; border-radius: 15px; text-align: center; border: 1px solid #3b82f6; margin-bottom: 20px;">
            <h2 style="color: white; margin: 0;">📊 DASHBOARD DE PERFORMANCE ESTRATOSFÉRICA</h2>
            <p style="color: #60a5fa; font-size: 0.9em;">Métricas de Conversão | Rastreio Afiliado Ativo</p>
        </div>
    """, unsafe_allow_html=True)

    if not os.path.exists(PATH_LOG):
        st.info("📊 Aguardando primeira mineração para gerar indicadores... Rode o 'Motor Autônomo' ou o 'Scanner' primeiro.")
        # Criar um arquivo de exemplo se não existir para o usuário ver algo
        registrar_mineracao("Exemplo: Luminária LED", "https://shopee.com.br", 95)
        st.rerun()

    try:
        df = pd.read_csv(PATH_LOG, on_bad_lines='skip', engine='python')
        
        if not df.empty:
            # --- MÉTRICAS DE IMPACTO ---
            total_produtos = len(df)
            media_calor = int(df['calor'].mean()) if 'calor' in df.columns else 0
            receita_est = total_produtos * 85 # Estimativa de R$ 85 por venda
            
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("📦 Alvos Detectados", total_produtos, "Nexus Intelligence")
            with c2:
                st.metric("🌡️ Calor Médio", f"{media_calor}°C", "Alta Potência")
            with c3:
                st.metric("💰 Potencial de Ganho", f"R$ {receita_est}", "ROI 4.5x")

            st.divider()

            col_grafico, col_tabela = st.columns([1, 1.5])

            with col_grafico:
                st.markdown("📈 **Tendência de Venda (Calor)**")
                if 'calor' in df.columns:
                    st.line_chart(df['calor'], height=250)

            with col_tabela:
                st.markdown("📋 **Últimos Alvos Sincronizados**")
                st.dataframe(
                    df.tail(10),
                    use_container_width=True,
                    hide_index=True
                )
        else:
            st.info("Base de dados vazia. Inicie o Ciclo Autônomo!")
    except Exception as e:
        st.error(f"Erro ao carregar Dashboard: {e}")

def registrar_mineracao(nome, link, calor):
    """Salva os dados minerados no CSV para o Dashboard ler"""
    data_hoje = datetime.now().strftime("%d/%m/%Y %H:%M")
    novo_dado = pd.DataFrame([[data_hoje, nome, link, calor]], 
                            columns=['data', 'produto', 'link', 'calor'])
    
    if not os.path.exists(PATH_LOG):
        novo_dado.to_csv(PATH_LOG, index=False)
    else:
        novo_dado.to_csv(PATH_LOG, mode='a', header=False, index=False)

def carregar_logs():
    """Função de compatibilidade para o app.py"""
    if os.path.exists(PATH_LOG):
        try:
            return pd.read_csv(PATH_LOG)
        except:
            return pd.DataFrame()
    return pd.DataFrame()
