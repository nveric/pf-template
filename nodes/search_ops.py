from typing import Any, Dict, Optional
from .base import Node
from utils.search_ops import grep_search
from utils.dir_ops import list_dir
import os

class GrepSearchNode(Node):
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Get search parameters from last history entry."""
        history_entry = shared["history"][-1]
        assert history_entry["tool"] == "grep_search"
        
        params = history_entry["params"].copy()
        params["working_dir"] = shared["working_dir"]
        return params
        
    def exec(self, params: Dict[str, Any]) -> tuple:
        """Execute the search."""
        return grep_search(
            query=params["query"],
            case_sensitive=params.get("case_sensitive", False),
            include_pattern=params.get("include_pattern"),
            exclude_pattern=params.get("exclude_pattern"),
            working_dir=params["working_dir"]
        )
        
    def post(self, shared: Dict[str, Any], prep_res: Any, exec_res: Any) -> str:
        """Store results and return to main agent."""
        matches, success = exec_res
        shared["history"][-1]["result"] = {
            "success": success,
            "matches": matches if success else [],
            "match_count": len(matches) if success else 0
        }
        return "decide_next"

class ListDirectoryNode(Node):
    def prep(self, shared: Dict[str, Any]) -> str:
        """Get directory path from last history entry."""
        history_entry = shared["history"][-1]
        assert history_entry["tool"] == "list_dir"
        
        rel_path = history_entry["params"]["relative_workspace_path"]
        return os.path.join(shared["working_dir"], rel_path)
        
    def exec(self, dir_path: str) -> tuple:
        """List directory contents."""
        return list_dir(dir_path)
        
    def post(self, shared: Dict[str, Any], prep_res: Any, exec_res: Any) -> str:
        """Store results and return to main agent."""
        success, tree_str = exec_res
        shared["history"][-1]["result"] = {
            "success": success,
            "tree": tree_str if success else None,
            "error": tree_str if not success else None
        }
        return "decide_next" 