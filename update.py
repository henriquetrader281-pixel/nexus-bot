# --- DENTRO DA FUNÇÃO dashboard_performance_simples ---

# 1. Adicionamos a coluna 'fonte' na visualização
colunas_visiveis = ["data", "horario_previsto", "produto", "link_afiliado", "status", "copy_funil"]

# 2. Criamos uma lógica simples para identificar a loja pelo link
df['fonte'] = df['link_afiliado'].apply(lambda x: 'Shopee 🟠' if 'shopee' in str(x).lower() else 'Outro ⚪')

# 3. Atualizamos a tabela para mostrar essa nova coluna primeiro
colunas_exibicao = ["data", "horario_previsto", "fonte", "produto", "link_afiliado", "status"]

st.data_editor(
    df[colunas_exibicao].tail(20),
    column_config={
        "fonte": st.column_config.TextColumn("Origem", width="small"),
        "link_afiliado": st.column_config.LinkColumn("Link", display_text="Abrir 🛒")
    },
    disabled=True,
    use_container_width=True,
    hide_index=True
)
