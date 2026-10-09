import json
import anthropic

_client = anthropic.Anthropic()
_MODEL = "claude-sonnet-4-5"

_SYSTEM = """Você é um especialista em qualificação de leads para mentoria individual de IA estratégica.
O mentor é Elvizio Vanzo, que atende profissionais de saúde, acadêmicos e pequenas empresas.

Analise a mensagem do lead e classifique-o como:
- QUENTE: alto interesse, dor clara, pronto para comprar
- MORNO: interesse moderado, ainda explorando opções
- FRIO: curiosidade superficial, sem urgência ou orçamento

Responda APENAS com um objeto JSON válido com as seguintes chaves:
{
  "classificacao": "QUENTE" | "MORNO" | "FRIO",
  "pontuacao": 0-100,
  "justificativa": "explicação em 2-3 frases",
  "pontos_fortes": ["lista", "de", "pontos"],
  "pontos_atencao": ["lista", "de", "pontos"],
  "proximo_passo_recomendado": "ação recomendada"
}"""


def qualificar_lead(nome: str, mensagem: str) -> dict:
    prompt = f"Nome do lead: {nome}\n\nMensagem recebida:\n{mensagem}"

    response = _client.messages.create(
        model=_MODEL,
        max_tokens=1024,
        system=_SYSTEM,
        messages=[{"role": "user", "content": prompt}],
    )

    text = response.content[0].text.strip()

    start = text.find("{")
    end = text.rfind("}") + 1
    if start != -1 and end > start:
        try:
            return json.loads(text[start:end])
        except json.JSONDecodeError:
            pass

    return {
        "classificacao": "MORNO",
        "pontuacao": 50,
        "justificativa": "Não foi possível analisar completamente a mensagem.",
        "pontos_fortes": [],
        "pontos_atencao": ["Análise incompleta"],
        "proximo_passo_recomendado": "Entrar em contato para coletar mais informações",
    }
