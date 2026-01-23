# scope_channel.py

class ScopeChannel:
    def __init__(self, name: str, color: str, enabled: bool = True):
        self.name = name
        self.color = color
        self.enabled = enabled
        self.signal = None  # numpy array

    def set_signal(self, sig):
        self.signal = sig
