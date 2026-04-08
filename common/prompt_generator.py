
from typing import Callable, Optional, List
import inspect
import re

class PromptGenerator:
    def __init__(self, function_to_test: Callable):
        self._function_to_test = function_to_test
        
        self._func_name = self._function_to_test.__name__
        self._lines, _ = inspect.getsourcelines(self._function_to_test)
        self._lines = "".join(self._lines)

    def generate_prompt(self, few_shot_examples: Optional[List[str]] = None):
        """Generate a prompt for the given function."""
        self._few_shot_examples = few_shot_examples
        #prompt = f" I am testing a function which takes a string representing a file's name, and returns   \
    #$'Yes' if the the file's name is valid, and returns 'No' otherwise.Generate diverse tests for the function {self._func_name} \n " 
        prompt = f"Generate tests with pytest for the function {self._func_name} \n I want you to generate a test function that has multiple assert statements that are formatted as follows: assert function_to_test(input) == expected_output. Try to minimize the number of test cases. The test function should be named test_{self._func_name} and should be written in a way that it can be directly executed. The function to test is defined as follows:\n"
        if self._few_shot_examples:

            for example in self._few_shot_examples:

                prompt += "Input\n"
                prompt += f"{self._lines}\n"
                prompt += "Example\n"
                prompt += f"{example}\n"

        #print(f"Lines {self._lines}")   
        prompt += "Input\n"
        prompt += f"{self._lines}\n"

        final_prompt = ''.join(prompt)
        comment_regex = r'""".*?"""'
        final_prompt = re.sub(comment_regex, '', final_prompt, flags=re.DOTALL)
        

        return final_prompt
