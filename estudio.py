import streamlit as st
import urllib.parse

def exibir_estudio(miny, motor_ia):
    st.markdown("### 🎬 Estúdio de Edição Nexus | Retenção & AIDA 🔱")
    
    # 1. SEGURANÇA
    if "sel_nome" not in st.session_state or not st.session_state.sel_nome:
        st.warning("⚠️ Selecione um produto no Scanner antes de entrar no Estúdio!")
        return

    # 2. LIMPEZA DO NOME DO PRODUTO
    produto_foco = st.session_state.sel_nome.split('|')[0].replace("NOME:", "").strip()

    # 3. MÁQUINA DE LINKS (À prova de falhas)
    nome_formatado_url = urllib.parse.quote(produto_foco)
    link_perfeito = f"https://shopee.com.br/search?keyword={nome_formatado_url}&smtt=18316451024"

    # --- 🔗 INTEGRAÇÃO COM O ARSENAL ---
    if "copy_ativa" in st.session_state and st.session_state.copy_ativa != "":
        st.success("✅ Copy de Alta Conversão recebida do Arsenal!")
        st.session_state.copy_final_pronta = f"{st.session_state.copy_ativa}\n\n🛒 **COMPRE AQUI:** {link_perfeito}"
        st.session_state.copy_ativa = ""

    # --- CONTAINER DA LEGENDA ---
    with st.container(border=True):
        st.markdown(f"#### 🎯 Estratégia: **{produto_foco}**")
        
        if st.button("🔥 GERAR NOVA MUNIÇÃO AIDA + LINK", use_container_width=True):
            with st.spinner("Buscando dados reais do produto e gerando legenda..."):
                
                # PROMPT RAG SIMULADO: Inteligente e direto
                prompt_aida = f"""MUDE AS REGRAS. IGNORE A LISTA DE 30 PRODUTOS.
Preciso de UMA legenda para o produto '{produto_foco}'.
PASSO 1: Lembre-se de 2 características técnicas e 2 benefícios reais que os compradores buscam neste produto.
PASSO 2: Escreva a legenda usando esses dados reais para dar credibilidade.
- Comece tocando numa dor ou problema comum.
- Apresente o produto com os dados técnicos.
- Termine com: 'Comenta EU QUERO que te mando o link no Direct!'
NÃO use a palavra 'http' e NÃO liste outros produtos."""
                
                try:
                    resultado = miny.minerar_produtos(prompt_aida, "Shopee", motor_ia)
                    
                    # FILTRO SNIPER (Apaga só o que é lixo da IA, protege o texto)
                    linhas_limpas = []
                    for linha in resultado.split('\n'):
                        # Se for a lista padrão do Scanner, ele ignora
                        if "CALOR:" in linha or "TICKET:" in linha:
                            continue
                        # Se a IA teimar em colocar um link solto, ele ignora
                        if "shopee.com.br" in linha:
                            continue
                        linhas_limpas.append(linha)
                    
                    texto_final_ia = "\n".join(linhas_limpas).strip()
                    
                    # Se por algum motivo a IA travar e não devolver nada, avisamos
                    if not texto_final_ia:
                        texto_final_ia = "⚠️ A IA não conseguiu formatar o texto. Clique em Gerar novamente."

                    # Junta o texto com a Máquina de Links
                    st.session_state.copy_final_pronta = f"{texto_final_ia}\n\n🛒 **SEU LINK DE AFILIADO:** {link_perfeito}"
                    st.rerun()
                except Exception as e:
                    st.error(f"Aguarde o reset da IA: {str(e)}")

        if "copy_final_pronta" in st.session_state:
            st.text_area("Sua munição (Legenda Viral + Link Shopee):", value=st.session_state.copy_final_pronta, height=200)

    st.divider()

    # --- CONTAINER DO ROTEIRO ---
    st.markdown("#### 🎥 Mapa de Cortes (Direção de Arte)")
    if st.button("🧠 GERAR ROTEIRO DE ALTA RETENÇÃO", use_container_width=True):
        with st.spinner("Criando mapa de cenas..."):
            prompt_video = f"""IGNORE BUSCA. Atue como Diretor de Marketing. Crie um roteiro prático de 15s para o vídeo de '{produto_foco}'.
Divida no formato:
[0-3s] HOOK VISUAL: Cena inicial.
[3-10s] DESEJO: O que mostrar.
[10-15s] CTA: O que escrever na tela."""
            try:
                res_roteiro = miny.minerar_produtos(prompt_video, "Shopee", motor_ia)
                
                linhas_rot = []
                for linha in res_roteiro.split('\n'):
                    if "CALOR:" not in linha:
                        linhas_rot.append(linha)
                        
                st.session_state.roteiro_video = "\n".join(linhas_rot).strip()
                st.rerun()
            except:
                st.error("IA em resfriamento. Tente em instantes.")

    if "roteiro_video" in st.session_state:
        with st.expander("🎞️ ROTEIRO CAPCUT", expanded=True):
            st.markdown(st.session_state.roteiro_video)
