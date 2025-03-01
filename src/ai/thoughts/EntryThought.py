from src.ai.ThoughtNode import ThoughtNode

class EntryThought(ThoughtNode):
  
    def __init__(self):
        super().__init__(thought=None)

    def _think(self, input):
        prepare_plan = input["prepare_plan"]
        return {
            "next_node": "prepare_plan" if prepare_plan else "skip_plan",
            **input,
        }