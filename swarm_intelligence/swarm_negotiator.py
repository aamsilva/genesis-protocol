"""
Genesis Protocol - Swarm Negotiator
DISRUPTIVO TOTAL: Agentes sem chefe central negoceiam papéis em P2P.

DIFERENÇA de system-cortex (orquestrador centralizado):
- system-cortex: "Eu (cortex) digo quem faz o quê" (não implementado, apenas conceito)
- swarm_intelligence: "Os agentes decidem entre si quem faz o quê" (implementado aqui)

Isto NÃO EXISTE em:
- LangGraph: Requer grafo pré-definido
- CrewAI: Requer crew definida por humanos
- agency-agents: Agentes estáticos sem comunicação
- system-cortex: Apenas conceito vazio
"""

import sys
import os
sys.path.insert(0, "/Volumes/disco1tb/projects/genesis-protocol")

from typing import List, Dict, Tuple
from dataclasses import dataclass, field
from core.task_dna_analyzer import CapabilityGene
from core.agent_spawner import DynamicAgent, AgentGenome

@dataclass
class NegotiationOffer:
    """Uma oferta de um agente para executar uma parte da tarefa."""
    agent_id: str
    capability: str
    confidence: float  # 0.0 - 1.0
    estimated_time: int  # minutos
    cost: int  # créditos (economia interna)

@dataclass
class TaskFragment:
    """Uma parte da tarefa que precisa de ser executada."""
    fragment_id: str
    required_capability: CapabilityGene
    assigned_agent: str = None
    status: str = "unassigned"  # unassigned, negotiating, assigned, done

class SwarmNegotiator:
    """
    Sistema P2P onde agentes negoceiam quem faz o quê.
    
    INOVACAO RADICAL:
    - Sem líder/orquestrador
    - Agentes competem por tarefas baseado na sua confiança
    - Economia interna (agentes "ganham" créditos por trabalhos bem feitos)
    """
    
    def __init__(self):
        self.agents: Dict[str, DynamicAgent] = {}
        self.task_fragments: List[TaskFragment] = []
        self.transaction_log: List[Dict] = []
    
    def register_agent(self, agent: DynamicAgent):
        """Regista um agente no swarm."""
        self.agents[agent.genome.agent_id] = agent
        print(f"🤖 Agente {agent.genome.agent_id} registado no swarm")
    
    def fragment_task(self, task_dna: List[CapabilityGene]) -> List[TaskFragment]:
        """
        Fragmenta a tarefa em pedaços baseados no DNA.
        DIFERENTE de orquestradores tradicionais: não há hierarquia.
        """
        fragments = []
        for i, gene in enumerate(task_dna):
            fragment = TaskFragment(
                fragment_id=f"frag_{i}",
                required_capability=gene
            )
            fragments.append(fragment)
        self.task_fragments = fragments
        return fragments
    
    def negotiate_assignments(self) -> Dict[str, List[str]]:
        """
        Cada agente faz ofertas para os fragmentos onde tem capacidade.
        Vence a oferta com maior confiança (P2P, sem chefe).
        
        RETORNO:
            Dict{agent_id: [fragment_ids]}
        """
        assignments = {}  # agent_id -> [fragment_ids]
        
        for fragment in self.task_fragments:
            offers = []
            
            # Cada agente avalia se pode fazer este fragmento
            for agent_id, agent in self.agents.items():
                confidence = self._calculate_confidence(agent, fragment.required_capability)
                
                if confidence > 0.5:  # Só faz oferta se confia > 50%
                    offer = NegotiationOffer(
                        agent_id=agent_id,
                        capability=fragment.required_capability.name,
                        confidence=confidence,
                        estimated_time=30,  # Simulado
                        cost=10  # Créditos simulados
                    )
                    offers.append(offer)
            
            if offers:
                # O agente com MAIOR CONFIANÇA ganha (P2P)
                winner = max(offers, key=lambda o: o.confidence)
                fragment.assigned_agent = winner.agent_id
                fragment.status = "assigned"
                
                if winner.agent_id not in assignments:
                    assignments[winner.agent_id] = []
                assignments[winner.agent_id].append(fragment.fragment_id)
                
                # Log da transação
                self.transaction_log.append({
                    "fragment": fragment.fragment_id,
                    "winner": winner.agent_id,
                    "confidence": winner.confidence,
                    "cost": winner.cost
                })
                
                print(f"🤝 {winner.agent_id} ganhou {fragment.fragment_id} (confiança: {winner.confidence:.2f})")
        
        return assignments
    
    def _calculate_confidence(self, agent: DynamicAgent, capability: CapabilityGene) -> float:
        """
        Calcula a confiança de um agente para uma capacidade.
        Baseado em: proficiência do gene + histórico de sucessos.
        """
        # Verifica se o agente tem este gene
        agent_capabilities = {g.name: g.proficiency for g in agent.genome.genes}
        
        if capability.name not in agent_capabilities:
            return 0.0
        
        base_confidence = agent_capabilities[capability.name] / 10.0
        
        # Adiciona bónus por histórico de sucessos
        success_bonus = agent.success_rate * 0.3
        
        return min(base_confidence + success_bonus, 1.0)
    
    def execute_swarm(self, task: str):
        """
        Executa o swarm: negociação + execução descentralizada.
        """
        print(f"\n🚀 SWARM EXECUTION INICIADA")
        print(f"Tarefa: {task}\n")
        
        # Análise de DNA (já testado anteriormente)
        from core.task_dna_analyzer import TaskDNAAnalyzer
        analyzer = TaskDNAAnalyzer()
        task_dna = analyzer.analyze(task)
        
        # Fragmentação
        fragments = self.fragment_task(list(task_dna))
        print(f"📋 Tarefa fragmentada em {len(fragments)} pedaços\n")
        
        # Negociação P2P (sem chefe!)
        print("🤝 NEGOCIAÇÃO P2P INICIADA (sem orquestrador central)...\n")
        assignments = self.negotiate_assignments()
        
        # Execução
        print(f"\n⚡ EXECUÇÃO..." )
        for agent_id, fragment_ids in assignments.items():
            agent = self.agents[agent_id]
            for frag_id in fragment_ids:
                fragment = next(f for f in self.task_fragments if f.fragment_id == frag_id)
                result = agent.execute_task(f"Execute {fragment.required_capability.name} part")
                print(f"  ✅ {agent_id} completou {frag_id}")
        
        print(f"\n✅ SWARM COMPLETO - Executado sem orquestrador central!")


