from typing import Any, Dict, Optional
from utils.logging_utils import get_logger
import time

class Node:
    def __init__(self, max_retries: int = 1, wait: int = 0):
        """Initialize a node.
        
        Args:
            max_retries (int): Maximum number of retries for exec()
            wait (int): Time to wait between retries in seconds
        """
        self.max_retries = max_retries
        self.wait = wait
        self.cur_retry = 0
        self.params = {}
        self.logger = get_logger(self.__class__.__name__)

    def set_params(self, params: Dict[str, Any]) -> None:
        """Set parameters for this node."""
        self.logger.debug(f"Setting params: {params}")
        self.params = params

    def prep(self, shared: Dict[str, Any]) -> Any:
        """Read and preprocess data from shared store.
        
        Args:
            shared: The shared memory store
            
        Returns:
            Data to be passed to exec()
        """
        return None

    def exec(self, prep_res: Any) -> Any:
        """Execute compute logic.
        
        Args:
            prep_res: Result from prep()
            
        Returns:
            Data to be passed to post()
        """
        return None

    def exec_fallback(self, prep_res: Any, exc: Exception) -> Any:
        """Handle exec() failures after all retries.
        
        Args:
            prep_res: Result from prep()
            exc: The exception that caused the failure
            
        Returns:
            Fallback data to be passed to post()
        """
        self.logger.error(f"All retries failed. Last error: {str(exc)}")
        raise exc

    def post(self, shared: Dict[str, Any], prep_res: Any, exec_res: Any) -> Optional[str]:
        """Postprocess and write data back to shared store.
        
        Args:
            shared: The shared memory store
            prep_res: Result from prep()
            exec_res: Result from exec() or exec_fallback()
            
        Returns:
            Action string for flow control, or None for "default"
        """
        return None

    def run(self, shared: Dict[str, Any]) -> str:
        """Run this node's full cycle.
        
        Args:
            shared: The shared memory store
            
        Returns:
            Action string for flow control
        """
        self.logger.info(f"Starting node execution")
        
        # Run prep
        self.logger.debug("Running prep()")
        prep_res = self.prep(shared)
        self.logger.debug(f"prep() returned: {prep_res}")
        
        # Run exec with retries
        exec_res = None
        last_exc = None
        
        for self.cur_retry in range(self.max_retries):
            try:
                self.logger.debug(f"Running exec() (attempt {self.cur_retry + 1}/{self.max_retries})")
                exec_res = self.exec(prep_res)
                self.logger.debug(f"exec() succeeded: {exec_res}")
                break
            except Exception as e:
                last_exc = e
                self.logger.warning(f"exec() failed (attempt {self.cur_retry + 1}): {str(e)}")
                if self.cur_retry < self.max_retries - 1:
                    if self.wait > 0:
                        self.logger.debug(f"Waiting {self.wait} seconds before retry")
                        time.sleep(self.wait)
                    continue
                self.logger.debug("Trying fallback")
                exec_res = self.exec_fallback(prep_res, e)
                break
        
        # Run post
        self.logger.debug("Running post()")
        action = self.post(shared, prep_res, exec_res)
        action = action if action is not None else "default"
        self.logger.info(f"Node execution completed with action: {action}")
        
        return action 