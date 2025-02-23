class TokenPricing:

    def __init__(self):
        self.pricing = {
            "gpt-4o": {
                "1M_input_tokens": 2.50,
                "1M_output_tokens": 10.00,
            },
            "gpt-4o-mini": {
                "1M_input_tokens": 0.150,
                "1M_output_tokens": 0.60,
            },
            "gpt-3.5-turbo": {
                "1M_input_tokens": 0.50,
                "1M_output_tokens": 1.50,
            },
        }

    def set_model_pricing(
        self, model, price_per_1M_input_tokens, price_per_1M_output_tokens
    ):
        if model not in self.pricing:
            self.pricing[model] = {}

        self.pricing[model]["1M_input_tokens"] = price_per_1M_input_tokens
        self.pricing[model]["1M_output_tokens"] = price_per_1M_output_tokens

    def get_model_pricing(self, model):
        if model not in self.pricing:
            return None
        return self.pricing[model]

    def get_total_cost(self, token_stats):
        cost = 0
        for model, stats in token_stats.items():
            if model not in self.pricing:
                print(
                    f"WARNING: No pricing data for model {model}. Skipping {stats['input_tokens'] + stats['output_tokens']} tokens."
                )
                continue
            cost += (
                stats["input_tokens"] * self.pricing[model]["1M_input_tokens"] / 1000000
            )
            cost += (
                stats["output_tokens"]
                * self.pricing[model]["1M_output_tokens"]
                / 1000000
            )
        return cost
