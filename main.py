import os
from typing import Optional
from flow import Flow, EditFlow
from nodes.main_agent import MainDecisionAgent
from nodes.file_ops import ReadFileNode, DeleteFileNode, EditFileNode, ApplyChangesNode
from nodes.search_ops import GrepSearchNode, ListDirectoryNode
from nodes.format_response import FormatResponseNode
from utils.logging_utils import setup_logging, get_logger

logger = get_logger(__name__)

def create_main_flow() -> Flow:
    """Create the main flow with all node connections."""
    # Create nodes
    main_agent = MainDecisionAgent()
    read_file = ReadFileNode()
    delete_file = DeleteFileNode()
    grep_search = GrepSearchNode()
    list_dir = ListDirectoryNode()
    format_response = FormatResponseNode()
    
    # Create edit flow
    edit_flow = create_edit_flow()
    
    # Connect nodes
    main_agent - "read_file" >> read_file
    main_agent - "delete_file" >> delete_file
    main_agent - "grep_search" >> grep_search
    main_agent - "list_dir" >> list_dir
    main_agent - "edit_file" >> edit_flow
    main_agent - "finish" >> format_response
    
    # All tool nodes return to main agent
    read_file - "decide_next" >> main_agent
    delete_file - "decide_next" >> main_agent
    grep_search - "decide_next" >> main_agent
    list_dir - "decide_next" >> main_agent
    edit_flow - "decide_next" >> main_agent
    
    return Flow(start=main_agent)

def create_edit_flow() -> EditFlow:
    """Create the edit file subflow."""
    # Create nodes
    edit_node = EditFileNode()
    apply_changes = ApplyChangesNode()
    
    # Connect nodes
    edit_node - "apply_changes" >> apply_changes
    
    return EditFlow(start=edit_node)

def run_coding_agent(
    query: str,
    working_dir: str,
    log_level: int = logging.INFO,
    log_file: Optional[str] = None
) -> str:
    """Run the coding agent on a query.
    
    Args:
        query: The user's request
        working_dir: The working directory for file operations
        log_level: Logging level
        log_file: Optional log file path
        
    Returns:
        The agent's response
    """
    # Setup logging
    setup_logging(level=log_level, log_file=log_file)
    logger.info(f"Starting coding agent with query: {query}")
    logger.info(f"Working directory: {working_dir}")
    
    try:
        # Create shared memory
        shared = {
            "user_query": query,
            "working_dir": os.path.abspath(working_dir),
            "history": []
        }
        
        # Create and run flow
        flow = create_main_flow()
        flow.run(shared)
        
        # Return response
        response = shared.get("response", "No response generated")
        logger.info("Coding agent completed successfully")
        return response
        
    except Exception as e:
        logger.error("Coding agent failed", exc_info=True)
        raise

if __name__ == "__main__":
    import argparse
    import logging
    
    # Parse arguments
    parser = argparse.ArgumentParser(description="Run the coding agent")
    parser.add_argument("query", help="The user's request")
    parser.add_argument("--working-dir", "-d", default=".", help="Working directory")
    parser.add_argument("--log-file", "-l", help="Log file path")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    
    args = parser.parse_args()
    
    # Run agent
    response = run_coding_agent(
        query=args.query,
        working_dir=args.working_dir,
        log_level=logging.DEBUG if args.debug else logging.INFO,
        log_file=args.log_file
    )
    
    print("\nResponse:")
    print(response)
