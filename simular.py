"""KUKA LBR iiwa 14 numa célula de fim de linha (esteira -> palete) no MuJoCo.

Uso:  python simular.py
Abre o visualizador do MuJoCo e executa:
  1) cada junta sozinha, indo do limite mínimo ao máximo;
  2) um movimento coordenado: repouso -> caixa na esteira -> vaga no palete -> repouso.
"""
import time
from pathlib import Path

import mujoco
import mujoco.viewer
import numpy as np

from roteiro import interpola, roteiro

CENA = Path(__file__).parent / "kuka_iiwa_14" / "cena_fim_de_linha.xml"
PASSOS_POR_QUADRO = 8  # passos de física entre cada atualização da tela


def main():
    model = mujoco.MjModel.from_xml_path(str(CENA))
    data = mujoco.MjData(model)

    # Começa na pose "home" definida no modelo do Menagerie
    mujoco.mj_resetDataKeyframe(model, data, model.key("home").id)
    mujoco.mj_forward(model, data)

    # Limites de cada junta, lidos do próprio modelo (radianos -> graus)
    limites = [tuple(np.degrees(model.jnt_range[j])) for j in range(model.njnt)]
    for j, (lo, hi) in enumerate(limites):
        print(f"J{j + 1}: {lo:+7.1f}° a {hi:+7.1f}°")

    with mujoco.viewer.launch_passive(model, data) as viewer:
        q_atual = data.qpos[:7].copy()
        inicio_real = time.time()

        for descricao, q_alvo, duracao in roteiro(limites):
            print(descricao)
            t0 = data.time
            while data.time - t0 < duracao and viewer.is_running():
                for _ in range(PASSOS_POR_QUADRO):
                    s = (data.time - t0) / duracao
                    # Atuadores do iiwa no Menagerie são servos de posição:
                    # ctrl = ângulo desejado de cada junta (rad).
                    data.ctrl[:] = interpola(q_atual, q_alvo, s)
                    # Compensa a gravidade para o robô seguir o alvo sem "cair"
                    data.qfrc_applied[:] = data.qfrc_bias
                    mujoco.mj_step(model, data)
                viewer.sync()
                # Mantém a simulação em tempo real
                atraso = data.time - (time.time() - inicio_real)
                if atraso > 0:
                    time.sleep(atraso)
            q_atual = q_alvo
            if not viewer.is_running():
                return

        print("Fim do roteiro. Feche a janela para sair.")
        while viewer.is_running():
            time.sleep(0.05)


if __name__ == "__main__":
    main()
