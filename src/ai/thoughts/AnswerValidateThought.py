from src.ai.ThoughtNode import ThoughtNode

class AnswerValidateThought(ThoughtNode):

    def __init__(self, assistant, model_name='gpt-4o-mini'):
        self.assistant = assistant
        self.model_name = model_name
        super().__init__(thought=None)

    def _think(self, input):
        query = input["query"]
        validation_prompt = f"""
          The main prompt was: '{query}'. 
          Was it successfully completed or answered? Are there any next steps or follow-up actions required?
          Answer with:
          - 'YES' if the task was successfully completed or answered.
          - 'NO' if the task was not completed or answered.
          - 'NEXT' if more information is needed to complete the task.
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