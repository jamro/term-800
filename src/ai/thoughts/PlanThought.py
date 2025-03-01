from src.ai.ThoughtNode import ThoughtNode

class PlanThought(ThoughtNode):

    def __init__(self, assistant, model_name='gpt-4o-mini', on_data_callback=None):
        self.assistant = assistant
        self.model_name = model_name
        self.on_data_callback = on_data_callback
        super().__init__(thought=None)

    def _think(self, input):
        query = input["query"]

        plan_prompt = f"""
        Prepare a plan for prompt: '{query}'.
          - Define goal of the plan
          - List of steps to achieve the goal
          - Expected outcome of each step
          - The plan must include collecting neccessary information from the host, executing commands and verifying the output.

          EXAMPLE
          Goal of the Plan:
          Install a LAMP (Linux, Apache, MySQL, PHP) stack on the system.

          Steps to Achieve the Goal:

          1. Update Package Index
            - Expected Outcome: Ensure the local package index is up-to-date.

          2. ...

          3. ...

          ...

          Collecting Necessary Information from the Host:
          - Check the current system OS and version.
          - Check current installed packages to avoid redundancy.
          - Verify current service statuses to ensure clean installations. 
        """

        self.assistant.ask(
            plan_prompt,
            model_name=self.model_name,
            on_data_callback=self.on_data_callback,
        )
        if self.on_data_callback:
            self.on_data_callback("\n")
            
        self.assistant.history.clean_text(plan_prompt)

        return input