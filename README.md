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

**Ferramentas:** usei o Claude (Anthropic) durante todo o trabalho: para escolher o
robô e o cenário, gerar a cena em MJCF e os scripts Python, calcular as poses da
tarefa e explicar o código. Não usei servidores MCP
para controlar o simulador; todo o controle é feito pelo script.

**Onde ajudou de verdade:** nas poses do movimento coordenado. Encontrar à mão os 7
ângulos que levam a flange até a caixa na esteira, com a garra apontando para baixo,
seria tentativa e erro. A IA resolveu isso uma única vez com cinemática inversa
numérica e arredondou os valores para graus inteiros, então o roteiro só usa ângulos
de junta. Também ajudou a entender o modelo do Menagerie, principalmente que o
`ctrl` dos atuadores não é torque, e sim o ângulo desejado de um controlador PD
(Kp = 2000, Kd = 200).

**Onde errou ou atrapalhou:**
- Na primeira versão do movimento coordenado, o braço ia direto do repouso até a
  esteira e passava raspando na lateral dela. Isso apareceu numa checagem de
  distância entre o braço e os objetos da cena e foi corrigido com uma pose
  intermediária com a garra levantada (`TRANSPORTE`). A lição foi não confiar que
  uma trajetória gerada está livre de colisão sem verificar.
- A IA não conseguiu instalar o MuJoCo no ambiente dela e entregou o código sem
  ter rodado no simulador real (as prévias em GIF que ela mostrou eram desenhos
  esquemáticos, não renders do MuJoCo). Só considerei o código válido depois de
  rodar na minha máquina e ver o roteiro completo chegar ao fim sem o robô travar
  em nenhum objeto.
