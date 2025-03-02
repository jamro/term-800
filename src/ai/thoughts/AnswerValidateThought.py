from src.ai.ThoughtNode import ThoughtNode


class AnswerValidateThought(ThoughtNode):

    def __init__(self, assistant, model_name="gpt-4o-mini"):
        self.assistant = assistant
        self.model_name = model_name
        super().__init__(thought=None)

    def _think(self, input):
        query = input["query"]
        validation_prompt = f"""
          The main prompt was: '{query}'.
          Review the information above and determine whether the task require any further steps or actions.

          Answer with:
            -	'DONE' if the task was successfully completed, fully answered, failed without further steps.
            -	'NEXT' if more information or further action is required and operation was NOT aborted by user.

          Do not provide any additional information.
        """

        validation_response = self.assistant.ask(
            validation_prompt,
            model_name=self.model_name,
        )
        self.assistant.history.undo(2)

        if validation_response == "NEXT":
            query = "continue"

        return {
            **input,
            "next_node": validation_response,
            "query": query,
        }
