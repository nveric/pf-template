from typing import Any, Dict, Optional
import os
from .base import Node
from utils.file_ops import read_file, delete_file, replace_file
from utils.call_llm import call_llm

class ReadFileNode(Node):
    def prep(self, shared: Dict[str, Any]) -> str:
        """Get file path from last history entry."""
        history_entry = shared["history"][-1]
        assert history_entry["tool"] == "read_file"
        
        # Get relative path and make it absolute
        rel_path = history_entry["params"]["target_file"]
        return os.path.join(shared["working_dir"], rel_path)
        
    def exec(self, file_path: str) -> tuple:
        """Read the file content."""
        return read_file(file_path)
        
    def post(self, shared: Dict[str, Any], prep_res: Any, exec_res: Any) -> str:
        """Store result in history and return to main agent."""
        content, success = exec_res
        shared["history"][-1]["result"] = {
            "success": success,
            "content": content if success else None,
            "error": None if success else content
        }
        return "decide_next"

class DeleteFileNode(Node):
    def prep(self, shared: Dict[str, Any]) -> str:
        """Get file path from last history entry."""
        history_entry = shared["history"][-1]
        assert history_entry["tool"] == "delete_file"
        
        rel_path = history_entry["params"]["target_file"]
        return os.path.join(shared["working_dir"], rel_path)
        
    def exec(self, file_path: str) -> tuple:
        """Delete the file."""
        return delete_file(file_path)
        
    def post(self, shared: Dict[str, Any], prep_res: Any, exec_res: Any) -> str:
        """Store result in history and return to main agent."""
        message, success = exec_res
        shared["history"][-1]["result"] = {
            "success": success,
            "message": message
        }
        return "decide_next"

class EditFileNode(Node):
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Get file info and edit instructions."""
        history_entry = shared["history"][-1]
        assert history_entry["tool"] == "edit_file"
        
        rel_path = history_entry["params"]["target_file"]
        abs_path = os.path.join(shared["working_dir"], rel_path)
        
        # Read current content
        content, success = read_file(abs_path)
        if not success:
            raise ValueError(f"Could not read file: {content}")
            
        return {
            "file_path": abs_path,
            "current_content": content,
            "instructions": history_entry["params"]["instructions"],
            "code_edit": history_entry["params"]["code_edit"]
        }
        
    def exec(self, context: Dict[str, Any]) -> list:
        """Analyze and plan the edits."""
        prompt = f"""
Analyze the following file content and edit instructions.
Return a list of specific edits to make.

CURRENT CONTENT:
{context['current_content']}

EDIT INSTRUCTIONS:
{context['instructions']}

CODE EDIT:
{context['code_edit']}

Return the edits as a list in YAML format:
```yaml
edits:
  - start_line: <first line to replace>
    end_line: <last line to replace>
    replacement: |
      <new content>
  ...
```
"""
        response = call_llm(prompt)
        yaml_str = response.split("```yaml")[1].split("```")[0].strip()
        result = yaml.safe_load(yaml_str)
        
        assert "edits" in result, "No edits specified"
        assert isinstance(result["edits"], list), "Edits must be a list"
        
        return result["edits"]
        
    def post(self, shared: Dict[str, Any], prep_res: Any, exec_res: Any) -> str:
        """Store edit plan and proceed to apply changes."""
        shared["edit_operations"] = exec_res
        return "apply_changes"

class ApplyChangesNode(Node):
    def prep(self, shared: Dict[str, Any]) -> list:
        """Get edit operations and sort them in descending order."""
        edits = shared["edit_operations"]
        edits.sort(key=lambda x: x["start_line"], reverse=True)
        return edits
        
    def exec(self, edits: list) -> list:
        """Apply each edit operation."""
        history_entry = shared["history"][-1]
        file_path = os.path.join(
            shared["working_dir"],
            history_entry["params"]["target_file"]
        )
        
        results = []
        for edit in edits:
            message, success = replace_file(
                file_path,
                edit["start_line"],
                edit["end_line"],
                edit["replacement"]
            )
            results.append({"success": success, "message": message})
            
            if not success:
                break
                
        return results
        
    def post(self, shared: Dict[str, Any], prep_res: Any, exec_res: Any) -> str:
        """Store results and clean up."""
        shared["history"][-1]["result"] = {
            "success": all(r["success"] for r in exec_res),
            "operations": exec_res
        }
        
        # Clean up edit operations
        shared.pop("edit_operations", None)
        
        return "decide_next" 