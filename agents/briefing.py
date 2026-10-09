import anthropic

_client = anthropic.Anthropic()
_MODEL = "claude-sonnet-4-5"

_SYSTEM = """Você é o assistente executivo do mentor Elvizio Vanzo.
Gere um briefing profissional e conciso para o mentor se preparar para uma conversa com um lead.
Use Markdown com seções claras. Seja direto e estratégico."""


def gerar_briefing(
    nome: str,
    mensagem: str,
    classificacao: dict,
    dm_gerada: str,
    horarios: dict,
) -> str:
    temperatura = classificacao.get("classificacao", "—")
    pontuacao = classificacao.get("pontuacao", "—")
    justificativa = classificacao.get("justificativa", "—")
    pontos_fortes = classificacao.get("pontos_fortes", [])
    pontos_atencao = classificacao.get("pontos_atencao", [])
    proximo_passo = classificacao.get("proximo_passo_recomendado", "—")

    horarios_str = ""
    for h in horarios.get("horarios", []):
        horarios_str += f"- {h.get('data', '')} às {h.get('hora', '')} ({h.get('duracao', '30 min')})\n"

    prompt = f"""Crie um briefing executivo para o mentor Elvizio Vanzo sobre o seguinte lead:

**Nome:** {nome}
**Mensagem original:** {mensagem}

**Qualificação:**
- Temperatura: {temperatura} (pontuação: {pontuacao}/100)
- Justificativa: {justificativa}
- Pontos fortes: {', '.join(pontos_fortes) if pontos_fortes else 'N/A'}
- Pontos de atenção: {', '.join(pontos_atencao) if pontos_atencao else 'N/A'}
- Próximo passo recomendado: {proximo_passo}

**DM enviada:**
{dm_gerada}

**Horários propostos:**
{horarios_str or 'Nenhum horário disponível'}

Estruture o briefing com as seções:
## Perfil do Lead
## Dor / Objetivo Principal
## Temperatura e Justificativa
## Ângulo de Abordagem Recomendado
## Pontos de Atenção
## Horários Propostos
## Notas Finais para Elvizio"""

    response = _client.messages.create(
        model=_MODEL,
        max_tokens=2048,
        system=_SYSTEM,
        messages=[{"role": "user", "content": prompt}],
    )

    return response.content[0].text.strip()
