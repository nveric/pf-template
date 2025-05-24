import os

def read_file(target_file):
    """Reads content from specified files.
    
    Args:
        target_file (str): Path to the file to read
        
    Returns:
        tuple: (file content, success status)
    """
    try:
        with open(target_file, 'r', encoding='utf-8') as f:
            content = f.read()
        return content, True
    except Exception as e:
        return str(e), False

def insert_file(target_file, content, line_number=None):
    """Writes or inserts content to a target file.
    
    Args:
        target_file (str): Path to the file
        content (str): Content to insert
        line_number (int, optional): Line number to insert at. If None, appends to end.
        
    Returns:
        tuple: (result message, success status)
    """
    try:
        if line_number is None:
            # Append mode
            with open(target_file, 'a', encoding='utf-8') as f:
                f.write(content)
        else:
            # Insert at specific line
            with open(target_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Insert the content
            lines.insert(line_number - 1, content + '\n')
            
            with open(target_file, 'w', encoding='utf-8') as f:
                f.writelines(lines)
                
        return "Content inserted successfully", True
    except Exception as e:
        return str(e), False

def remove_file(target_file, start_line=None, end_line=None):
    """Removes content from a file based on line numbers.
    
    Args:
        target_file (str): Path to the file
        start_line (int, optional): First line to remove (1-indexed)
        end_line (int, optional): Last line to remove (1-indexed)
        
    Returns:
        tuple: (result message, success status)
    """
    try:
        with open(target_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if start_line is None or end_line is None:
            # Remove entire file content
            lines = []
        else:
            # Remove specific lines
            del lines[start_line - 1:end_line]
        
        with open(target_file, 'w', encoding='utf-8') as f:
            f.writelines(lines)
            
        return "Content removed successfully", True
    except Exception as e:
        return str(e), False

def delete_file(target_file):
    """Deletes a file from the file system.
    
    Args:
        target_file (str): Path to the file to delete
        
    Returns:
        tuple: (result message, success status)
    """
    try:
        os.remove(target_file)
        return "File deleted successfully", True
    except Exception as e:
        return str(e), False

def replace_file(target_file, start_line, end_line, new_content):
    """Replaces content in a file based on line numbers.
    
    Args:
        target_file (str): Path to the file
        start_line (int): First line to replace (1-indexed)
        end_line (int): Last line to replace (1-indexed)
        new_content (str): Content to replace with
        
    Returns:
        tuple: (result message, success status)
    """
    try:
        with open(target_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Replace the lines
        lines[start_line - 1:end_line] = [new_content + '\n']
        
        with open(target_file, 'w', encoding='utf-8') as f:
            f.writelines(lines)
            
        return "Content replaced successfully", True
    except Exception as e:
        return str(e), False

if __name__ == "__main__":
    # Example usage
    test_file = "test.txt"
    
    # Create a test file
    with open(test_file, 'w') as f:
        f.write("Line 1\nLine 2\nLine 3\n")
    
    # Test read
    content, success = read_file(test_file)
    print(f"Read file: {content}")
    
    # Test insert
    insert_file(test_file, "New Line", 2)
    
    # Test replace
    replace_file(test_file, 2, 2, "Replaced Line")
    
    # Test remove
    remove_file(test_file, 1, 1)
    
    # Test delete
    delete_file(test_file) 