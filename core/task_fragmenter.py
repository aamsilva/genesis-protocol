"""
Task Fragmenter Module

Fragments task DNA (lists of CapabilityGene) into TaskFragment objects
that can be processed by the SwarmNegotiator.
"""

from dataclasses import dataclass
from typing import List


@dataclass
class CapabilityGene:
    """Represents a capability required for a task.
    
    Attributes:
        name: The name of the capability.
        category: The category of the capability.
        strength: The strength level (1-10) of the capability.
        tags: List of tags associated with the capability.
    """
    name: str
    category: str
    strength: int  # 1-10
    tags: List[str]


@dataclass
class TaskFragment:
    """A fragment of a task with associated capability requirements.
    
    Attributes:
        fragment_id: Unique identifier for the fragment.
        required_capability: The capability gene required for this fragment.
        complexity_score: Complexity score between 0.0 and 1.0.
    """
    fragment_id: str
    required_capability: CapabilityGene
    complexity_score: float


class TaskFragmenter:
    """Fragments task DNA into executable task fragments."""
    
    def fragment_task(self, dna: List[CapabilityGene]) -> List[TaskFragment]:
        """Convert a list of CapabilityGene objects into TaskFragment objects.
        
        Each CapabilityGene becomes one TaskFragment. The fragment_id is
        generated as 'frag_{index}' and complexity_score is calculated as
        required_capability.strength / 10.0.
        
        Args:
            dna: List of CapabilityGene objects representing task requirements.
            
        Returns:
            List of TaskFragment objects ready for SwarmNegotiator.
        """
        fragments = []
        for index, gene in enumerate(dna):
            fragment = TaskFragment(
                fragment_id=f'frag_{index}',
                required_capability=gene,
                complexity_score=gene.strength / 10.0
            )
            fragments.append(fragment)
        return fragments


def main():
    """Demo function showcasing TaskFragmenter usage."""
    # Create sample capability genes (simulating TaskDNAAnalyzer output)
    sample_dna = [
        CapabilityGene(
            name="python_coding",
            category="programming",
            strength=8,
            tags=["python", "backend", "fastapi"]
        ),
        CapabilityGene(
            name="data_analysis",
            category="analytics",
            strength=6,
            tags=["pandas", "numpy", "visualization"]
        ),
        CapabilityGene(
            name="ui_design",
            category="design",
            strength=9,
            tags=["react", "css", "responsive"]
        )
    ]
    
    print("=" * 60)
    print("Task Fragmenter Demo")
    print("=" * 60)
    
    # Create fragmenter and fragment the task
    fragmenter = TaskFragmenter()
    fragments = fragmenter.fragment_task(sample_dna)
    
    print(f"\nInput: {len(sample_dna)} CapabilityGene objects")
    print(f"Output: {len(fragments)} TaskFragment objects\n")
    
    print("-" * 60)
    print("Fragment Details:")
    print("-" * 60)
    
    for fragment in fragments:
        print(f"\nFragment ID: {fragment.fragment_id}")
        print(f"  Required Capability: {fragment.required_capability.name}")
        print(f"  Category: {fragment.required_capability.category}")
        print(f"  Strength: {fragment.required_capability.strength}")
        print(f"  Tags: {', '.join(fragment.required_capability.tags)}")
        print(f"  Complexity Score: {fragment.complexity_score:.1f}")
    
    print("\n" + "=" * 60)
    print("Demo completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
