"""
Genesis Protocol - Evolution Engine
Handles mutation of CapabilityGene objects over time, improves agent DNA
based on success rates, and enables self-improvement of the swarm.
"""

import random
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field

# Import CapabilityGene from task_dna_analyzer
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from task_dna_analyzer import CapabilityGene, TaskDNAAnalyzer


@dataclass
class EvolutionStats:
    """Tracks evolution statistics for the swarm."""
    total_mutations: int = 0
    strength_increases: int = 0
    tags_added: int = 0
    category_changes: int = 0
    agents_evolved: int = 0
    evolution_events: List[Dict] = field(default_factory=list)
    
    def record_mutation(self, agent_id: str, mutation_type: str, details: str):
        """Record a mutation event."""
        self.total_mutations += 1
        if mutation_type == "strength_increase":
            self.strength_increases += 1
        elif mutation_type == "tag_added":
            self.tags_added += 1
        elif mutation_type == "category_change":
            self.category_changes += 1
        
        self.evolution_events.append({
            "agent_id": agent_id,
            "type": mutation_type,
            "details": details
        })


class EvolutionEngine:
    """
    Evolution Engine for the Genesis Protocol swarm.
    
    Handles mutation of CapabilityGene objects, improves agent DNA
    based on success rates, and enables self-improvement of the swarm.
    
    Mutation Rules:
    - 10% chance to increase strength by 1 (max 10)
    - 5% chance to add a new tag from related capabilities
    - 2% chance to change category (frontend<->backend) for multi-skilled agents
    """
    
    # Related capabilities mapping for tag generation
    RELATED_CAPABILITIES = {
        'react': ['javascript', 'jsx', 'components', 'hooks', 'spa'],
        'vue': ['javascript', 'components', 'directives', 'spa'],
        'angular': ['typescript', 'components', 'rxjs', 'spa'],
        'css': ['styling', 'responsive', 'flexbox', 'grid'],
        'html': ['markup', 'semantic', 'accessibility'],
        'typescript': ['javascript', 'typing', 'interfaces'],
        'api': ['rest', 'endpoints', 'http', 'crud'],
        'database': ['sql', 'nosql', 'queries', 'schema'],
        'microservices': ['docker', 'kubernetes', 'scalability', 'distributed'],
        'auth': ['jwt', 'oauth', 'security', 'tokens'],
        'rest': ['http', 'endpoints', 'json', 'api'],
        'graphql': ['queries', 'schema', 'resolvers', 'api'],
        'llm': ['prompts', 'tokens', 'completion', 'ai'],
        'prompt-engineering': ['prompts', 'context', 'templates', 'ai'],
        'rag': ['embeddings', 'vector-db', 'retrieval', 'ai'],
        'fine-tuning': ['training', 'datasets', 'models', 'ai'],
        'embeddings': ['vectors', 'similarity', 'semantic', 'ai'],
        'pandas': ['dataframe', 'analysis', 'python', 'data'],
        'sql': ['queries', 'database', 'data'],
        'etl': ['pipeline', 'transform', 'data'],
        'visualization': ['charts', 'plots', 'dashboards', 'data'],
        'statistics': ['analysis', 'probability', 'math', 'data'],
        'docker': ['containers', 'images', 'deployment', 'devops'],
        'kubernetes': ['orchestration', 'containers', 'scaling', 'devops'],
        'ci-cd': ['automation', 'testing', 'deployment', 'devops'],
        'monitoring': ['logs', 'metrics', 'alerts', 'devops'],
        'cloud': ['aws', 'azure', 'gcp', 'devops'],
    }
    
    # Category change mapping (frontend <-> backend for multi-skilled agents)
    CATEGORY_MAPPING = {
        'frontend': 'backend',
        'backend': 'frontend'
    }
    
    def __init__(self, seed: Optional[int] = None):
        """
        Initialize the EvolutionEngine.
        
        Args:
            seed: Random seed for reproducibility
        """
        if seed is not None:
            random.seed(seed)
        self.stats = EvolutionStats()
        self._agent_success_rates: Dict[str, float] = {}
        self._agent_task_counts: Dict[str, int] = {}
        self._agent_dna: Dict[str, List[CapabilityGene]] = {}
    
    def register_agent(self, agent_id: str, dna: List[CapabilityGene]):
        """Register an agent with the evolution engine."""
        self._agent_dna[agent_id] = dna.copy()
        self._agent_task_counts[agent_id] = 0
        self._agent_success_rates[agent_id] = 0.0
    
    def record_task_completion(self, agent_id: str, success: bool):
        """
        Record a task completion for an agent.
        Triggers evolution check when agent completes 5+ tasks.
        """
        if agent_id not in self._agent_task_counts:
            return
        
        self._agent_task_counts[agent_id] += 1
        
        # Update success rate (exponential moving average)
        alpha = 0.3
        if success:
            self._agent_success_rates[agent_id] = (
                alpha * 1.0 + (1 - alpha) * self._agent_success_rates[agent_id]
            )
        else:
            self._agent_success_rates[agent_id] = (
                alpha * 0.0 + (1 - alpha) * self._agent_success_rates[agent_id]
            )
        
        # Check if evolution should trigger (5+ tasks)
        if self._agent_task_counts[agent_id] >= 5:
            self.evolve_agent(agent_id)
    
    def mutate_dna(self, dna: List[CapabilityGene], agent_id: str = "unknown") -> List[CapabilityGene]:
        """
        Mutate agent DNA based on evolution rules.
        
        Mutation Rules:
        - 10% chance to increase strength by 1 (max 10)
        - 5% chance to add a new tag from related capabilities
        - 2% chance to change category (frontend<->backend) for multi-skilled agents
        
        Args:
            dna: List of CapabilityGene objects
            agent_id: Agent identifier for tracking
            
        Returns:
            Mutated list of CapabilityGene objects
        """
        mutated_dna = []
        
        for gene in dna:
            # Create a copy to avoid modifying the original
            new_gene = CapabilityGene(
                name=gene.name,
                category=gene.category,
                strength=gene.strength,
                tags=gene.tags.copy()
            )
            
            # Rule 1: 10% chance to increase strength by 1 (max 10)
            if random.random() < 0.10:
                if new_gene.strength < 10:
                    new_gene.strength += 1
                    self.stats.record_mutation(
                        agent_id,
                        "strength_increase",
                        f"Increased {gene.name} strength from {gene.strength} to {new_gene.strength}"
                    )
            
            # Rule 2: 5% chance to add a new tag from related capabilities
            if random.random() < 0.05:
                new_tag = self._get_related_tag(new_gene.name, new_gene.tags)
                if new_tag:
                    new_gene.tags.append(new_tag)
                    self.stats.record_mutation(
                        agent_id,
                        "tag_added",
                        f"Added tag '{new_tag}' to {gene.name}"
                    )
            
            # Rule 3: 2% chance to change category (frontend<->backend) for multi-skilled agents
            if random.random() < 0.02:
                if self._is_multi_skilled(dna):
                    if new_gene.category in self.CATEGORY_MAPPING:
                        old_category = new_gene.category
                        new_gene.category = self.CATEGORY_MAPPING[old_category]
                        self.stats.record_mutation(
                            agent_id,
                            "category_change",
                            f"Changed {gene.name} category from {old_category} to {new_gene.category}"
                        )
            
            mutated_dna.append(new_gene)
        
        return mutated_dna
    
    def evolve_agent(self, agent_id: str) -> Optional[List[CapabilityGene]]:
        """
        Evolve an agent based on its success rate and task history.
        
        Args:
            agent_id: The agent to evolve
            
        Returns:
            New mutated DNA if evolution occurred, None otherwise
        """
        if agent_id not in self._agent_dna:
            return None
        
        # Get current DNA
        current_dna = self._agent_dna[agent_id]
        
        # Determine mutation probability based on success rate
        success_rate = self._agent_success_rates.get(agent_id, 0.0)
        
        # Higher success rate = higher chance of beneficial mutation
        # Lower success rate = higher chance of larger mutations
        mutation_boost = 1.0
        if success_rate < 0.3:
            mutation_boost = 2.0  # More mutation for struggling agents
        elif success_rate > 0.8:
            mutation_boost = 0.5  # Less mutation for successful agents
        
        # Apply mutations
        new_dna = self.mutate_dna(current_dna, agent_id)
        
        # Update stored DNA
        self._agent_dna[agent_id] = new_dna
        self.stats.agents_evolved += 1
        
        return new_dna
    
    def get_evolution_stats(self) -> Dict:
        """
        Get evolution statistics for the swarm.
        
        Returns:
            Dictionary containing evolution statistics
        """
        return {
            "total_mutations": self.stats.total_mutations,
            "strength_increases": self.stats.strength_increases,
            "tags_added": self.stats.tags_added,
            "category_changes": self.stats.category_changes,
            "agents_evolved": self.stats.agents_evolved,
            "recent_events": self.stats.evolution_events[-10:] if self.stats.evolution_events else [],
            "agent_success_rates": dict(self._agent_success_rates),
            "agent_task_counts": dict(self._agent_task_counts)
        }
    
    def _get_related_tag(self, capability_name: str, existing_tags: List[str]) -> Optional[str]:
        """
        Get a related tag that is not already in the existing tags.
        
        Args:
            capability_name: The capability to find related tags for
            existing_tags: Tags already associated with the gene
            
        Returns:
            A new related tag, or None if no suitable tag found
        """
        if capability_name not in self.RELATED_CAPABILITIES:
            return None
        
        related = self.RELATED_CAPABILITIES[capability_name]
        available = [tag for tag in related if tag not in existing_tags]
        
        if available:
            return random.choice(available)
        return None
    
    def _is_multi_skilled(self, dna: List[CapabilityGene]) -> bool:
        """
        Check if an agent is multi-skilled (has genes from multiple categories).
        
        Args:
            dna: List of CapabilityGene objects
            
        Returns:
            True if agent has genes from multiple categories
        """
        categories = set(gene.category for gene in dna)
        return len(categories) > 1
    
    def get_agent_dna(self, agent_id: str) -> Optional[List[CapabilityGene]]:
        """Get the current DNA of an agent."""
        return self._agent_dna.get(agent_id)
    
    def get_agent_success_rate(self, agent_id: str) -> float:
        """Get the success rate of an agent."""
        return self._agent_success_rates.get(agent_id, 0.0)


