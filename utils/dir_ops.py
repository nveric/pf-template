import os
from typing import Tuple

def list_dir(relative_workspace_path: str) -> Tuple[bool, str]:
    """Lists contents of a directory with a tree visualization.
    
    Args:
        relative_workspace_path (str): Path to list contents of
        
    Returns:
        tuple: (success status, tree visualization string)
    """
    try:
        # Convert to absolute path
        abs_path = os.path.abspath(relative_workspace_path)
        
        if not os.path.exists(abs_path):
            return False, f"Path does not exist: {relative_workspace_path}"
            
        if not os.path.isdir(abs_path):
            return False, f"Path is not a directory: {relative_workspace_path}"
        
        # Initialize tree string
        tree = []
        
        def add_to_tree(path: str, prefix: str = ""):
            # List directory contents
            entries = os.listdir(path)
            entries.sort()
            
            # Process each entry
            for i, entry in enumerate(entries):
                # Skip hidden files
                if entry.startswith('.'):
                    continue
                    
                # Full path
                full_path = os.path.join(path, entry)
                
                # Is this the last entry?
                is_last = i == len(entries) - 1
                
                # Add to tree
                if is_last:
                    tree.append(f"{prefix}└── {entry}")
                    new_prefix = prefix + "    "
                else:
                    tree.append(f"{prefix}├── {entry}")
                    new_prefix = prefix + "│   "
                
                # Recurse into directories
                if os.path.isdir(full_path):
                    add_to_tree(full_path, new_prefix)
        
        # Start with the root directory name
        root_name = os.path.basename(abs_path.rstrip('/\\'))
        tree.append(root_name)
        
        # Build the tree
        add_to_tree(abs_path)
        
        return True, '\n'.join(tree)
        
    except Exception as e:
        return False, str(e)

if __name__ == "__main__":
    # Example usage
    success, tree = list_dir(".")
    if success:
        print(tree)
    else:
        print(f"Error: {tree}") 