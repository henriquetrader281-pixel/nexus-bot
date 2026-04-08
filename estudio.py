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

    # 3. MÁQUINA DE LINKS (Gera o link perfeito da Shopee sem depender do Scanner)
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
            with st.spinner("Forçando IA a agir como Especialista em Reels..."):
                
              # NOVO PROMPT: Simula a leitura da página do produto (RAG Simulado)
                prompt_aida = f"""Atue como um Copywriter Sênior de Instagram Reels especializado em produtos da Shopee.
Produto: '{produto_foco}'.
PASSO 1: Busque no seu conhecimento quais são as 2 principais características TÉCNICAS e os 2 maiores BENEFÍCIOS reais que os clientes mais procuram quando compram '{produto_foco}'.
PASSO 2: Use essas informações reais para escrever UMA legenda persuasiva e viral em formato AIDA.
- Início (Dor): Comece tocando na ferida ou problema diário.
- Meio (Solução Real): Apresente o produto usando as características técnicas reais que você levantou no Passo 1 para dar credibilidade (ex: material, durabilidade, facilidade).
- Fim (CTA): Termine OBRIGATORIAMENTE com: 'Comenta EU QUERO que te mando o link no Direct!'
ATENÇÃO: NÃO mostre o Passo 1 para o usuário. Entregue APENAS o texto final da legenda pronto para postar. NÃO liste produtos."""
                
                try:
                    resultado = miny.minerar_produtos(prompt_aida, "Shopee", motor_ia)
                    
                    # Filtro físico contra listas
                    linhas_limpas = []
                    for linha in resultado.split('\n'):
                        if "NOME:" not in linha and "CALOR:" not in linha and "http" not in linha:
                            linhas_limpas.append(linha)
                    
                    texto_final_ia = "\n".join(linhas_limpas).strip()

                    # Junta o texto com a Máquina de Links que criamos acima
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
            prompt_video = f"""IGNORE BUSCA. Atue como Diretor de Marketing. Crie um roteiro de edição prático de 15s para o produto: {produto_foco}.
Divida a edição no formato AIDA visual:
[0-3s] HOOK VISUAL: Cena para prender a atenção.
[3-10s] DESEJO/DOR: Demonstração do produto.
[10-15s] CTA: Chamada final na tela."""
            try:
                res_roteiro = miny.minerar_produtos(prompt_video, "Shopee", motor_ia)
                
                linhas_rot = []
                for linha in res_roteiro.split('\n'):
                    if "NOME:" not in linha and "CALOR:" not in linha:
                        linhas_rot.append(linha)
                        
                st.session_state.roteiro_video = "\n".join(linhas_rot).strip()
                st.rerun()
            except:
                st.error("IA em resfriamento. Tente em instantes.")

    if "roteiro_video" in st.session_state:
        with st.expander("🎞️ ROTEIRO CAPCUT", expanded=True):
            st.markdown(st.session_state.roteiro_video)
