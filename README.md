# KUKA LBR iiwa 14: célula de fim de linha (MuJoCo)

Robô KUKA LBR iiwa 14 (7 graus de liberdade, todas as juntas de revolução) entre uma esteira transportadora e um palete. O script move cada junta de um limite ao outro e depois faz um movimento coordenado: repouso → caixa na esteira → vaga livre no palete → repouso.

- **Simulador:** MuJoCo `3.17.0` (`python -c "import mujoco; print(mujoco.__version__)"`)
- **Modelo do robô:** `kuka_iiwa_14` do [MuJoCo Menagerie](https://github.com/google-deepmind/mujoco_menagerie) (licença BSD-3, ver `kuka_iiwa_14/LICENSE`)

## Estrutura

```
simular.py                      # abre o visualizador e executa o roteiro
roteiro.py                      # poses (em graus) e sequência de movimentos
kuka_iiwa_14/
  iiwa14.xml, assets/           # modelo do robô (Menagerie, sem alterações)
  cena_fim_de_linha.xml         # cena: pedestal, esteira, caixas, palete
```

A cena fica dentro de `kuka_iiwa_14/` porque o `iiwa14.xml` procura as malhas em `assets/` relativo ao arquivo principal.

## Como instalar e rodar

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install mujoco numpy
python simular.py
```

No macOS, use `mjpython simular.py` (o visualizador passivo exige isso).

Para só olhar a cena e mexer nos sliders: `python -m mujoco.viewer --mjcf kuka_iiwa_14/cena_fim_de_linha.xml`

## Como o controle funciona

Os atuadores do iiwa no Menagerie são servos de posição: `data.ctrl[i]` é o ângulo desejado da junta *i* em radianos. O `roteiro.py` define os alvos e o `simular.py` interpola entre eles com perfil suave (cosseno). Também aplica compensação de gravidade (`qfrc_applied = qfrc_bias`) para o robô seguir o alvo sem "cair". Não há cinemática inversa no roteiro, só ângulos de junta.

## Limites das juntas (do modelo)

| Junta | Faixa |
|---|---|
| J1, J3, J5 | ±170° |
| J2, J4, J6 | ±120° |
| J7 | ±175° |

## Uso de IA

*(preencher: ferramentas usadas e para quê, um exemplo em que ajudou, um exemplo em que errou e como você percebeu)*
