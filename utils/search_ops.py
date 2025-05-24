import os
import re
from typing import List, Tuple, Optional

def grep_search(
    query: str,
    case_sensitive: bool = False,
    include_pattern: Optional[str] = None,
    exclude_pattern: Optional[str] = None,
    working_dir: Optional[str] = None
) -> Tuple[List[dict], bool]:
    """Searches through files for specific patterns using ripgrep-like functionality.
    
    Args:
        query (str): Pattern to search for
        case_sensitive (bool, optional): Whether to do case-sensitive search
        include_pattern (str, optional): Glob pattern for files to include
        exclude_pattern (str, optional): Glob pattern for files to exclude
        working_dir (str, optional): Directory to search in
        
    Returns:
        tuple: (list of matches, success status)
        Each match is a dict with keys: file_path, line_number, content
    """
    try:
        # Set working directory
        if working_dir:
            os.chdir(working_dir)
        
        # Compile regex pattern
        flags = 0 if case_sensitive else re.IGNORECASE
        pattern = re.compile(query, flags)
        
        matches = []
        max_matches = 50  # Cap results at 50 matches
        
        # Walk through directory
        for root, _, files in os.walk('.'):
            for file in files:
                # Skip binary and excluded files
                if file.startswith('.') or any(file.endswith(ext) for ext in ['.pyc', '.jpg', '.png', '.gif']):
                    continue
                    
                # Check include/exclude patterns
                if include_pattern and not re.match(include_pattern, file):
                    continue
                if exclude_pattern and re.match(exclude_pattern, file):
                    continue
                
                file_path = os.path.join(root, file)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        for i, line in enumerate(f, 1):
                            if pattern.search(line):
                                matches.append({
                                    'file_path': file_path,
                                    'line_number': i,
                                    'content': line.strip()
                                })
                                
                                if len(matches) >= max_matches:
                                    return matches, True
                except UnicodeDecodeError:
                    # Skip files that can't be read as text
                    continue
                    
        return matches, True
    except Exception as e:
        return [], False

if __name__ == "__main__":
    # Example usage
    matches, success = grep_search(
        query="def",
        case_sensitive=False,
        include_pattern=r".*\.py$"  # Only Python files
    )
    
    if success:
        for match in matches:
            print(f"{match['file_path']}:{match['line_number']}: {match['content']}")
    else:
        print("Search failed") 