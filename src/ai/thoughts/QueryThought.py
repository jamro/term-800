from src.ai.ThoughtNode import ThoughtNode


class QueryThought(ThoughtNode):

    def __init__(
        self,
        assistant,
        post_exec_prompt,
        model_name="gpt-4o-mini",
        on_data_callback=None,
    ):
        self.post_exec_prompt = post_exec_prompt
        self.assistant = assistant
        self.model_name = model_name
        self.on_data_callback = on_data_callback
        super().__init__(thought=None)

    def _think(self, input):
        query = input["query"]
        response = self.assistant.ask(
            query, model_name=self.model_name, on_data_callback=self.on_data_callback
        )
        self.assistant.history.clean_text(self.post_exec_prompt)
        return {
            "response": response,
            **input,
        }
