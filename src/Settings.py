import json


class Settings:
    def __init__(self, config_file="term800_config.json"):
        self.config_file = config_file
        self._config = self.load_config()

    def load_config(self):
        try:
            with open(self.config_file, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return {"llm_model": "gpt-4o-mini", "host:": "skynet.local", "user": "lab"}

    def save_config(self):
        with open(self.config_file, "w") as file:
            json.dump(self._config, file, indent=4)

    def get(self, key):
        return self._config.get(key)

    def set(self, key, value):
        self._config[key] = value
        self.save_config()