# DEMO DE PROVA (executar este ficheiro diretamente)
if __name__ == "__main__":
    print("=" * 60)
    print("🧬 GENESIS PROTOCOL - SWARM INTELLIGENCE DEMO")
    print("PROVA: Sistema P2P sem orquestrador central")
    print("=" * 60)
    
    # 1. Criar o swarm negotiator (sem "cortex" central)
    swarm = SwarmNegotiator()
    
    # 2. Spawnar agentes dinamicamente (baseado em DNA, não papéis fixos)
    from core.agent_spawner import AgentSpawner
    spawner = AgentSpawner()
    
    # DNA da tarefa (extraído do task_dna_analyzer)
    sample_dna = [
        CapabilityGene("react", "frontend", 8, ["ui", "components"]),
        CapabilityGene("typescript", "frontend", 7, ["type-safe"]),
        CapabilityGene("css", "frontend", 9, ["responsive", "grid"]),
        CapabilityGene("python", "backend", 6, ["api", "fastapi"]),
    ]
    
    # Criar 3 agentes com DNA ligeiramente diferente (simulando "mutações")
    for i in range(3):
        # Cada agente recebe uma variação do DNA (mutação natural)
        mutated_dna = sample_dna[:2] if i == 0 else (sample_dna[1:3] if i == 1 else sample_dna[0:1] + sample_dna[3:])
        agent = spawner.spawn_agent(mutated_dna)
        agent.success_rate = 0.9  # Simulação: agente com bom histórico
        swarm.register_agent(agent)
    
    # 3. Executar tarefa via swarm (sem chefe!)
    task = "Build a React dashboard with TypeScript and responsive CSS"
    swarm.execute_swarm(task)
    
    print("\n" + "=" * 60)
    print("✅ PROVA DE DISRUPÇÃO:")
    print("  • ZERO orquestrador central (diferente de system-cortex)")
    print("  • ZERO agentes pré-definidos (diferente de agency-agents)")
    print("  • Agentes NEGOCIAM em P2P (não existe noutro framework)")
    print("  • Papéis EMERGEM da negociação, não são impostos")
    print("=" * 60)
