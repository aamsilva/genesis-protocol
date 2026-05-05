"""
Genesis Protocol - Dynamic Agent Spawner
DISRUPTIVO: Gera agentes em runtime baseados no DNA da tarefa.
NÃO é um "prompt template" como agency-agents. Isto é código real.
"""

import sys
import os
import uuid
sys.path.insert(0, "/Volumes/disco1tb/projects/genesis-protocol/core")

from typing import Dict, List, Optional
from dataclasses import dataclass

from task_dna_analyzer import CapabilityGene, TaskDNAAnalyzer
from reputation_system import ReputationSystem


@dataclass
class AgentGenome:
    """O genoma de um agente - define as suas capacidades."""
    agent_id: str
    genes: List[CapabilityGene]
    lifespan_tasks: int  # Quantas tarefas pode executar antes de "morrer"
    reproduction_probability: float  # Chance de se reproduzir após sucesso
    mutation_rate: float  # Taxa de mutação para descendentes


class DynamicAgent:
    """
    Um agente dinâmico cujas capacidades nascem do DNA da tarefa.
    
    INOVACAO: Este agente NÃO tem um papel pré-definido.
    O seu papel EMERGE das capacidades que possui.
    """
    
    def __init__(self, genome: AgentGenome, llm_backend: str = "openrouter"):
        self.genome = genome
        self.llm_backend = llm_backend
        self.tasks_completed = 0
        self.success_rate = 0.0
        self.offspring_count = 0
    
    def get_role(self) -> str:
        """
        O papel do agente EMERGE das suas capacidades, não é pré-definido.
        """
        categories = {}
        for gene in self.genome.genes:
            categories[gene.category] = categories.get(gene.category, 0) + gene.strength
        
        dominant_category = max(categories, key=categories.get)
        return f"Dynamic {dominant_category.title()} Specialist (Emergent)"
    
    def execute_task(self, task: str) -> Dict:
        """
        Executa uma tarefa usando as suas capacidades genéticas.
        """
        # Aqui usaria o LLM com um prompt construído dinamicamente
        # baseado nas capacidades do agente (não um prompt estático!)
        prompt = self._build_dynamic_prompt(task)
        
        # Simulação (na implementação real usaria LLM API)
        result = {
            "agent_id": self.genome.agent_id,
            "role": self.get_role(),
            "task": task,
            "capabilities_used": [g.name for g in self.genome.genes],
            "success": True  # Simulado
        }
        
        self.tasks_completed += 1
        return result
    
    def _build_dynamic_prompt(self, task: str) -> str:
        """
        Constrói um prompt dinâmico baseado no genoma do agente.
        DIFERENTE de agency-agents: não é um prompt estático de markdown.
        """
        capabilities = ", ".join([f"{g.name} (level {g.strength})" for g in self.genome.genes])
        return f"""You are a dynamic agent with these capabilities: {capabilities}.
Your role emerges from these capabilities, not from a pre-defined role.
Task: {task}
Use your specific capabilities to solve this task."""
    
    def should_reproduce(self) -> bool:
        """Determina se o agente deve reproduzir-se (evolução)."""
        import random
        return (
            self.success_rate > 0.8 and 
            random.random() < self.genome.reproduction_probability
        )


