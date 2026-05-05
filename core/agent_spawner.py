"""
Genesis Protocol - Dynamic Agent Spawner
DISRUPTIVO: Gera agentes em runtime baseados no DNA da tarefa.
NÃO é um "prompt template" como agency-agents. Isto é código real.
"""

import sys
import os
sys.path.insert(0, "/Volumes/disco1tb/projects/genesis-protocol/core")

from typing import Dict, List, Optional
from dataclasses import dataclass
from task_dna_analyzer import CapabilityGene, TaskDNAAnalyzer

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
            categories[gene.category] = categories.get(gene.category, 0) + gene.proficiency
        
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
        capabilities = ", ".join([f"{g.name} (level {g.proficiency})" for g in self.genome.genes])
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
    """
    
    def spawn_agent(self, task_dna: List[CapabilityGene]) -> DynamicAgent:
        """
        Gera um novo agente com o DNA exato para a tarefa.
        """
        import uuid
        
        genome = AgentGenome(
            agent_id=f"agent_{uuid.uuid4().hex[:8]}",
            genes=task_dna,
            lifespan_tasks=10,  # Pode executar 10 tarefas
            reproduction_probability=0.3,
            mutation_rate=0.1
        )
        
        return DynamicAgent(genome)
