import random
import ast
import copy
from parser import extract_seed_input
from common.abstract_executor import AbstractExecutor

class FuzzingGenerator:
    def __init__(self, function_to_test, test_code, initial_coverage, executor):
        self.function_to_test = function_to_test
        self.target_name = getattr(function_to_test, "__name__", "")
        self.test_code = test_code
        self._name = "FuzzingGenerator"
        self.initial_coverage = initial_coverage
        self.executor = executor
        self.operator_scores = {"insert": 1.0, "delete": 1.0, "substitute": 1.0}
        try:
            input_data = extract_seed_input(test_code)
        except ValueError as e:
            print(f"Error extracting seed input: {e}")
            input_data = None
        self.seed_input = input_data

    def _safe_literal_eval(self, value):
        if value is None:
            return None
        if not isinstance(value, str):
            return value
        try:
            return ast.literal_eval(value)
        except (ValueError, SyntaxError):
            return value

    def _seed_pool(self):
        parsed_seed = self._safe_literal_eval(self.seed_input)
        if parsed_seed is None:
            return []
        if isinstance(parsed_seed, list):
            return parsed_seed.copy()
        return [parsed_seed]

    def _coverage_metrics(self, coverage_data):
        coverage = coverage_data.get("coverage", {})
        line_coverage = coverage.get("percent_covered", 0.0) / 100.0
        num_branches = coverage.get("num_branches", 0)
        covered_branches = coverage.get("covered_branches", 0)
        branch_coverage = (covered_branches / num_branches) if num_branches else 0.0
        return line_coverage, branch_coverage

    def evaluate_fitness(self, input_list, alpha=1.0, beta=1.0, gamma=0.05):
        coverage_data = self.executor._execute_input(input_list=input_list)
        line_coverage, branch_coverage = self._coverage_metrics(coverage_data)
        ntests = len(input_list)
        fitness = (alpha * line_coverage) + (beta * branch_coverage) - (gamma * ntests)
        return fitness, coverage_data

    def _random_number_input(self):
        edge_values = [0, 1, 9, 10, 11, 19, 20, 21, 99, 100, 101, 999, 1000, 1001, 999999]
        if random.random() < 0.7:
            return random.choice(edge_values)
        return random.randint(0, 1_000_000)

    def _random_password_input(self):
        alphabet = "abcdefghijklmnopqrstuvwxyz"
        ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        digits = "0123456789"
        specials = "!@#$%^&*()-_=+[]{}"
        charset = alphabet + ALPHABET + digits + specials
        length = random.randint(0, 28)
        return "".join(random.choice(charset) for _ in range(length))

    def _choose_mutation_operator(self):
        operators = ["insert", "delete", "substitute"]
        weights = [max(self.operator_scores[op], 0.1) for op in operators]
        return random.choices(operators, weights=weights, k=1)[0]

    def _update_operator_score(self, operator, fitness_delta):
        if fitness_delta > 0:
            self.operator_scores[operator] += fitness_delta + 0.05
        else:
            self.operator_scores[operator] = max(0.1, self.operator_scores[operator] * 0.98)

    def _normalize_input(self, input_data):
        if self.target_name == "number_to_words":
            try:
                value = int(input_data)
            except (TypeError, ValueError):
                value = self._random_number_input()
            return max(0, value)

        if self.target_name == "strong_password_checker":
            if input_data is None:
                return self._random_password_input()
            return str(input_data)

        return input_data


    def mutate_input(self, input_data):
        normalized = self._normalize_input(input_data)

        if self.target_name == "number_to_words":
            n = normalized
            mutation_type = random.choice(["delta", "scale", "edge"])

            if mutation_type == "delta":
                n = n + random.choice([-1000, -100, -10, -1, 1, 10, 100, 1000])
            elif mutation_type == "scale":
                n = n * random.choice([0, 1, 2, 10])
            else:
                n = self._random_number_input()

            return max(0, int(n))

        if self.target_name == "strong_password_checker":
            s = normalized
            if s == "":
                s = self._random_password_input()

            alphabet = "abcdefghijklmnopqrstuvwxyz"
            ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            digits = "0123456789"
            specials = "!@#$%^&*()-_=+[]{}"
            charset = alphabet + ALPHABET + digits + specials

            mutation_type = random.choice(["insert", "delete", "substitute", "repeat", "length_jump"])
            idx = random.randint(0, max(0, len(s) - 1)) if s else 0

            if mutation_type == "insert":
                c = random.choice(charset)
                return s[:idx] + c + s[idx:]

            if mutation_type == "delete":
                if not s:
                    return ""
                return s[:idx] + s[idx + 1:]

            if mutation_type == "repeat":
                c = s[idx] if s else random.choice(charset)
                reps = random.randint(3, 6)
                return s[:idx] + (c * reps) + s[idx:]

            if mutation_type == "length_jump":
                return self._random_password_input()

            c = random.choice(charset)
            if not s:
                return c
            return s[:idx] + c + s[idx + 1:]

        return normalized
    
    def generate_new_inputs(self):
        initial_inputs = self._seed_pool()
        return self.mutate_list(initial_inputs)

    def _mutate_suite_once(self, input_list, mutation_type):
        if not input_list:
            pool = self._seed_pool()
            if pool:
                return [self._normalize_input(random.choice(pool))]
            return [self.mutate_input(None)]

        mutated_list = copy.deepcopy(input_list)

        if mutation_type == "insert":
            index = random.randint(0, len(mutated_list))
            source = random.choice(mutated_list)
            new_input = self.mutate_input(source)
            mutated_list.insert(index, new_input)
        elif mutation_type == "delete":
            if len(mutated_list) > 1:
                index = random.randrange(len(mutated_list))
                mutated_list.pop(index)
            else:
                mutated_list[0] = self.mutate_input(mutated_list[0])
        else:  # substitute
            index = random.randrange(len(mutated_list))
            mutated_list[index] = self.mutate_input(mutated_list[index])

        return mutated_list
    
    def mutate_list(self, input_list, alpha=1.0, beta=1.0, gamma=0.05, budget=100):
        best_inputs = copy.deepcopy(input_list) if input_list is not None else []

        if not best_inputs:
            best_inputs = self._seed_pool()
        if not best_inputs:
            best_inputs = [self.mutate_input(None)]

        best_inputs = [self._normalize_input(x) for x in best_inputs]

        best_fitness, _ = self.evaluate_fitness(best_inputs, alpha=alpha, beta=beta, gamma=gamma)

        for _ in range(budget):
            mutation_type = self._choose_mutation_operator()
            candidate_inputs = self._mutate_suite_once(best_inputs, mutation_type)
            candidate_fitness, _ = self.evaluate_fitness(candidate_inputs, alpha=alpha, beta=beta, gamma=gamma)
            delta = candidate_fitness - best_fitness

            self._update_operator_score(mutation_type, delta)

            if delta > 0:
                best_fitness = candidate_fitness
                best_inputs = candidate_inputs

        return best_inputs