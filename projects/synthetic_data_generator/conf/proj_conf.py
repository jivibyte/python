import os
from time import time

def timer(func):
    """
    Decorator that measures and tracks the execution time of a function.
    Records the execution time of the decorated function and maintains a running
    total of all execution times. Prints both the individual execution time and
    the cumulative total after each function call.
    Args:
        func: The function to be decorated and timed.
    Returns:
        wrapper: The wrapped function that tracks execution time.
    Example:
        @timer
        def my_function():
            pass
        my_function()  # Prints: Execution time: 0.001   Total: 0.001
        my_function()  # Prints: Execution time: 0.002   Total: 0.003
    """
    def wrapper(*args, **kwargs):
        nonlocal total
        start = time()
        result = func(*args, **kwargs)
        duration = time() - start
        total += duration
        print(f"Execution time: {duration}   Total: {total}")
        return result

    total = 0
    return wrapper

def get_proj_home():
    """
    Get the project home directory path.
    
    This function determines the project home directory by:
    1. Finding the directory containing the current file
    2. Converting backslashes to forward slashes for cross-platform compatibility
    3. Changing the current working directory to the config directory
    4. Moving up one directory level to reach the project root
    5. Retrieving and normalizing the absolute path
    
    Returns:
        str: The absolute path to the project home directory with forward slashes.
    """
    proj_path = os.path.dirname(os.path.abspath(__file__))
    set_cwdproj_path = proj_path.replace('\\', '/')
    os.chdir(set_cwdproj_path) 
    os.chdir('..')
    proj_home = os.getcwd().replace('\\', '/')
    return proj_home

def get_output_path():
    """
    Retrieve the output directory path for the project.

    Constructs the output directory path by joining the project home directory
    with an 'output' subdirectory. Path separators are normalized to forward slashes.

    Returns:
        str: The absolute path to the project's output directory with forward slashes.
    """
    proj_home = get_proj_home()
    output_path = os.path.join(proj_home, 'output').replace('\\', '/')
    return output_path