class AgentSpawner:
    """
    Spawns new agents based on task DNA.
    
    Isto NÃO existe em nenhum framework atual.
    Integrates with ReputationSystem for trust tracking.
    """
    
    def __init__(self, 
                 reputation_system: Optional[ReputationSystem] = None,
                 evolution_engine: Optional['EvolutionEngine'] = None):
        """
        Initialize the AgentSpawner.
        
        Args:
            reputation_system: Optional ReputationSystem instance for syncing agent trust
            evolution_engine: Optional EvolutionEngine instance for agent evolution
        """
        self.reputation_system = reputation_system
        self.evolution_engine = evolution_engine
    
    def spawn_agent(self, task_dna: List[CapabilityGene], 
                    reputation_system: Optional[ReputationSystem] = None,
                    evolution_engine: Optional['EvolutionEngine'] = None) -> DynamicAgent:
        """
        Gera um novo agente com o DNA exato para a tarefa.
        
        Args:
            task_dna: List of CapabilityGene objects defining the agent's DNA
            reputation_system: Optional ReputationSystem to sync with (overrides instance)
            evolution_engine: Optional EvolutionEngine to register with (overrides instance)
            
        Returns:
            DynamicAgent instance with initialized genome
        """
        genome = AgentGenome(
            agent_id=f"agent_{uuid.uuid4().hex[:8]}",
            genes=task_dna,
            lifespan_tasks=10,  # Pode executar 10 tarefas
            reproduction_probability=0.3,
            mutation_rate=0.1
        )
        
        agent = DynamicAgent(genome)
        
        # Sync with reputation system if available
        # Use provided reputation_system first, then instance reputation_system
        rep_system = reputation_system or self.reputation_system
        if rep_system:
            rep_system.sync_agent_success_rate(genome.agent_id, agent)
        
        # Register with evolution engine if available
        evo_engine = evolution_engine or self.evolution_engine
        if evo_engine:
            evo_engine.register_agent(genome.agent_id, task_dna)
        
        return agent


# DEMO DE PROVA (executar este ficheiro diretamente)
if __name__ == "__main__":
    print("=" * 60)
    print("🧬 GENESIS PROTOCOL - AGENT SPAWNER DEMO")
    print("PROVA: Agentes dinâmicos com integração de reputação")
    print("=" * 60)
    
    # Initialize reputation system
    reputation_system = ReputationSystem()
    
    # Create spawner with reputation system
    spawner = AgentSpawner(reputation_system=reputation_system)
    
    # DNA da tarefa (extraído do task_dna_analyzer)
    sample_dna = [
        CapabilityGene("react", "frontend", 8, ["ui", "components"]),
        CapabilityGene("typescript", "frontend", 7, ["type-safe"]),
        CapabilityGene("css", "frontend", 9, ["responsive", "grid"]),
        CapabilityGene("python", "backend", 6, ["api", "fastapi"]),
    ]
    
    print("\n📋 Spawning 3 agents with different DNA variations...\n")
    
    # Criar 3 agentes com DNA ligeiramente diferente (simulando "mutações")
    agents = []
    for i in range(3):
        # Cada agente recebe uma variação do DNA (mutação natural)
        if i == 0:
            mutated_dna = sample_dna[:2]
        elif i == 1:
            mutated_dna = sample_dna[1:3]
        else:
            mutated_dna = sample_dna[0:1] + sample_dna[3:]
        
        agent = spawner.spawn_agent(mutated_dna)
        agents.append(agent)
        
        print(f"  ✅ {agent.genome.agent_id} spawned")
        print(f"     Role: {agent.get_role()}")
        print(f"     Capabilities: {[g.name for g in agent.genome.genes]}")
        print(f"     Initial success_rate: {agent.success_rate:.2f} (Laplace prior)")
        print()
    
    # Simulate some task executions to build reputation
    print("📊 Simulating task executions to build reputation...\n")
    
    for agent in agents:
        for i in range(5):
            success = (i < 4)  # 4 out of 5 successful
            trust = reputation_system.update_trust(agent.genome.agent_id, success)
            reputation_system.sync_agent_success_rate(agent.genome.agent_id, agent)
        
        print(f"  {agent.genome.agent_id}: trust = {agent.success_rate:.3f}")
    
    print("\n" + "=" * 60)
    print("✅ AGENT SPAWNER COM REPUTATION INTEGRADA:")
    print("  • Agentes gerados com DNA específico")
    print("  • Reputação inicial via Laplace smoothing (0.5)")
    print("  • Sync automático entre AgentSpawner e ReputationSystem")
    print("=" * 60)
