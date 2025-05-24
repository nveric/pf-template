from typing import Any, Dict, Optional, List, Tuple
from nodes.base import Node
from utils.logging_utils import get_logger

logger = get_logger(__name__)

class Flow:
    def __init__(self, start: Node):
        """Initialize a flow with a start node.
        
        Args:
            start: The starting node
        """
        self.start = start
        self.transitions: Dict[Tuple[Node, str], Node] = {}
        self.params: Dict[str, Any] = {}
        self.logger = logger
        
    def set_params(self, params: Dict[str, Any]) -> None:
        """Set parameters for this flow."""
        self.params = params
        
    def __rshift__(self, other: Node) -> None:
        """Add a default transition (>>) from last added node to other."""
        if not hasattr(self, '_last_node'):
            self._last_node = self.start
        self.add_transition(self._last_node, "default", other)
        self._last_node = other
        
    def add_transition(self, from_node: Node, action: str, to_node: Node) -> None:
        """Add a transition between nodes.
        
        Args:
            from_node: Source node
            action: Action string that triggers this transition
            to_node: Target node
        """
        self.transitions[(from_node, action)] = to_node
        self.logger.debug(f"Added transition: {from_node.__class__.__name__} --{action}--> {to_node.__class__.__name__}")
        
    def run(self, shared: Dict[str, Any]) -> None:
        """Run this flow from start to finish.
        
        Args:
            shared: The shared memory store
        """
        current_node = self.start
        self.logger.info(f"Starting flow with {current_node.__class__.__name__}")
        
        # Set flow params on start node
        current_node.set_params(self.params)
        
        while current_node:
            # Log current node and shared state
            self.logger.debug(f"Running node: {current_node.__class__.__name__}")
            self.logger.debug(f"Shared state: {shared}")
            
            try:
                # Run the node
                action = current_node.run(shared)
                self.logger.info(f"Node {current_node.__class__.__name__} returned action: {action}")
                
                # Find next node
                next_node = self.transitions.get((current_node, action))
                if next_node:
                    self.logger.debug(f"Transitioning to: {next_node.__class__.__name__}")
                    next_node.set_params(self.params)
                    current_node = next_node
                else:
                    if action != "done":
                        self.logger.warning(f"No transition found for action '{action}' from {current_node.__class__.__name__}")
                    current_node = None
                    
            except Exception as e:
                self.logger.error(f"Error in node {current_node.__class__.__name__}: {str(e)}", exc_info=True)
                raise

class EditFlow(Flow):
    """Special flow for edit operations that maintains its own params."""
    def run(self, shared: Dict[str, Any]) -> None:
        """Run the edit flow, preserving edit-specific params."""
        # Store edit params from the history entry
        history_entry = shared["history"][-1]
        assert history_entry["tool"] == "edit_file"
        
        self.set_params(history_entry["params"])
        super().run(shared)