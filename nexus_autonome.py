import os
import time
import requests
from datetime import datetime

def executar_ciclo_autonomo():
    print("🔱 [Nexus Bot] A iniciar ciclo autónomo de descoberta de dores e oferta...")
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    openai_base_url = os.environ.get("OPENAI_API_BASE") or os.environ.get("OPENAI_BASE_URL")
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL") or os.environ.get("WEBHOOK_URL")
    
    resposta_ia = ""
    
    # 1. IA DETECTA DOR E PRODUTO COM COPY HUMANIZADA
    prompt_dor = """
    Analise o comportamento atual do consumidor online e redes sociais. 
    Identifique 1 dor REAL, LATENTE e URGENTE no nicho de casa, produtividade ou eletrónicos.
    
    IMPORTANTE: O PRODUTO deve ser a solução direta e lógica para a DOR detectada.
    
    REGRAS PARA A COPY (ESTILO AGÊNCIA DE ALTO NÍVEL):
    - Gancho (Atenção): Curiosidade ou quebra de padrão.
    - Corpo (Desejo): Transformação e alívio da dor.
    - Escassez/Urgência: O 'segredo' revelado.
    - CTA (Ação): Chamada agressiva e clara.

    Retorne no formato:
    DOR: [descrição]
    PRODUTO: [nome exato do produto físico]
    COPY: [copy de alta conversão com gatilhos e CTA]
    KEYWORDS_LEADS: [3 termos de busca de alta intenção]
    PROMPT_IMAGEM: [descrição visual do produto]
    """

    if openai_api_key:
        try:
            from openai import OpenAI
            client_kwargs = {"api_key": openai_api_key}
            if openai_base_url:
                client_kwargs["base_url"] = openai_base_url
            client = OpenAI(**client_kwargs)
            chat = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "Você é um Copywriter Senior focado em conversão agressiva para e-commerce. Use gatilhos mentais e estruturas de vendas validadas."},
                    {"role": "user", "content": prompt_dor}
                ],
                model="gpt-4o-mini",
                temperature=0.9
            )
            resposta_ia = chat.choices[0].message.content.strip()
        except Exception as e:
            print(f"⚠️ Erro com OpenAI: {e}")

    if not resposta_ia:
        print("❌ ERRO: Nenhuma IA válida conseguiu responder.")
        return

    print("💡 [Nexus Bot] Inteligência gerada com sucesso!")
    
    # 2. SIMULAR CAPTURA DE LEADS COM AS KEYWORDS GERADAS
    # Em um cenário real, aqui dispararíamos buscas em APIs de redes sociais.
    
    id_afiliado = "18316451024"
    link_afiliado = f"https://shopee.com.br/universal-link/search?smtt=0.0.{id_afiliado}&keyword=produto"
    
    mensagem_final = f"🚨 **NEXUS AUTÓNOMO: OPORTUNIDADE DETECTADA** 🚨\n\n{resposta_ia}\n\n🛒 **Link:** {link_afiliado}\n\n🎯 *Aguardando disparo automático para leads detectados...*"
    
    # 3. DISPARO PARA WEBHOOK (AUTOMAÇÃO DE POSTAGEM)
    if webhook_url and webhook_url != "SEU_WEBHOOK_AQUI":
        payload = {"content": mensagem_final}
        try:
            resp = requests.post(webhook_url, json=payload, timeout=20)
            if resp.status_code < 300:
                print("✅ [Nexus Bot] Ciclo completo enviado para o postador!")
            else:
                print(f"⚠️ [Nexus Bot] Falha no webhook: {resp.status_code}")
        except Exception as e:
            print(f"⚠️ Erro ao enviar webhook: {e}")
    else:
        print("ℹ️ [Nexus Bot] Simulação concluída com sucesso localmente.")
        print("-" * 30)
        print(mensagem_final)
        
    return resposta_ia

if __name__ == "__main__":
    executar_ciclo_autonomo()
