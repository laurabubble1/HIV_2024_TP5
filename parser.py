import re
import ast

def extract_seed_input(test_code: str):
    """
    Extracts the seed input from the generated test code.
    First tries to find 'seed_input = ...', then falls back to extracting
    arguments from function calls in assertions.

    Args:
        test_code (str): The generated test code as a string.

    Returns:
        str or list: The extracted seed input(s) as a string representation.
    """
    # Use regular expressions to find the seed input in the test code
    seed_input_pattern = r"seed_input\s*=\s*(.*)"
    match = re.search(seed_input_pattern, test_code)
    
    if match:
        seed_input = match.group(1).strip()
        return seed_input
    else:
        # Try to extract inputs from function calls in assertions
        # Pattern: function_name(arg) where arg is a literal (number or string)
        function_call_pattern = r"\w+\(([^)]+)\)\s*=="
        matches = re.findall(function_call_pattern, test_code)
        
        if matches:
            inputs = []
            for arg_str in matches:
                arg_str = arg_str.strip()
                try:
                    # Try to parse as Python literal
                    parsed = ast.literal_eval(arg_str)
                    inputs.append(parsed)
                except (ValueError, SyntaxError):
                    # If parsing fails, keep as string
                    inputs.append(arg_str)
            
            if inputs:
                return repr(inputs)  # Return as string representation of list
        
        # If nothing found, return empty list
        return repr([])