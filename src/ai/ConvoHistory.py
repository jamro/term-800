import json


class ConvoHistory:
    def __init__(self):
        self._system_block = {
            "role": "system",
            "content": "",
        }
        self._items = [self._system_block]

    def set_system_message(self, message):
        self._system_block["content"] = message

    def get_system_message(self):
        return self._system_block["content"]

    def get_items(self):
        return self._items

    def append_message(self, role, content, others={}):
        self._items.append({"role": role, "content": content, **others})

    def dump(self):
        return json.dumps(self._items)

    def clean_text(self, text):
        for item in self._items[1:]:
            item["content"] = item["content"].replace(text, "")

    def clean_transformed(self, func):
        for item in self._items[1:]:
            item["content"] = func(item["content"])

    def clear(self):
        self._items = [self._system_block]
