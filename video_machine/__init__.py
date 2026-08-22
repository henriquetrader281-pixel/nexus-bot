"""Máquina de Vídeos Nexus — núcleo de projetos, agentes e memória."""

from .agents import AGENT_SPECS, AgentOrchestrator, AgentResult, AgentSpec, list_agents
from .memory_store import load_memory, recent_context, record_agent_run, record_learning
from .project_store import Scene, VideoProject, add_scene, create_project, list_projects, load_project, save_project

__all__ = [
    "AGENT_SPECS",
    "AgentOrchestrator",
    "AgentResult",
    "AgentSpec",
    "Scene",
    "VideoProject",
    "add_scene",
    "create_project",
    "list_agents",
    "list_projects",
    "load_memory",
    "load_project",
    "recent_context",
    "record_agent_run",
    "record_learning",
    "save_project",
]
