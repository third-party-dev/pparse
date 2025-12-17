from importlib.metadata import entry_points
from typing import Callable, Dict

CommandRegistrar = Callable[[object], None]

_COMMANDS: Dict[str, CommandRegistrar] = {}

def register_command(name: str, registrar: CommandRegistrar):
    if name in _COMMANDS:
        raise ValueError(f"Command '{name}' already registered")
    _COMMANDS[name] = registrar

def get_commands():
    return _COMMANDS.values()

def load_entrypoint_plugins(entrypoint_group):
    eps = entry_points(group=entrypoint_group)
    for ep in eps:
        register = ep.load()
        register_command(ep.name, register)