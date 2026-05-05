"""
Genesis Protocol - Reputation System
Trust and reputation tracking for agents using Laplace smoothing.

Integrates with:
- AgentSpawner: Reads/updates agent success_rate
- SwarmNegotiator: Provides trust scores for P2P negotiation

Uses SQLite for persistence with Laplace smoothing to avoid zero-trust issues.
"""

import sqlite3
import os
from typing import Optional, Dict, List
from dataclasses import dataclass, field


@dataclass
class AgentReputation:
    """Represents an agent's reputation data."""
    agent_id: str
    success_count: int
    total_tasks: int
    trust_score: float = 0.0
    
    def __post_init__(self):
        """Calculate trust score after initialization."""
        self.trust_score = self.calculate_trust()
    
    def calculate_trust(self) -> float:
        """
        Calculate trust score using Laplace smoothing.
        
        Laplace smoothing: (success_count + 1) / (total_tasks + 2)
        This avoids 0 trust for new agents and provides Bayesian prior.
        
        Returns:
            Trust score between 0.0 and 1.0
        """
        if self.total_tasks == 0:
            # New agent: (0 + 1) / (0 + 2) = 0.5 initial trust
            return 0.5
        return (self.success_count + 1) / (self.total_tasks + 2)
    
    def update(self, success: bool) -> float:
        """
        Update reputation based on task execution result.
        
        Args:
            success: Whether the task was completed successfully
            
        Returns:
            Updated trust score
        """
        self.total_tasks += 1
        if success:
            self.success_count += 1
        self.trust_score = self.calculate_trust()
        return self.trust_score


