import pandas as pd
import os

def executar_manutencao():
    print("🔱 Nexus Absolute: Iniciando Protocolo de Correção...")
    
    # 1. Correção do Banco de Dados (CSV)
    DATA_PATH = "nexus_master_data.csv"
    colunas_corretas = ["data", "produto", "status", "views", "cliques", "vendas", "faturamento", "copy", "link"]
    
    try:
        if os.path.exists(DATA_PATH):
            df = pd.read_csv(DATA_PATH)
            # Verifica se todas as colunas existem, se não, reconstrói
            for col in colunas_corretas:
                if col not in df.columns:
                    df[col] = ""
            df.to_csv(DATA_PATH, index=False)
            print("✅ Linha 15: Banco de Dados sincronizado e colunas corrigidas.")
        else:
            pd.DataFrame(columns=colunas_corretas).to_csv(DATA_PATH, index=False)
            print("✅ Linha 18: Novo banco de dados criado do zero.")
    except Exception as e:
        print(f"❌ Erro ao corrigir CSV: {e}")

    # 2. Limpeza de Cache de Vídeos
    if not os.path.exists("videos"):
        os.makedirs("videos")
        print("✅ Linia 24: Pasta /videos criada.")

    # 3. Verificação de Cookies
    if not os.path.exists("cookies"):
        os.makedirs("cookies")
        print("✅ Linha 28: Pasta /cookies preparada.")

    print("\n🚀 Sistema pronto para voltar ao combate! Reinicie o Streamlit.")

if __name__ == "__main__":
    executar_manutencao()
