from typing import Any, Dict, Optional
from .base import Node
from utils.call_llm import call_llm
import json

class FormatResponseNode(Node):
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare context for response generation."""
        return {
            "query": shared["user_query"],
            "history": shared["history"],
            "working_dir": shared["working_dir"]
        }
        
    def exec(self, context: Dict[str, Any]) -> str:
        """Generate a user-friendly response."""
        prompt = f"""
Given the following context, generate a clear and concise response for the user.

USER QUERY:
{context['query']}

ACTION HISTORY:
{json.dumps(context['history'], indent=2)}

Guidelines:
1. Summarize what was done
2. Include relevant results or findings
3. If there were errors, explain them clearly
4. If further actions are needed, suggest them
5. Keep the tone professional but friendly

Return your response in markdown format.
"""
        return call_llm(prompt)
        
    def post(self, shared: Dict[str, Any], prep_res: Any, exec_res: Any) -> str:
        """Store the formatted response."""
        shared["response"] = exec_res
        return "done" 