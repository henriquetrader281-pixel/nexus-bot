# ManyChat no Nexus Bot: webhook sem credenciais

O Nexus Bot não precisa de usuário, senha ou token do ManyChat quando usa um **endpoint HTTP externo**. A única configuração no Streamlit é a URL HTTPS que receberá o `POST` do Nexus. Essa URL pode ser um webhook personalizado do Make, Zapier, n8n ou um endpoint próprio.

> Importante: o bloco **External Request** do ManyChat normalmente envia dados do fluxo ManyChat para um serviço externo. Ele não significa automaticamente que o ManyChat forneceu uma URL de entrada para o Nexus. Para o sentido **Nexus → ManyChat**, use um endpoint intermediário, como um Custom Webhook do Make, e depois conecte esse cenário ao ManyChat; ou use a API oficial do ManyChat, que é um fluxo diferente e pode exigir autenticação própria.

## Configuração recomendada: Nexus → Make → ManyChat

### 1. Criar o endpoint que receberá o Nexus

Acesse o [Make](https://www.make.com/), crie um cenário e adicione **Webhooks → Custom webhook**. Clique em **Add**, copie a URL HTTPS gerada e use-a como `MANYCHAT_WEBHOOK_URL`.

No cenário, adicione a etapa do ManyChat que deve executar a automação. Mapeie os campos recebidos:

```json
{
  "produto": "nome do produto",
  "link_afiliado": "https://...",
  "copy": "legenda pronta",
  "trigger": "QUERO",
  "test_mode": false
}
```

### 2. Adicionar a URL aos Secrets do Streamlit

Em **Streamlit Cloud → Settings → Secrets**, adicione somente a URL do endpoint:

```toml
MANYCHAT_WEBHOOK_URL = "https://hook.us1.make.com/seu-endpoint"
```

Não coloque token, senha ou credencial do ManyChat nessa variável.

### 3. Validar sem disparar cliente real

O Nexus inclui `validate_social_credentials.py`. O comando abaixo verifica formato e credenciais do Pinterest, mas não envia nada ao ManyChat:

```bash
python validate_social_credentials.py
```

Para enviar um evento técnico controlado ao endpoint, use explicitamente:

```bash
python validate_social_credentials.py --send-manychat-test
```

O payload de teste possui `test_mode=true`, produto fictício e gatilho `NEXUS_TEST`; ele não deve ser usado para acionar uma DM comercial. No Make, configure uma rota/filtro que ignore eventos com `test_mode=true`.

### 4. Verificar a entrega

O HTTP `2xx` confirma apenas que o endpoint aceitou a requisição. Depois, verifique no histórico do Make e no fluxo do ManyChat se a automação recebeu os campos corretamente. O Nexus não pode confirmar sozinho que uma DM foi entregue ao usuário final sem uma confirmação adicional do provedor.

## Checklist

| Item | Status esperado |
|---|---|
| URL HTTPS do endpoint | Obrigatória |
| Token do ManyChat no Nexus | Não necessário neste fluxo |
| `MANYCHAT_WEBHOOK_URL` nos Secrets | Obrigatório |
| Filtro `test_mode=true` no Make | Recomendado |
| Teste técnico antes de publicar | Obrigatório |
| Confirmação no histórico do endpoint | Obrigatória |

Referências: [ManyChat External Request](https://help.manychat.com/hc/en-us/articles/14281285374364-Dev-Tools-External-request) e [Make Custom Webhooks](https://www.make.com/en/help/tools/webhooks).
