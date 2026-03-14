
---

## 🎮 Sobre o Jogo

**Harvest Farm Constructor** é um jogo de simulação e gerenciamento de fazenda no estilo top-down inspirado em títulos como *Stardew Valley* e *Constructor*. O jogador controla um fazendeiro, cultiva 8 tipos de plantações, gerencia sua economia, enfrenta climas variados e expande sua propriedade ao longo de 4 estações do ano.

---

## ✨ Funcionalidades

### 🗺️ Mundo e Mapa
- Mapa grande **60×40 tiles** gerado proceduralmente com múltiplos biomas
- **Grama, terra fértil, caminhos de pedra, lago animado, pomar e construções**
- Arte vetorial 100% desenhada em código (sem depender de assets externos)
- Câmera suave com **lerp** que segue o jogador pelo mapa expansível
- Sistema de **Y-sorting** e sombras nos objetos

### 🌤️ Sistema de Clima e Estações
- **4 estações** do ano: Primavera, Verão, Outono e Inverno (7 dias cada)
- **5 climas** dinâmicos com pesos por estação: Ensolarado, Nublado, Chuvoso, Tempestade e Nevando
- **Chuva animada** com efeito de neblina azulada
- **Neve animada** com flocos voando pela tela
- **Nuvens flutuando** com transparência variável por clima
- 🌧️ **Chuva e Tempestade regam suas plantas automaticamente!**
- Ciclo **dia/noite completo** com gradiente de céu e estrelas à noite

### 🌱 Plantações e Agricultura
- **8 tipos de plantas**, cada uma com arte única em 3 estágios de crescimento:
  | Planta | Preço | Recompensa | Tempo |
  |--------|-------|------------|-------|
  | 🌾 Trigo | $10 | $8 | Rápido |
  | 🌽 Milho | $18 | $15 | Médio |
  | 🍅 Tomate | $28 | $25 | Médio |
  | 🥔 Batata | $8 | $6 | Muito rápido |
  | 🥕 Cenoura | $14 | $12 | Rápido |
  | 🍓 Morango | $50 | $40 | Lento |
  | 🎃 Abóbora | $65 | $55 | Muito lento |
  | 🍇 Uva | $90 | $80 | Extremamente lento |
- Plantas crescem apenas em **terra molhada** (3 estágios visuais animados)
- Terra seca ao longo do tempo — regue regularmente!
- Animação de balanço nas plantas conforme o vento (baseada em seno)

### 🖱️ Controles e Interação
- **WASD / Setas** — Mover o personagem
- **Clique Esquerdo** — Plantar, Colher ou agir no tile sob o cursor
- **Clique Direito** — Regar a terra
- **1–9** — Selecionar item no hotbar
- **TAB** — Mudar aba no painel lateral
- **F5** — Salvar manualmente
- **ESC** — Salvar e voltar ao menu
- **F1** — Abrir painel de ajuda
- **Cursor inteligente**: muda de cor (verde/vermelho) indicando se o tile está ao alcance
- **Tooltips contextuais** descrevem o que acontece ao clicar em cada tile

### 💰 Economia e Progressão
- Sistema de **Ouro** ganho com colheitas
- **Nível e XP**: cada colheita concede XP e sobe de nível com aviso animado
- **Sistema de Conquistas** com notificações flutuantes
- Loja com compra de sementes por clique direto no painel lateral
- **Upgrades permanentes** no painel "Obras":
  - 🏗️ Expandir Terreno — aumenta o mapa
  - 🌿 Adubo Premium — reduz o tempo de crescimento em 25%
  - 💧 Regador de Ouro — solo retém umidade mais tempo
  - 🏚️ Silo de Armazenamento

### 🤖 NPCs com IA de Patrulha
- **Carlos** (comerciante) e **Ana** (trabalhadora) caminham pelo mapa
- Rotas de patrulha configuráveis com idle aleatório
- Nome flutuando acima de cada NPC

### 🎨 Visual e Interface
- **Arte vetorial procedural** para todos os tiles, cenários e personagens
- **Menu inicial animado**: céu gradiente, colinas ondulando, moinho de vento, pirilampos pulsantes, nuvens flutuantes e título com estrelas giratórias
- **Top Bar elegante**: ouro, nível, barra de XP, hora, estação, clima
- **Sidebar lateral** com 3 abas: 🎒 Bag, 🛒 Loja, ⚗ Obras
- **Hotbar animada** com glow no slot ativo
- **Partículas físicas** em colheitas, plantio, rega e sono
- **Textos flutuantes** aparecem em todas as ações importantes
- **Overlay de noite** com estrelas e fade gradual
- **Efeito de sono** com fade para preto ao dormir na casa

### 💾 Sistema de Save/Load
| Gatilho | Descrição |
|---------|-----------|
| **ESC** | Salva e retorna ao menu principal |
| **F5** | Salva manualmente durante o jogo |
| **Dormir** na casa | Salva automaticamente ao acordar |
| **Auto-save** | Salva a cada 3 minutos automaticamente |
| **"Continuar"** no menu | Restaura exatamente de onde parou |

O arquivo de save fica em `saves/savegame.json` e preserva: plantas, sementes, moedas, XP, nível, clima, hora e estação.

---

## 🏗️ Arquitetura do Código

```
devops---jogo/
├── src/
│   ├── main.py         # Entry point: fullscreen, menu, loop principal, save/load
│   ├── engine.py       # Motor do jogo: World, Player, Camera, UIManager, Weather, NPCs, Arte
│   ├── menu.py         # Menu inicial animado com botões interativos
│   └── savesystem.py   # Serialização/desserialização do estado em JSON
├── assets/             # Sprites opcionais (o jogo funciona sem eles)
├── saves/              # Arquivos de save (gerado automaticamente)
├── tests/              # Testes automatizados com Pytest
└── requirements.txt
```

---

## 🚀 Como Executar


### Instalação

```bash
# 1. Clone o repositório
git clone <url-do-repositorio>
cd devops---jogo

# 2. Crie e ative o ambiente virtual
python -m venv .venv

# Windows
.venv\Scripts\Activate.ps1

# Linux / macOS
source .venv/bin/activate

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Execute o jogo
python -m src.main
```

### Executar testes

```bash
pytest tests/
```

### Lint (Ruff)

```bash
ruff check src/
```

---

## 🛠️ Tecnologias Utilizadas

| Tecnologia | Uso |
|------------|-----|
| **Python 3.10+** | Linguagem principal |
| **Pygame 2.6** | Motor de renderização, eventos e som |
| **JSON** | Serialização do sistema de save |
| **Pytest** | Testes automatizados |
| **Ruff** | Lint e qualidade de código |
| **Git / GitHub** | Versionamento e CI/CD |

---

## 👥 Equipe

**Grupo DevOps:**
- Akaz Luís
- Maria Clara
- Mateus Azevedo