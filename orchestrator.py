#!/usr/bin/env python3
"""Sistema multi-agente de vendas para mentoria individual de IA - Elvizio Vanzo."""
import argparse
import sys
import time

from agents import qualificar_lead, gerar_resposta_dm, propor_horarios, gerar_briefing

# ANSI colors
RESET = "\033[0m"
BOLD = "\033[1m"
CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
MAGENTA = "\033[35m"
BLUE = "\033[34m"
DIM = "\033[2m"

COR_QUENTE = RED
COR_MORNO = YELLOW
COR_FRIO = BLUE


def _titulo_secao(numero: int, titulo: str, cor: str = CYAN) -> None:
    print(f"\n{cor}{BOLD}{'═' * 60}{RESET}")
    print(f"{cor}{BOLD}  {numero}. {titulo.upper()}{RESET}")
    print(f"{cor}{BOLD}{'═' * 60}{RESET}\n")


def _spinner(texto: str, duracao: float = 0.8) -> None:
    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    end_time = time.time() + duracao
    i = 0
    while time.time() < end_time:
        print(f"\r{DIM}{frames[i % len(frames)]} {texto}...{RESET}", end="", flush=True)
        time.sleep(0.1)
        i += 1
    print(f"\r{' ' * (len(texto) + 10)}\r", end="", flush=True)


def _exibir_classificacao(resultado: dict) -> None:
    temp = resultado.get("classificacao", "MORNO")
    cor = COR_QUENTE if temp == "QUENTE" else (COR_FRIO if temp == "FRIO" else COR_MORNO)

    print(f"{BOLD}Temperatura:{RESET} {cor}{BOLD}{temp}{RESET}  "
          f"{DIM}(pontuação: {resultado.get('pontuacao', '?')}/100){RESET}")
    print(f"\n{BOLD}Justificativa:{RESET}")
    print(f"  {resultado.get('justificativa', '')}")

    pontos_fortes = resultado.get("pontos_fortes", [])
    if pontos_fortes:
        print(f"\n{GREEN}{BOLD}Pontos Fortes:{RESET}")
        for p in pontos_fortes:
            print(f"  {GREEN}✓{RESET} {p}")

    pontos_atencao = resultado.get("pontos_atencao", [])
    if pontos_atencao:
        print(f"\n{YELLOW}{BOLD}Pontos de Atenção:{RESET}")
        for p in pontos_atencao:
            print(f"  {YELLOW}⚠{RESET} {p}")

    print(f"\n{BOLD}Próximo Passo:{RESET}")
    print(f"  {MAGENTA}→{RESET} {resultado.get('proximo_passo_recomendado', '')}")


def _exibir_dm(dm: str) -> None:
    print(f"{DIM}{'─' * 50}{RESET}")
    for linha in dm.split("\n"):
        print(f"  {linha}")
    print(f"{DIM}{'─' * 50}{RESET}")


def _exibir_horarios(horarios: dict) -> None:
    lista = horarios.get("horarios", [])
    if not lista:
        print(f"  {RED}Nenhum horário disponível.{RESET}")
    else:
        for i, h in enumerate(lista, 1):
            print(f"  {GREEN}{BOLD}{i}.{RESET} {h.get('data', '')} às {BOLD}{h.get('hora', '')}{RESET} — {h.get('duracao', '30 min')}")

    obs = horarios.get("observacao", "")
    if obs:
        print(f"\n  {DIM}Observação: {obs}{RESET}")


def _exibir_briefing(briefing: str) -> None:
    for linha in briefing.split("\n"):
        if linha.startswith("## "):
            print(f"\n{MAGENTA}{BOLD}{linha}{RESET}")
        elif linha.startswith("# "):
            print(f"\n{CYAN}{BOLD}{linha}{RESET}")
        elif linha.startswith("**") and linha.endswith("**"):
            print(f"{BOLD}{linha[2:-2]}{RESET}")
        elif linha.startswith("- "):
            print(f"  {YELLOW}•{RESET} {linha[2:]}")
        else:
            print(linha)


def executar(nome: str, mensagem: str) -> None:
    print(f"\n{CYAN}{BOLD}{'═' * 60}{RESET}")
    print(f"{CYAN}{BOLD}  SISTEMA MULTI-AGENTE DE VENDAS — ELVIZIO VANZO{RESET}")
    print(f"{CYAN}{BOLD}{'═' * 60}{RESET}")
    print(f"\n{DIM}Lead: {nome}{RESET}")
    print(f"{DIM}{'─' * 40}{RESET}")

    _titulo_secao(1, "Qualificação do Lead", GREEN)
    _spinner("Analisando perfil do lead", 1.2)
    classificacao = qualificar_lead(nome, mensagem)
    _exibir_classificacao(classificacao)

    _titulo_secao(2, "Resposta Instagram DM", BLUE)
    _spinner("Gerando mensagem personalizada", 1.0)
    dm = gerar_resposta_dm(nome, mensagem, classificacao)
    _exibir_dm(dm)

    _titulo_secao(3, "Proposta de Horários", YELLOW)
    _spinner("Verificando disponibilidade no calendário", 1.5)
    horarios = propor_horarios(nome, classificacao)
    _exibir_horarios(horarios)

    _titulo_secao(4, "Briefing Executivo para Elvizio", MAGENTA)
    _spinner("Compilando briefing estratégico", 1.2)
    briefing = gerar_briefing(nome, mensagem, classificacao, dm, horarios)
    _exibir_briefing(briefing)

    print(f"\n{GREEN}{BOLD}{'═' * 60}{RESET}")
    print(f"{GREEN}{BOLD}  ✓ PIPELINE CONCLUÍDO COM SUCESSO{RESET}")
    print(f"{GREEN}{BOLD}{'═' * 60}{RESET}\n")


def _coletar_input_interativo() -> tuple[str, str]:
    print(f"\n{CYAN}{BOLD}Sistema Multi-Agente de Vendas — Elvizio Vanzo{RESET}\n")
    nome = input(f"{BOLD}Nome do lead:{RESET} ").strip()
    if not nome:
        print(f"{RED}Nome é obrigatório.{RESET}")
        sys.exit(1)

    print(f"{BOLD}Mensagem do lead{RESET} {DIM}(pressione Enter duas vezes para finalizar):{RESET}")
    linhas = []
    while True:
        linha = input()
        if linha == "" and linhas and linhas[-1] == "":
            break
        linhas.append(linha)

    mensagem = "\n".join(linhas).strip()
    if not mensagem:
        print(f"{RED}Mensagem é obrigatória.{RESET}")
        sys.exit(1)

    return nome, mensagem


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Sistema multi-agente de vendas para mentoria de IA — Elvizio Vanzo"
    )
    parser.add_argument("--nome", type=str, help="Nome do lead")
    parser.add_argument("--mensagem", type=str, help="Mensagem recebida do lead")
    args = parser.parse_args()

    if args.nome and args.mensagem:
        executar(args.nome, args.mensagem)
    else:
        nome, mensagem = _coletar_input_interativo()
        executar(nome, mensagem)
