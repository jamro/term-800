import openai
import json
import tiktoken
from .ConvoHistory import ConvoHistory


def count_tokens(text, model):
    encoding = tiktoken.encoding_for_model(model)
    tokens = len(encoding.encode(text))
    return tokens


class Conversation:

    def __init__(
        self, api_key, model_name="gpt-4o-mini", system_message="", token_stats=None
    ):
        self.api_key = api_key
        self.model_name = model_name
        self.history = ConvoHistory()
        self.functions = []
        self.token_stats = token_stats or {}
        self.history.set_system_message(system_message)

    def add_function(self, name, description, logic, parameters={}):
        self.functions.append(
            {
                "name": name,
                "description": description,
                "parameters": parameters,
                "logic": logic,
            }
        )

    def get_models(self):
        client = openai.OpenAI(api_key=self.api_key)
        response = client.models.list()

        result = []
        for model in response.data:
            result.append(model.id)

        return result

    def ask(
        self,
        query,
        model_name=None,
        on_data_callback=None,
        recurence_limit=25,
    ):
        model_name = model_name or self.model_name

        if recurence_limit <= 0:
            return "Recurence limit reached"

        client = openai.OpenAI(api_key=self.api_key)

        if model_name not in self.token_stats:
            self.token_stats[model_name] = {}
        if "input_tokens" not in self.token_stats[model_name]:
            self.token_stats[model_name]["input_tokens"] = 0
        if "output_tokens" not in self.token_stats[model_name]:
            self.token_stats[model_name]["output_tokens"] = 0

        if query:
            self.history.append_message("user", query)

        functions_def = [
            {k: v for k, v in func.items() if k != "logic"} for func in self.functions
        ]
        response = client.chat.completions.create(
            model=model_name,
            messages=self.history.get_items(),
            functions=functions_def if self.functions else None,
            stream=True,
        )

        input_tokens = 0
        output_tokens = 0
        function_call_accumulator = None
        function_name = None
        function_args = ""
        response_all = ""

        input_tokens += count_tokens(self.history.dump(), model_name)
        if self.functions:
            input_tokens += count_tokens(json.dumps(functions_def), model_name)

        for chunk in response:
            if len(chunk.choices) == 0 or chunk.choices[0].delta is None:
                continue

            delta = chunk.choices[0].delta

            if delta.content is not None:
                if on_data_callback:
                    on_data_callback(delta.content)
                response_all += delta.content

            # Handle function call
            if delta.function_call is not None:
                if function_call_accumulator is None:
                    function_call_accumulator = True
                    function_name = delta.function_call.name

                function_args += delta.function_call.arguments

        if function_call_accumulator:
            function_args_json = json.loads(function_args)
            matching_function = next(
                (func for func in self.functions if func["name"] == function_name), None
            )

            if matching_function:
                function_response = matching_function["logic"](**function_args_json)

                if response_all:
                    self.history.append_message("assistant", response_all)

                self.history.append_message(
                    "function", function_response, {"name": function_name}
                )

                # Count output tokens
                output_tokens += count_tokens(response_all, model_name)
                output_tokens += count_tokens(function_args, model_name)
                self.token_stats[model_name]["input_tokens"] += input_tokens
                self.token_stats[model_name]["output_tokens"] += output_tokens

                return self.ask(
                    None,
                    model_name,
                    on_data_callback,
                    recurence_limit=recurence_limit - 1,
                )

        self.history.append_message("assistant", response_all)

        # Count output tokens
        output_tokens += count_tokens(response_all, model_name)
        output_tokens += count_tokens(function_args, model_name)
        self.token_stats[model_name]["input_tokens"] += input_tokens
        self.token_stats[model_name]["output_tokens"] += output_tokens

        return response_all
