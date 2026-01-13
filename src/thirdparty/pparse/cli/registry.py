from importlib.metadata import entry_points
from typing import Callable, Dict

CommandRegistrar = Callable[[object], None]

_COMMANDS: Dict[str, CommandRegistrar] = {}

def register_command(name: str, registrar: CommandRegistrar):
    if name in _COMMANDS and _COMMANDS[name] != registrar:
        raise ValueError(f"Command '{name}' already registered")
    _COMMANDS[name] = registrar

def get_commands():
    return _COMMANDS.values()

def load_entrypoint_plugins(entrypoint_group):

    if isinstance(entry_points(), dict):
        # Python 3.9
        eps = []
        for ep in entry_points()['pparse_command']:
            if not ep in eps:
                eps.append(ep)
    else:
        # Python 3.10+
        eps = entry_points(group=entrypoint_group)

    for ep in eps:
        register_command(ep.name, ep.load())
