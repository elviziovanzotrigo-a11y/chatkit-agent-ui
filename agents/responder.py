import anthropic

_client = anthropic.Anthropic()
_MODEL = "claude-sonnet-4-5"

_SYSTEM = """Você escreve respostas de Instagram DM para o mentor Elvizio Vanzo.
Elvizio oferece mentoria individual de IA estratégica para profissionais de saúde, acadêmicos e pequenas empresas.

Escreva uma resposta direta, acolhedora e profissional com:
- 3 a 5 frases curtas
- Máximo 2 emojis
- Tom: profissional, direto e empático
- NÃO mencione a classificação interna do lead
- Incentive o próximo passo (agendar uma conversa)"""


def gerar_resposta_dm(nome: str, mensagem: str, classificacao: dict) -> str:
    temperatura = classificacao.get("classificacao", "MORNO")
    proximo_passo = classificacao.get("proximo_passo_recomendado", "")

    prompt = (
        f"Lead: {nome}\n"
        f"Mensagem dele: {mensagem}\n"
        f"Contexto interno (não mencionar): temperatura={temperatura}, próximo passo sugerido={proximo_passo}\n\n"
        "Escreva a resposta de DM para este lead."
    )

    response = _client.messages.create(
        model=_MODEL,
        max_tokens=512,
        system=_SYSTEM,
        messages=[{"role": "user", "content": prompt}],
    )

    return response.content[0].text.strip()
