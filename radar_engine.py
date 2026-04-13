import streamlit as st

def exibir_radar():
    st.header("🌍 Inteligência Radar")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🇺🇸 Mercado EUA")
        if st.button("Varrer TikTok USA", width='stretch'):
            st.info("Analisando tendências de exportação...")
            st.write("1. **Smart Watch V9** (Explodindo)")
            st.write("2. **Mini Seladora Pro** (Alta conversão)")
            
    with col2:
        st.subheader("🇧🇷 Mercado Brasil")
        if st.button("Varrer Shopee BR", width='stretch'):
            st.success("Analisando volume de buscas local...")
            st.write("1. **Mop Giratório** (Topo de vendas)")
            st.write("2. **Utensílios de Silicone** (Estável)")
