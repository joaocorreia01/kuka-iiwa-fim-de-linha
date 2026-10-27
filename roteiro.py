"""Poses e sequência de movimentos do KUKA LBR iiwa 14 (ângulos em graus).

Não depende do MuJoCo: só define ONDE o robô deve ir e em QUANTO tempo.
Quem executa é o simular.py.

Ordem das juntas: [J1, J2, J3, J4, J5, J6, J7] (todas de revolução).
"""
import numpy as np

# --- Poses fixas -------------------------------------------------------------
REPOUSO      = [0, 45, 0, -90, 0, 0, 0]   # keyframe "home" do Menagerie
VERTICAL     = [0, 0, 0, 0, 0, 0, 0]       # braço todo esticado para cima
COTOVELO_90  = [0, 0, 0, -90, 0, 0, 0]     # antebraço na horizontal
PUNHO_90     = [0, 0, 0, -90, 0, 90, 0]    # antebraço horizontal + punho dobrado
TRANSPORTE   = [0, 10, 0, -90, 0, 60, 0]   # garra levantada: evita raspar na esteira ao girar a base

# Poses da tarefa (garra apontando para baixo).
# Encontradas uma única vez com cinemática inversa numérica e arredondadas
# para graus inteiros; o roteiro em si só usa ângulos de junta.
ESTEIRA_ACIMA = [68, 47, 0, -19, 0, 114, 0]   # ~14 cm acima da caixa na esteira
ESTEIRA_PERTO = [68, 41, 0, -37, 0, 102, 0]   # ~8 cm acima da caixa
PALETE_ACIMA  = [-63, 30, 0, -77, 0, 73, 0]   # acima da vaga livre no palete
PALETE_PERTO  = [-63, 42, 0, -86, 0, 52, 0]   # descendo na vaga

# Para cada junta: a pose de partida em que o movimento dela fica bem visível
# e não bate em nada da cena.
POSE_PARA_JUNTA = [COTOVELO_90, VERTICAL, COTOVELO_90, VERTICAL, PUNHO_90, COTOVELO_90, PUNHO_90]


def roteiro(limites_graus, t_mov=2.0):
    """Lista de (descrição, alvo em graus, duração em s).

    limites_graus: lista de (min, max) de cada junta, lida do modelo.
    """
    passos = [("Repouso", REPOUSO, 1.0)]

    # 1) Cada junta sozinha, de um limite ao outro
    for i, (lo, hi) in enumerate(limites_graus):
        base = list(POSE_PARA_JUNTA[i])
        nome = f"J{i + 1}"
        passos.append((f"{nome}: posição inicial", base, t_mov))
        for alvo, rotulo in ((lo, "limite mínimo"), (hi, "limite máximo"), (base[i], "volta")):
            q = list(base)
            q[i] = alvo
            dur = 2 * t_mov if rotulo == "limite máximo" else t_mov  # min -> max é o dobro do curso
            passos.append((f"{nome}: {rotulo} ({alvo:+.0f}°)", q, dur))

    # 2) Movimento coordenado: esteira -> palete
    passos += [
        ("Coordenado: repouso", REPOUSO, t_mov),
        ("Coordenado: levanta a garra", TRANSPORTE, t_mov),
        ("Coordenado: acima da caixa na esteira", ESTEIRA_ACIMA, 1.5 * t_mov),
        ("Coordenado: perto da caixa", ESTEIRA_PERTO, t_mov),
        ("Coordenado: pausa (pegaria a caixa)", ESTEIRA_PERTO, 0.5 * t_mov),
        ("Coordenado: sobe", ESTEIRA_ACIMA, t_mov),
        ("Coordenado: gira até o palete", PALETE_ACIMA, 2 * t_mov),
        ("Coordenado: desce na vaga livre", PALETE_PERTO, t_mov),
        ("Coordenado: pausa (soltaria a caixa)", PALETE_PERTO, 0.5 * t_mov),
        ("Coordenado: sobe", PALETE_ACIMA, t_mov),
        ("Coordenado: volta ao repouso", REPOUSO, 1.5 * t_mov),
    ]
    return [(d, np.radians(q), t) for d, q, t in passos]


def interpola(q0, q1, s):
    """Vai de q0 a q1 com perfil suave (começa e termina com velocidade zero). s em [0, 1]."""
    s = min(max(s, 0.0), 1.0)
    a = 0.5 - 0.5 * np.cos(np.pi * s)
    return q0 + a * (q1 - q0)
