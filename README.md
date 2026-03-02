# Wowlinette

Bot automatizado para correção de listas de exercícios em linguagem C, com execução isolada via Docker e validação estruturada por bateria de testes.

## Visão Geral

Wowlinette é um sistema de avaliação automatizada que compila, executa e valida implementações em C submetidas por usuários.

O projeto foi projetado com foco em:

- Execução segura de código arbitrário
- Isolamento de ambiente via container
- Reprodutibilidade
- Testes orientados a falhas comuns
- Arquitetura modular e extensível

# Arquitetura do Sistema

A aplicação segue uma arquitetura separada em camadas:

Frontend → API Backend → Engine de Compilação → Ambiente Isolado (Docker)

## Componentes Principais

### 1. Frontend
Responsável por:
- Upload dos arquivos
- Seleção da lista de exercícios
- Exibição dos resultados
- Comunicação com o backend via HTTP

### 2. Backend
Responsável por:
- Orquestrar compilação
- Injetar código de teste
- Executar binários
- Comparar saídas
- Retornar status estruturado

### 3. Engine de Testes
Cada exercício possui:
- Arquivo de bateria de testes
- Casos múltiplos (mínimo 5 quando aplicável)
- Edge cases
- Validação de saída exata

### 4. Ambiente Isolado
Todo código submetido é executado dentro de container Docker, garantindo:
- Isolamento de sistema
- Controle de dependências
- Ambiente reprodutível
- Mitigação de riscos ao executar código externo

# Fluxo de Execução Interno

1. Recebimento dos arquivos `.c`
2. Seleção da bateria correspondente
3. Geração dinâmica de um `main` de teste
4. Compilação com GCC
5. Execução controlada em pasta temporária
6. Captura de stdout/stderr
7. Comparação com output esperado
8. Retorno do resultado
9. Limpeza de cache na pasta temp

---

## Injeção Dinâmica de Código

Para cada teste, o sistema cria um arquivo temporário contendo:

- Include do exercício submetido
- Função main específica para aquele cenário
- Parâmetros simulados quando necessário

Isso permite validar funções individualmente, sem depender da implementação de um main pelo usuário.

# Segurança e Isolamento

Executar código arbitrário exige controle rigoroso.

Medidas implementadas:

- Execução dentro de container Docker
- Ambiente mínimo com dependências controladas
- Sem acesso direto ao host
- Timeout de execução
- Captura de erros e falhas de segmentação
- Limitação implícita de recursos via container

Essa abordagem reduz riscos como:
- Execução maliciosa
- Loops infinitos
- Acesso indevido ao sistema

# Estratégia de Testes

Os testes são estruturados para identificar falhas comuns cometidas por iniciantes em C.

Cada exercício pode conter múltiplos cenários de validação:

- Casos básicos
- Casos limite
- Zero
- Valores negativos
- Arrays de tamanho 1
- Arrays já ordenados
- Arrays invertidos
- Off-by-one
- Erros de lógica em loops
- Manipulação incorreta de ponteiros

O objetivo não é apenas validar o caso feliz, mas expor implementações incompletas.

# Tecnologias Utilizadas

## Backend

- Python 3
- subprocess (execução de comandos do sistema)
- GCC (compilador C)

## Containerização

- Docker
- Docker Compose

## Frontend

- React / Next.js
- CSS customizado (tema dark + neon)

## Justificativas Técnicas

Python foi escolhido pela facilidade de orquestrar:
- Execução de processos
- Manipulação de arquivos temporários
- Estrutura modular de testes

Docker foi adotado para:
- Garantir isolamento
- Padronizar ambiente
- Facilitar deploy
- Evitar inconsistências entre máquinas

---

# Como Executar Localmente

## Pré-requisitos

- Docker
- Docker Compose (opcional)

---

## Build da imagem

docker build -t wowlinette .

---

## Executar container

docker run -p 8000:8000 wowlinette

Aplicação disponível em:
http://localhost:8000

---

## Alternativa com Docker Compose

docker-compose up --build
