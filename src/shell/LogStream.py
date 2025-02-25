import io
from pyee import EventEmitter


class LogStream(io.StringIO):
    def __init__(self, command):
        super().__init__()
        self.command = command
        self.emitter = EventEmitter()

    def write(self, text):
        for line in text.splitlines():
            self.emitter.emit("log", line)

    def done(self):
        self.emitter.emit("complete")

    def on_log(self, handler):
        self.emitter.on("log", handler)

    def on_complete(self, handler):
        self.emitter.on("complete", handler)
