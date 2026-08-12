import os
import json
import requests

def executar_ciclo_completo():
    print("🔱 [Nexus Master] Iniciando ciclo completo...")
    
    # Exemplo de dados de alta conversão caso a API falhe
    dados = {
        "dor": "Cansaço visual e falta de foco no home office devido a iluminação inadequada.",
        "produto": "Luminária de Monitor LED Anti-Reflexo",
        "copy_reels": "Gente, parei de ter dor de cabeça no trabalho! Esse segredo aqui salvou meus olhos e meu foco. Comenta QUERO que te mando o link com desconto!",
        "keywords": ["alguém recomenda luminária monitor", "melhor luz para home office", "olho cansado pc"],
        "image_prompt": "Foto realista de um setup gamer minimalista com uma luminária de monitor LED ligada, luz quente, ambiente aconchegante, 4k, estilo Pinterest."
    }
    
    # Tenta usar a IA se a chave estiver presente
    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key, base_url=os.environ.get("OPENAI_API_BASE"))
            resp = client.chat.completions.create(
                messages=[{"role": "user", "content": "Gere um JSON para um produto viral de afiliado com dor, produto, copy_reels, keywords e image_prompt."}],
                model="gpt-4o-mini",
                response_format={"type": "json_object"}
            )
            dados = json.loads(resp.choices[0].message.content)
        except:
            print("⚠️ Usando dados pré-configurados de alta conversão.")

    with open("nexus_manifest.json", "w") as f:
        json.dump(dados, f)
    
    print(f"✅ Inteligência Nexus pronta para: {dados['produto']}")
    return dados

if __name__ == "__main__":
    executar_ciclo_completo()
