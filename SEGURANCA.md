# Segurança e configuração de acesso

O Nexus Bot exige uma senha definida explicitamente na variável `NEXUS_PASSWORD`. A aplicação não possui mais uma senha padrão embutida, evitando que uma publicação sem configuração exponha o painel com uma credencial previsível.

## Execução local

Antes de iniciar o Streamlit, defina uma senha forte no ambiente:

```bash
export NEXUS_PASSWORD='substitua-por-uma-senha-forte'
streamlit run app.py
```

Também é possível definir o segredo no arquivo `.streamlit/secrets.toml`, que não deve ser versionado:

```toml
NEXUS_PASSWORD = "substitua-por-uma-senha-forte"
```

Se o segredo não estiver configurado, o Nexus permanece bloqueado e mostra uma orientação na tela. Para testes automatizados, use uma senha temporária apenas no ambiente de teste; nunca reutilize credenciais reais.

A comparação da senha utiliza comparação em tempo constante e o valor digitado é removido da sessão após uma tentativa bem-sucedida. Ainda assim, a autenticação do Streamlit deve ser protegida por HTTPS e por controles de acesso da infraestrutura quando o painel for publicado na internet.