class ReputationSystem:
    """
    Reputation system for tracking agent trust scores.
    
    Uses SQLite for persistence and Laplace smoothing for trust calculation.
    Integrates with AgentSpawner and SwarmNegotiator.
    """
    
    def __init__(self, db_path: str = None):
        """
        Initialize the reputation system.
        
        Args:
            db_path: Path to SQLite database file. 
                     Defaults to ~/.genesis_protocol/reputation.db
        """
        if db_path is None:
            home = os.path.expanduser("~")
            data_dir = os.path.join(home, ".genesis_protocol")
            os.makedirs(data_dir, exist_ok=True)
            db_path = os.path.join(data_dir, "reputation.db")
        
        self.db_path = db_path
        self._init_database()
        self._cache: Dict[str, AgentReputation] = {}
        self._load_cache()
    
    def _init_database(self):
        """Initialize SQLite database with agents table."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agents (
                agent_id TEXT PRIMARY KEY,
                success_count INTEGER NOT NULL DEFAULT 0,
                total_tasks INTEGER NOT NULL DEFAULT 0,
                trust_score REAL NOT NULL DEFAULT 0.5,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create index for faster lookups
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_agent_id 
            ON agents(agent_id)
        """)
        
        conn.commit()
        conn.close()
    
    def _get_connection(self):
        """Get a database connection with timeout to avoid locks."""
        return sqlite3.connect(self.db_path, timeout=10)
    
    def _load_cache(self):
        """Load all agent reputations from database into cache."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Ensure table exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agents (
                agent_id TEXT PRIMARY KEY,
                success_count INTEGER NOT NULL DEFAULT 0,
                total_tasks INTEGER NOT NULL DEFAULT 0,
                trust_score REAL NOT NULL DEFAULT 0.5,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            SELECT agent_id, success_count, total_tasks, trust_score 
            FROM agents
        """)
        
        for row in cursor.fetchall():
            agent_id, success_count, total_tasks, trust_score = row
            self._cache[agent_id] = AgentReputation(
                agent_id=agent_id,
                success_count=success_count,
                total_tasks=total_tasks,
                trust_score=trust_score
            )
        
        conn.close()
    
    def _save_agent(self, agent_rep: AgentReputation):
        """Save a single agent's reputation to database."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Ensure table exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agents (
                agent_id TEXT PRIMARY KEY,
                success_count INTEGER NOT NULL DEFAULT 0,
                total_tasks INTEGER NOT NULL DEFAULT 0,
                trust_score REAL NOT NULL DEFAULT 0.5,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            INSERT INTO agents (agent_id, success_count, total_tasks, trust_score, last_updated)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(agent_id) 
            DO UPDATE SET 
                success_count = excluded.success_count,
                total_tasks = excluded.total_tasks,
                trust_score = excluded.trust_score,
                last_updated = CURRENT_TIMESTAMP
        """, (agent_rep.agent_id, agent_rep.success_count, 
              agent_rep.total_tasks, agent_rep.trust_score))
        
        conn.commit()
        conn.close()
    
    def update_trust(self, agent_id: str, success: bool) -> float:
        """
        Update an agent's trust score based on task execution result.
        
        Args:
            agent_id: The agent's unique identifier
            success: Whether the task was completed successfully
            
        Returns:
            Updated trust score (0.0 - 1.0)
        """
        if agent_id not in self._cache:
            # New agent - create with initial values
            self._cache[agent_id] = AgentReputation(
                agent_id=agent_id,
                success_count=0,
                total_tasks=0
            )
        
        agent_rep = self._cache[agent_id]
        new_trust = agent_rep.update(success)
        
        # Persist to database
        self._save_agent(agent_rep)
        
        return new_trust
    
    def get_trust(self, agent_id: str) -> float:
        """
        Get an agent's current trust score.
        
        Args:
            agent_id: The agent's unique identifier
            
        Returns:
            Trust score between 0.0 and 1.0
            Returns 0.5 for unknown agents (Laplace prior)
        """
        if agent_id not in self._cache:
            # Return Laplace prior for unknown agents
            return 0.5
        
        return self._cache[agent_id].trust_score
    
    def get_reputation(self, agent_id: str) -> Optional[AgentReputation]:
        """
        Get full reputation data for an agent.
        
        Args:
            agent_id: The agent's unique identifier
            
        Returns:
            AgentReputation object or None if not found
        """
        return self._cache.get(agent_id)
    
    def get_all_reputations(self) -> List[AgentReputation]:
        """
        Get all agent reputations.
        
        Returns:
            List of all AgentReputation objects
        """
        return list(self._cache.values())
    
    def get_top_agents(self, limit: int = 10) -> List[AgentReputation]:
        """
        Get top agents by trust score.
        
        Args:
            limit: Maximum number of agents to return
            
        Returns:
            List of top AgentReputation objects sorted by trust score
        """
        sorted_agents = sorted(
            self._cache.values(), 
            key=lambda a: a.trust_score, 
            reverse=True
        )
        return sorted_agents[:limit]
    
    def sync_agent_success_rate(self, agent_id: str, dynamic_agent: 'DynamicAgent'):
        """
        Sync trust score back to AgentSpawner's DynamicAgent.
        
        This allows AgentSpawner to use the reputation system's trust score
        instead of its own simple success_rate tracking.
        
        Args:
            agent_id: The agent's unique identifier
            dynamic_agent: The DynamicAgent instance to update
        """
        trust = self.get_trust(agent_id)
        dynamic_agent.success_rate = trust
    
    def get_trust_for_negotiation(self, agent_id: str) -> float:
        """
        Get trust score formatted for SwarmNegotiator.
        
        This method provides trust scores for P2P negotiation.
        Includes the Laplace smoothing benefit automatically.
        
        Args:
            agent_id: The agent's unique identifier
            
        Returns:
            Trust score optimized for negotiation (0.0 - 1.0)
        """
        return self.get_trust(agent_id)
    
    def save_all(self):
        """Explicitly save all cached reputations to database."""
        for agent_rep in self._cache.values():
            self._save_agent(agent_rep)
    
    def reset_agent(self, agent_id: str):
        """
        Reset an agent's reputation to initial state.
        
        Args:
            agent_id: The agent's unique identifier
        """
        if agent_id in self._cache:
            del self._cache[agent_id]
        
        # Remove from database
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Ensure table exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agents (
                agent_id TEXT PRIMARY KEY,
                success_count INTEGER NOT NULL DEFAULT 0,
                total_tasks INTEGER NOT NULL DEFAULT 0,
                trust_score REAL NOT NULL DEFAULT 0.5,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("DELETE FROM agents WHERE agent_id = ?", (agent_id,))
        conn.commit()
        conn.close()
    
    def get_stats(self) -> Dict:
        """
        Get statistics about the reputation system.
        
        Returns:
            Dictionary with statistics
        """
        if not self._cache:
            return {
                "total_agents": 0,
                "total_tasks": 0,
                "average_trust": 0.5,
                "average_success_rate": 0.5
            }
        
        total_tasks = sum(a.total_tasks for a in self._cache.values())
        avg_trust = sum(a.trust_score for a in self._cache.values()) / len(self._cache)
        
        # Calculate actual success rate (without Laplace smoothing)
        total_success = sum(a.success_count for a in self._cache.values())
        avg_success = total_success / total_tasks if total_tasks > 0 else 0.5
        
        return {
            "total_agents": len(self._cache),
            "total_tasks": total_tasks,
            "average_trust": round(avg_trust, 3),
            "average_success_rate": round(avg_success, 3)
        }


# Convenience function for quick trust updates
def update_agent_trust(reputation_system: ReputationSystem, 
                      agent_id: str, 
                      success: bool, 
                      dynamic_agent: Optional['DynamicAgent'] = None) -> float:
    """
    Convenience function to update trust and optionally sync to DynamicAgent.
    
    Args:
        reputation_system: The ReputationSystem instance
        agent_id: The agent's unique identifier
        success: Whether the task was successful
        dynamic_agent: Optional DynamicAgent to sync success_rate
        
    Returns:
        Updated trust score
    """
    trust = reputation_system.update_trust(agent_id, success)
    
    if dynamic_agent is not None:
        dynamic_agent.success_rate = trust
    
    return trust


if __name__ == "__main__":
    """
    Demo of the ReputationSystem.
    """
    print("=" * 60)
    print("🧬 GENESIS PROTOCOL - REPUTATION SYSTEM DEMO")
    print("=" * 60)
    
    # Create reputation system (uses default ~/.genesis_protocol/reputation.db)
    rep_system = ReputationSystem()
    
    # Simulate some task executions
    print("\n📊 Simulating task executions...\n")
    
    agents = ["agent_abc123", "agent_def456", "agent_ghi789"]
    
    # Agent 1: High success rate
    print("Agent abc123: 10 tasks, 9 successful")
    for i in range(10):
        success = (i < 9)  # 9 out of 10 successful
        trust = rep_system.update_trust("agent_abc123", success)
        if i == 9:
            print(f"  Final trust after 10 tasks: {trust:.3f}")
    
    # Agent 2: Medium success rate
    print("\nAgent def456: 10 tasks, 6 successful")
    for i in range(10):
        success = (i < 6)  # 6 out of 10 successful
        trust = rep_system.update_trust("agent_def456", success)
        if i == 9:
            print(f"  Final trust after 10 tasks: {trust:.3f}")
    
    # Agent 3: New agent (Laplace prior)
    print("\nAgent ghi789: New agent (no tasks yet)")
    trust = rep_system.get_trust("agent_ghi789")
    print(f"  Initial trust (Laplace prior): {trust:.3f}")
    
    # First task for new agent - successful
    trust = rep_system.update_trust("agent_ghi789", True)
    print(f"  Trust after 1st successful task: {trust:.3f}")
    
    # Get top agents
    print("\n🏆 Top agents by trust score:")
    top_agents = rep_system.get_top_agents()
    for i, agent in enumerate(top_agents, 1):
        print(f"  {i}. {agent.agent_id}: {agent.trust_score:.3f} "
              f"({agent.success_count}/{agent.total_tasks} tasks)")
    
    # Get statistics
    print("\n📈 Reputation System Statistics:")
    stats = rep_system.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Integration example with AgentSpawner
    print("\n🔗 Integration with AgentSpawner:")
    print("  # Example: sync_agent_success_rate(agent_id, dynamic_agent)")
    print("  # This updates dynamic_agent.success_rate with trust score")
    
    # Integration example with SwarmNegotiator
    print("\n🔗 Integration with SwarmNegotiator:")
    print("  # Example: trust = rep_system.get_trust_for_negotiation(agent_id)")
    print("  # Use trust score in P2P negotiation confidence calculation")
    
    print("\n" + "=" * 60)
    print("✅ REPUTATION SYSTEM READY")
    print("   • SQLite persistence: ~/.genesis_protocol/reputation.db")
    print("   • Laplace smoothing: (success + 1) / (total + 2)")
    print("   • Integrates with AgentSpawner & SwarmNegotiator")
    print("=" * 60)
