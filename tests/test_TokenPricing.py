from src.TokenPricing import TokenPricing


def test_get_model_pricing_no_model():
    token_pricing = TokenPricing()
    assert token_pricing.get_model_pricing("gpt-awesome-unkwnown") == None


def test_set_new_model_pricing():
    token_pricing = TokenPricing()
    token_pricing.set_model_pricing("gpt-awesome", 0.25, 1.25)
    assert token_pricing.get_model_pricing("gpt-awesome") == {
        "1M_input_tokens": 0.25,
        "1M_output_tokens": 1.25,
    }


def test_update_model_pricing():
    token_pricing = TokenPricing()
    token_pricing.set_model_pricing("gpt-awesome", 0.25, 1.25)
    token_pricing.set_model_pricing("gpt-awesome", 0.50, 2.50)
    assert token_pricing.get_model_pricing("gpt-awesome") == {
        "1M_input_tokens": 0.50,
        "1M_output_tokens": 2.50,
    }


def test_get_total_cost():
    token_pricing = TokenPricing()
    token_pricing.set_model_pricing("gpt-awesome-1", 0.25, 1.25)
    token_pricing.set_model_pricing("gpt-awesome-2", 0.50, 2.50)
    token_stats = {
        "gpt-awesome-1": {
            "input_tokens": 1 * 1000000,
            "output_tokens": 5 * 1000000,
        },
        "gpt-awesome-2": {
            "input_tokens": 2 * 1000000,
            "output_tokens": 1 * 1000000,
        },
    }
    assert (
        token_pricing.get_total_cost(token_stats)
        == 1 * 0.25 + 5 * 1.25 + 2 * 0.50 + 1 * 2.50
    )


def test_get_total_cost_no_pricing():
    token_pricing = TokenPricing()
    token_pricing.set_model_pricing("gpt-awesome-1", 0.25, 1.25)
    token_stats = {
        "gpt-awesome-1": {
            "input_tokens": 1 * 1000000,
            "output_tokens": 5 * 1000000,
        },
        "gpt-awesome-2": {
            "input_tokens": 2 * 1000000,
            "output_tokens": 1 * 1000000,
        },
    }
    assert token_pricing.get_total_cost(token_stats) == 1 * 0.25 + 5 * 1.25
