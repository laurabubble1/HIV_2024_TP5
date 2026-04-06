import os

import dotenv
from google import genai
from common.llm_test_generator import LLMTestGenerator
from common.prompt_generator import PromptGenerator
from common.abstract_executor import AbstractExecutor
from file_name_check import file_name_check
import importlib

dotenv.load_dotenv()
key = os.getenv("API_KEY")
   

if __name__ == "__main__":
    # Configure the generative AI with the API key
    client = genai.Client(api_key=key)

    # Create a generative model
    model_name = "gemini-2.5-flash"

    function_to_test = file_name_check

    ######Generate intial tests with LLM


    # Create an LLMTestGenerator object with the generative model and the function to test
    llm_generator = LLMTestGenerator(client, model_name=model_name, function=function_to_test)

    # Create a PromptGenerator object with the function to test
    prompt_generator = PromptGenerator(function_to_test)

    # Generate a prompt for the function
    prompt = prompt_generator.generate_prompt()

    # Print the prompt
    print("PROMPT:")
    print(prompt)

    # Create a test function using the LLMTestGenerator
    test, test_name = llm_generator.create_test_function(prompt)

    print("Tests produced by LLM:")
    print(test)

    # Define the filename for the generated test file
    filename = "test_generated.py"

    # Write the test function to the file
    llm_generator.write_test_to_file(test, filename=filename)

    # Get the module name and function name from the filename
    module_name = filename.split(".")[0]
    function_name = test_name

    # Import the module dynamically
    module = importlib.import_module(module_name)

    # Get the function from the module
    function = getattr(module, function_name)


    executor2 = AbstractExecutor(function)

    # Execute the input function and get the coverage date
    coverage_data = executor2._execute_input(function_to_test)

    # Print the coverage date
    print("Coverage data:")
    print(coverage_data)
