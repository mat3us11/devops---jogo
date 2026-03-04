# Arcade 2D Game – Projeto DevOps

## Descrição

Este projeto consiste no desenvolvimento de um jogo arcade 2D simples utilizando **Python e Pygame**, seguindo práticas de **DevOps**, como controle de versão com Git, desenvolvimento incremental e integração contínua.

O objetivo do projeto é demonstrar a evolução do jogo através de entregas progressivas, adicionando novas funcionalidades a cada versão.

## Funcionalidades atuais

* Movimentação do jogador com teclado (setas)
* Sistema básico de colisão
* Coleta de moedas
* Sistema de pontuação

## Tecnologias utilizadas

* Python
* Pygame
* Git / GitHub
* Pytest (para testes automatizados)
* Ruff (lint de código)

## Estrutura do projeto

```
devops---jogo
│
├── src
│   ├── main.py        # Arquivo principal do jogo
│   ├── game.py        # Lógica principal do jogo
│   ├── entities.py    # Entidades do jogo (player, inimigos, etc)
│   └── settings.py    # Configurações do jogo
│
├── tests              # Testes automatizados
│
└── .github/workflows  # Integração contínua (CI)
```

## Como executar o projeto

1. Clone o repositório

```
git clone <url-do-repositorio>
```

2. Crie um ambiente virtual

```
python -m venv .venv
```

3. Ative o ambiente virtual

Windows:

```
.venv\Scripts\Activate.ps1
```

4. Instale as dependências

```
pip install -r requirements.txt
```

5. Execute o jogo

```
python -m src.main
```

## Desenvolvimento incremental

O projeto será desenvolvido em várias entregas:

**Entrega 1**

* Movimentação do jogador
* Sistema básico de pontuação

**Entrega 2**

* Inimigos
* Sistema de vidas

**Entrega 3**

* Game Over
* Melhorias no gameplay

**Entrega 4**

* Testes automatizados
* Integração contínua (CI)

## Grupo:

Akaz Luís, Maria Clara e Mateus Azevedo
