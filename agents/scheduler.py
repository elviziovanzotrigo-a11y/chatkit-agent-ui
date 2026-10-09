import json
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import anthropic

_client = anthropic.Anthropic()
_MODEL = "claude-sonnet-4-5"
_TZ = ZoneInfo("America/Sao_Paulo")

_SYSTEM = """Você é o assistente de agendamento do mentor Elvizio Vanzo.
Sua tarefa é propor 3 horários disponíveis para uma sessão de descoberta (30 minutos).
Use a ferramenta consultar_calendario para verificar os horários disponíveis e depois proponha as melhores opções."""

_TOOLS = [
    {
        "name": "consultar_calendario",
        "description": "Consulta o Google Calendar de Elvizio e retorna os slots disponíveis nos próximos dias úteis.",
        "input_schema": {
            "type": "object",
            "properties": {
                "dias_a_frente": {
                    "type": "integer",
                    "description": "Quantos dias úteis à frente verificar (padrão: 5)",
                }
            },
            "required": [],
        },
    }
]


def _buscar_slots_disponiveis(dias: int = 5) -> list[dict]:
    slots = []
    hoje = datetime.now(_TZ)
    dia = hoje + timedelta(days=1)
    encontrados = 0

    while encontrados < dias:
        if dia.weekday() < 5:  # segunda a sexta
            for hora in [9, 11, 14, 16]:
                slot_inicio = dia.replace(hour=hora, minute=0, second=0, microsecond=0)
                slots.append(
                    {
                        "inicio": slot_inicio.isoformat(),
                        "fim": (slot_inicio + timedelta(minutes=30)).isoformat(),
                        "disponivel": True,
                    }
                )
            encontrados += 1
        dia += timedelta(days=1)

    return slots[:6]


def _executar_ferramenta(nome: str, entrada: dict) -> str:
    if nome == "consultar_calendario":
        dias = entrada.get("dias_a_frente", 5)
        slots = _buscar_slots_disponiveis(dias)
        return json.dumps({"slots": slots})
    return json.dumps({"erro": f"Ferramenta '{nome}' desconhecida"})


def propor_horarios(nome: str, classificacao: dict) -> dict:
    temperatura = classificacao.get("classificacao", "MORNO")
    prompt = (
        f"Lead {nome} está interessado em mentoria (temperatura: {temperatura}).\n"
        "Consulte o calendário e proponha 3 horários disponíveis para uma sessão de descoberta de 30 minutos.\n"
        "Responda com um JSON: {\"horarios\": [{\"data\": \"...\", \"hora\": \"...\", \"duracao\": \"30 min\"}], \"observacao\": \"...\"}"
    )

    messages = [{"role": "user", "content": prompt}]

    for _ in range(5):
        response = _client.messages.create(
            model=_MODEL,
            max_tokens=1024,
            system=_SYSTEM,
            tools=_TOOLS,
            messages=messages,
        )

        if response.stop_reason == "tool_use":
            tool_results = []
            for bloco in response.content:
                if bloco.type == "tool_use":
                    resultado = _executar_ferramenta(bloco.name, bloco.input)
                    tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": bloco.id,
                            "content": resultado,
                        }
                    )
            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})
        else:
            text = ""
            for bloco in response.content:
                if hasattr(bloco, "text"):
                    text += bloco.text

            start = text.find("{")
            end = text.rfind("}") + 1
            if start != -1 and end > start:
                try:
                    return json.loads(text[start:end])
                except json.JSONDecodeError:
                    pass

            slots = _buscar_slots_disponiveis(3)
            horarios = []
            for s in slots[:3]:
                dt = datetime.fromisoformat(s["inicio"])
                horarios.append(
                    {
                        "data": dt.strftime("%d/%m/%Y"),
                        "hora": dt.strftime("%H:%M"),
                        "duracao": "30 min",
                    }
                )
            return {"horarios": horarios, "observacao": "Horários baseados na disponibilidade padrão."}

    return {"horarios": [], "observacao": "Não foi possível verificar o calendário."}
