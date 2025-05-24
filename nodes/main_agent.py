from typing import Any, Dict, Optional
from .base import Node
from utils.call_llm import call_llm
import yaml
import json
from datetime import datetime

class MainDecisionAgent(Node):
    def __init__(self):
        super().__init__(max_retries=2)  # Allow 2 retries for LLM calls
        
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare context for decision making.
        
        Returns dict with:
            - user_query: Current user request
            - history: Relevant action history
            - working_dir: Current working directory
        """
        return {
            "query": shared["user_query"],
            "history": shared.get("history", []),
            "working_dir": shared["working_dir"]
        }
        
    def exec(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Decide which tool to use based on context.
        
        Returns dict with:
            - tool: Selected tool name
            - reason: Explanation for tool selection
            - params: Parameters for the tool
        """
        # Construct prompt
        prompt = f"""
Given the following context, decide which tool to use next:

USER QUERY: {context['query']}

PREVIOUS ACTIONS:
{json.dumps(context['history'], indent=2)}

AVAILABLE TOOLS:
1. read_file
   - target_file: Path to file (relative to {context['working_dir']})
   - explanation: Why read this file

2. edit_file
   - target_file: Path to file
   - instructions: Clear description of edit
   - code_edit: Code changes with context

3. delete_file
   - target_file: Path to file
   - explanation: Why delete

4. grep_search
   - query: Text/regex to find
   - case_sensitive: (optional) boolean
   - include_pattern: (optional) e.g. "*.py"
   - exclude_pattern: (optional)
   - explanation: Why search

5. list_dir
   - relative_workspace_path: Path to list
   - explanation: Why list directory

6. finish
   - Return final response to user

Decide the next action and return in YAML format:
```yaml
thinking: |
    <your step-by-step reasoning>
tool: <tool_name>
reason: <one-line explanation>
params:
    <parameter_name>: <parameter_value>
    ...
```
"""
        # Get LLM response
        response = call_llm(prompt)
        
        # Extract YAML part
        yaml_str = response.split("```yaml")[1].split("```")[0].strip()
        decision = yaml.safe_load(yaml_str)
        
        # Validate decision
        assert "tool" in decision, "Tool name missing"
        assert "reason" in decision, "Reason missing"
        assert "params" in decision, "Parameters missing"
        assert isinstance(decision["params"], dict), "Parameters must be a dict"
        
        if decision["tool"] not in ["read_file", "edit_file", "delete_file", "grep_search", "list_dir", "finish"]:
            raise ValueError(f"Invalid tool: {decision['tool']}")
            
        return decision
        
    def post(self, shared: Dict[str, Any], prep_res: Any, exec_res: Any) -> str:
        """Update history and return next action.
        
        Args:
            shared: Shared memory store
            prep_res: Context dict from prep()
            exec_res: Decision dict from exec()
            
        Returns:
            Action string (tool name)
        """
        # Initialize history if needed
        if "history" not in shared:
            shared["history"] = []
            
        # Add new action to history
        shared["history"].append({
            "tool": exec_res["tool"],
            "reason": exec_res["reason"],
            "params": exec_res["params"],
            "timestamp": datetime.now().isoformat()
        })
        
        # For finish action, prepare response
        if exec_res["tool"] == "finish":
            shared["response"] = exec_res["params"].get("response", "Task completed")
            return "finish"
            
        # Return tool name as action
        return exec_res["tool"] 