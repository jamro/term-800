from src.ai.ThoughtNode import ThoughtNode


class ComplexityThought(ThoughtNode):

    def __init__(self, assistant, model_name="gpt-4o-mini"):
        self.assistant = assistant
        self.model_name = model_name
        super().__init__(thought=None)

    def _think(self, input):
        query = input["query"]
        complexity_prompt = f"""
          The main prompt was: '{query}'.  
          Analyze the prompt and determine its complexity.
          Answer 'COMPLEX' if the prompt requires execution of multiple commands or complex logic.
          Answer 'SIMPLE' if the prompt can be completed with a single command or requires minimal logic.
        """

        complexity_response = self.assistant.ask(
            complexity_prompt, model_name=self.model_name
        )
        self.assistant.history.undo(2)

        return {
            "complexity": complexity_response,
            **input,
        }
