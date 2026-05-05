"""
Genesis Protocol - Task DNA Analyzer
DISRUPTIVO: Analisa tarefas e extrai "genes de capacidade" necessários.
NÃO EXISTE em nenhum framework atual (LangGraph, CrewAI, agency-agents).
"""

from typing import List, Dict, Set
from dataclasses import dataclass

@dataclass
class CapabilityGene:
    """Um gene de capacidade necessário para uma tarefa."""
    name: str
    category: str  # 'frontend', 'backend', 'data', 'ai', etc.
    proficiency: int  # 1-10
    context_keywords: List[str]
    
    def __hash__(self):
        return hash(self.name + self.category)
    
    def __eq__(self, other):
        if not isinstance(other, CapabilityGene):
            return False
        return self.name == other.name and self.category == other.category

class TaskDNAAnalyzer:
    """
    Analisa uma descrição de tarefa e extrai os genes de capacidade.
    
    INOVACAO: Em vez de papéis pré-definidos (ex: "Frontend Dev"),
    extrai capacidades granulares (ex: "React", "TypeScript", "CSS Grid").
    """
    
    # Ontologia de capacidades (não é uma lista estática como agency-agents)
    CAPABILITY_TAXONOMY = {
        'frontend': ['react', 'vue', 'angular', 'css', 'html', 'typescript', 'responsive'],
        'backend': ['api', 'database', 'microservices', 'auth', 'rest', 'graphql'],
        'ai': ['llm', 'prompt-engineering', 'rag', 'fine-tuning', 'embeddings'],
        'data': ['pandas', 'sql', 'etl', 'visualization', 'statistics'],
        'devops': ['docker', 'kubernetes', 'ci-cd', 'monitoring', 'cloud'],
    }
    
    def analyze(self, task_description: str) -> Set[CapabilityGene]:
        """
        Extrai genes de capacidade de uma descrição de tarefa.
        
        Returns:
            Set de CapabilityGene necessários (o "DNA" da tarefa)
        """
        task_lower = task_description.lower()
        required_genes = set()
        
        for category, capabilities in self.CAPABILITY_TAXONOMY.items():
            for cap in capabilities:
                if cap in task_lower:
                    # Determina proficiência baseada em contexto
                    proficiency = self._estimate_proficiency(task_lower, cap)
                    gene = CapabilityGene(
                        name=cap,
                        category=category,
                        proficiency=proficiency,
                        context_keywords=self._extract_context(task_lower, cap)
                    )
                    required_genes.add(gene)
        
        return required_genes
    
    def _estimate_proficiency(self, text: str, capability: str) -> int:
        """Estima nível de proficiência necessário (1-10)."""
        if 'expert' in text or 'advanced' in text:
            return 9
        elif 'senior' in text:
            return 8
        elif 'junior' in text or 'basic' in text:
            return 5
        return 7  # Default
    
    def _extract_context(self, text: str, capability: str) -> List[str]:
        """Extrai palavras-chave de contexto cerca da capacidade."""
        words = text.split()
        idx = words.index(capability) if capability in words else -1
        if idx >= 0:
            start = max(0, idx - 3)
            end = min(len(words), idx + 4)
            return words[start:end]
        return []

# Exemplo de uso (prova de funcionamento)
if __name__ == "__main__":
    analyzer = TaskDNAAnalyzer()
    
    # Tarefa de exemplo (não é um "agente frontend" pré-definido)
    task = "Build a React dashboard with TypeScript and responsive CSS for real-time data visualization"
    
    dna = analyzer.analyze(task)
    
    print("🧬 Task DNA Extracted:")
    for gene in dna:
        print(f"  - {gene.name} ({gene.category}) | Proficiency: {gene.proficiency}/10")
        print(f"    Context: {gene.context_keywords}")
    
    print("\n✅ Nenhum agente pré-definido foi usado. Papéis emergem do DNA!")
