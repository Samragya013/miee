"""Command Router — routes CLI commands to application handlers.

The command router provides a clean mapping between CLI command names
and their handler functions. It centralizes command registration,
validation, and dispatch.

Commands are grouped by domain:
- analyze: Full pipeline analysis
- benchmark: Benchmark execution
- validate: Artifact validation
- inspect: System inspection
- report: Report generation
- config: Configuration management
- system: System information
- help: Help and documentation
"""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional


class CommandDomain(enum.Enum):
    """Command domain categories."""

    ANALYZE = "analyze"
    BENCHMARK = "benchmark"
    VALIDATE = "validate"
    INSPECT = "inspect"
    REPORT = "report"
    CONFIG = "config"
    SYSTEM = "system"
    HELP = "help"


@dataclass
class Command:
    """A registered command definition.

    Attributes:
        name: CLI command name (e.g., 'analyze', 'detect').
        domain: The command domain.
        description: Human-readable description.
        handler: Callable that executes the command logic.
        hidden: If True, not shown in help output.
    """

    name: str
    domain: CommandDomain
    description: str
    handler: Callable[..., Any]
    hidden: bool = False


@dataclass
class CommandRegistry:
    """Registry of all available commands."""

    commands: Dict[str, Command] = field(default_factory=dict)

    def register(self, command: Command) -> None:
        self.commands[command.name] = command

    def get(self, name: str) -> Optional[Command]:
        return self.commands.get(name)

    def list_commands(self, include_hidden: bool = False) -> List[Command]:
        cmds = list(self.commands.values())
        if not include_hidden:
            cmds = [c for c in cmds if not c.hidden]
        return sorted(cmds, key=lambda c: (c.domain.value, c.name))

    def list_by_domain(self, include_hidden: bool = False) -> Dict[str, List[Command]]:
        result: Dict[str, List[Command]] = {}
        for cmd in self.list_commands(include_hidden):
            domain = cmd.domain.value
            if domain not in result:
                result[domain] = []
            result[domain].append(cmd)
        return result


class CommandRouter:
    """Routes CLI commands to application handlers.

    The router is the single point of entry for command dispatch.
    It validates inputs, records session history, and delegates
    execution to the appropriate handler.

    The router contains NO scientific logic — it is a pure
    dispatch mechanism.
    """

    def __init__(self) -> None:
        self._registry = CommandRegistry()

    @property
    def registry(self) -> CommandRegistry:
        return self._registry

    def register(self, command: Command) -> None:
        """Register a command."""
        self._registry.register(command)

    def dispatch(self, command_name: str, **kwargs: Any) -> Any:
        """Dispatch a command by name with the given arguments.

        Raises KeyError if the command is not registered.
        """
        cmd = self._registry.get(command_name)
        if cmd is None:
            raise KeyError(f"Unknown command: {command_name}")
        return cmd.handler(**kwargs)

    def has_command(self, name: str) -> bool:
        """Check if a command is registered."""
        return self._registry.get(name) is not None

    def get_help_text(self) -> str:
        """Generate help text for all registered commands."""
        lines = ["Available commands:", ""]
        by_domain = self._registry.list_by_domain()
        for domain, commands in by_domain.items():
            lines.append(f"  {domain.upper()}")
            for cmd in commands:
                lines.append(f"    {cmd.name:<16} {cmd.description}")
            lines.append("")
        return "\n".join(lines)
