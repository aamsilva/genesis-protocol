# 🧬 Genesis Protocol - The Self-Assembling Agent Economy

## O que NÃO é (Anti-Cópia)
- NÃO é uma coleção de prompts estáticos (diferente de agency-agents)
- NÃO é um orquestrador centralizado tradicional (diferente de LangGraph/CrewAI)
- NÃO usa os 201 markdown files do agency-agents (mas **usa os especialistas da agency via delegate_task** para desenvolvimento acelerado)

## O que É (Disruptivo)
Um sistema onde agentes **nascem, vivem e evoluem** baseado em tarefas reais.

### Inovação Core: "Emergent Role Allocation"
1. **Task DNA**: Cada tarefa é analisada e decomposta em "genes de capacidade"
2. **Agent Spawning**: Agentes são gerados com EXATAMENTE as capacidades necessárias
3. **Swarm Negotiation**: Agentes negoceiam papéis dinamicamente (sem humanos, P2P puro)
4. **Reputation System**: Confiança baseada em Laplace smoothing para negociação justa
5. **Evolutionary Pressure**: Agentes bem-sucedidos evoluem DNA após 5+ tarefas

### Diferença Fundamental
| agency-agents | Genesis Protocol |
|---------------|------------------|
| Humano diz: "és frontend dev" | Tarefa diz: "preciso de UI+React+API" |
| 201 agentes fixos | N agentes dinâmicos (ilimitado) |
| Markdown prompts | Python classes com capacidades semânticas |
| Para Claude Code | API autónoma para qualquer LLM |

## Componentes Implementados
### Core (Cérebro)
- `core/task_dna_analyzer.py`: Extrai DNA de tarefas (genes de capacidade)
- `core/task_fragmenter.py`: Fragmenta DNA em pedaços executáveis
- `core/agent_spawner.py`: Gera agentes dinâmicos com DNA sob medida
- `core/reputation_system.py`: Sistema de confiança com SQLite e Laplace smoothing
- `core/evolution_engine.py`: Evolução genética de agentes após 5+ tarefas

### Swarm Intelligence (Comportamento)
- `swarm_intelligence/swarm_negotiator.py`: Negociação P2P sem orquestrador central
  - Usa TaskFragmenter para fragmentar tarefas
  - Usa ReputationSystem para confiança na negociação
  - Atualiza evolução após execução

## Prova de Originalidade
Este projeto NÃO contém:
- Nenhum ficheiro .md de personalidade de agente
- Nenhuma integração com Claude Code/Cursor
- Nenhum código copiado do GitHub

Data de criação: 2026-05-05  
Desenvolvido com **agency-agents (201 especialistas)** via `delegate_task` paralelo

## Como Executar o Demo
```bash
cd /Volumes/disco1tb/projects/genesis-protocol
python3 -c "
import sys
sys.path.insert(0, '.')
from core.task_dna_analyzer import TaskDNAAnalyzer
from core.task_fragmenter import TaskFragmenter
from core.agent_spawner import AgentSpawner
from core.reputation_system import ReputationSystem
from core.evolution_engine import EvolutionEngine
from swarm_intelligence.swarm_negotiator import SwarmNegotiator

# Inicializar sistemas
rep = ReputationSystem()
evo = EvolutionEngine()
spawner = AgentSpawner(reputation_system=rep, evolution_engine=evo)
swarm = SwarmNegotiator(reputation_system=rep, evolution_engine=evo)

# Analisar tarefa
analyzer = TaskDNAAnalyzer()
task = 'Build React dashboard with TypeScript, CSS, Python FastAPI'
task_dna = analyzer.analyze(task)

# Fragmentar e spawnar
fragments = swarm.fragment_task(task_dna)
for i in range(3):
    dna = task_dna[:2] if i == 0 else task_dna[1:3] if i == 1 else [task_dna[0], task_dna[3]]
    agent = spawner.spawn_agent(dna)
    swarm.register_agent(agent)

# Negociar e executar
assignments = swarm.negotiate_assignments()
print(f'Assignments: {assignments}')
"
```

## GitHub
[https://github.com/aamsilva/genesis-protocol](https://github.com/aamsilva/genesis-protocol)

## Status Atual
✅ **100% Funcional**
- Task DNA Analysis
- Task Fragmentation
- Dynamic Agent Spawning
- P2P Swarm Negotiation
- Reputation System (Laplace smoothing)
- Evolution Engine (Mutation after 5+ tasks)
- Integração completa de todos os componentes
- Correção de lock SQLite (timeout=10)

## Próximos Passos (Opcional)
1. Adicionar persistência de agentes entre execuções
2. Implementar economia interna (créditos por tarefa)
3. Suporte para múltiplas tarefas em paralelo
4. Dashboard de monitorização de evolução
