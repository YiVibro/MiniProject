"""
Base Agent Class for AI Agents
==============================

Provides common functionality for all specialized agents in the adaptive learning system.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid
from pydantic import BaseModel, Field

class AgentState(BaseModel):
    """Base state for all agents"""
    agent_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agent_type: str
    user_id: str
    session_id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class AgentResponse(BaseModel):
    """Standard response format for all agents"""
    agent_id: str
    agent_type: str
    response: str
    confidence: float = Field(ge=0.0, le=1.0)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)

class BaseAgent(ABC):
    """Base class for all AI agents"""
    
    def __init__(self, agent_type: str, llm_service):
        self.agent_type = agent_type
        self.llm_service = llm_service
        self.agent_id = str(uuid.uuid4())
    
    @abstractmethod
    async def process(self, state: AgentState) -> AgentResponse:
        """Process the agent's specific task"""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """Return list of agent capabilities"""
        pass
    
    def create_state(self, user_id: str, session_id: str, **kwargs) -> AgentState:
        """Create agent state with common fields"""
        return AgentState(
            agent_type=self.agent_type,
            user_id=user_id,
            session_id=session_id,
            **kwargs
        )
    
    def create_response(self, response: str, confidence: float = 0.8, **kwargs) -> AgentResponse:
        """Create standardized agent response"""
        return AgentResponse(
            agent_id=self.agent_id,
            agent_type=self.agent_type,
            response=response,
            confidence=confidence,
            **kwargs
        )
