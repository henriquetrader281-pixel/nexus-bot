import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from backtest_engine import executar_backtest_estrategico

def gerar_grafico_projeção(prateleira="🔥 Virais & Desejo"):
    budgets = np.arange(20, 520, 20)
    data = []
    
    for b in budgets:
        res = executar_backtest_estrategico(b, prateleira)
        data.append({
            "Orçamento Diário (R$)": b,
            "Lucro Líquido (R$)": res['lucro_estimado'],
            "ROI (%)": res['roi']
        })
        
    df = pd.DataFrame(data)
    
    fig, ax1 = plt.subplots(figsize=(10, 6))
    
    color = 'tab:blue'
    ax1.set_xlabel('Orçamento Diário (R$)')
    ax1.set_ylabel('Lucro Líquido (R$)', color=color)
    ax1.plot(df["Orçamento Diário (R$)"], df["Lucro Líquido (R$)"], color=color, marker='o', label='Lucro Líquido')
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.grid(True, linestyle='--', alpha=0.7)
    
    ax2 = ax1.twinx()
    color = 'tab:red'
    ax2.set_ylabel('ROI (%)', color=color)
    ax2.plot(df["Orçamento Diário (R$)"], df["ROI (%)"], color=color, linestyle='--', marker='x', label='ROI (%)')
    ax2.tick_params(axis='y', labelcolor=color)
    
    plt.title(f'Projeção de Escala: {prateleira}')
    fig.tight_layout()
    
    output_path = "/home/ubuntu/nexus-bot/projecao_escala.png"
    plt.savefig(output_path)
    return output_path

if __name__ == "__main__":
    path = gerar_grafico_projeção()
    print(f"Gráfico gerado em: {path}")