# Example usage and testing
if __name__ == "__main__":
    # Create evolution engine with seed for reproducibility
    engine = EvolutionEngine(seed=42)
    
    # Create sample DNA
    sample_dna = [
        CapabilityGene("react", "frontend", 7, ["components", "spa"]),
        CapabilityGene("api", "backend", 6, ["rest", "endpoints"]),
        CapabilityGene("llm", "ai", 8, ["prompts", "ai"]),
    ]
    
    print("🧬 Original DNA:")
    for gene in sample_dna:
        print(f"  - {gene.name} ({gene.category}) | Strength: {gene.strength} | Tags: {gene.tags}")
    
    # Register agent
    engine.register_agent("agent_test_001", sample_dna)
    
    # Simulate task completions
    print("\n📊 Simulating task completions...")
    for i in range(6):
        success = random.random() > 0.3  # 70% success rate
        engine.record_task_completion("agent_test_001", success)
    
    # Get evolved DNA
    evolved_dna = engine.get_agent_dna("agent_test_001")
    print("\n🧬 Evolved DNA:")
    if evolved_dna:
        for gene in evolved_dna:
            print(f"  - {gene.name} ({gene.category}) | Strength: {gene.strength} | Tags: {gene.tags}")
    
    # Get evolution stats
    print("\n📈 Evolution Statistics:")
    stats = engine.get_evolution_stats()
    for key, value in stats.items():
        if key != "recent_events":
            print(f"  {key}: {value}")
    
    if stats["recent_events"]:
        print("\n  Recent Events:")
        for event in stats["recent_events"]:
            print(f"    - {event['agent_id']}: {event['type']} - {event['details']}")
    
    print("\n✅ Evolution Engine test complete!")
