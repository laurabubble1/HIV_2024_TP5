
import typing
import inspect

class LLMTestGenerator():
    """Generator for the LLM test suite."""

    def __init__(self, client, model_name: str, function: typing.Callable):
        self._name = "LLMTestGenerator"
        self.client = client
        self.model_name = model_name
        self._func_name = function.__name__

    def generate_assertions(self, prompt: str) -> str:
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
        )
        return response.text or ""

    def parse_assertions(self, generated_text):
        lines = generated_text.split("\n")
        assertions = [line.strip() for line in lines if line.strip().startswith("assert")]
        return assertions

    def create_test_function(self, code_snippet):
        function_name = self._func_name
        generated_text = self.generate_assertions(code_snippet)
        assertions = self.parse_assertions(generated_text)

        if not assertions:
            formatted_assertions = "assert False, 'No assertions generated'"
        else:
            formatted_assertions = "\n    ".join(assertions)

        test_function_code = (
            f"def test_{function_name}({function_name}):\n    {formatted_assertions}\n"
        )
        return test_function_code, f"test_{function_name}"

    def write_test_to_file(self, test_function_code, filename="test_generated.py"):
        with open(filename, "w") as file:
            file.write(test_function_code)
        print(f"Test function written to {filename}")