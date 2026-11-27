"""Agent interfaces, telemetry, and external bot discovery."""

from __future__ import annotations

import abc
import importlib.util
import inspect
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

from ..config import ALL_ACTIONS, STAY
from ..engine.game_state import GameState


@dataclass(slots=True)
class SearchMetrics:
    explored_states: int = 0
    elapsed_ms: float = 0.0
    depth_reached: int = 0
    pruned_branches: int = 0
    tt_hits: int = 0
    best_value: float = 0.0
    chosen_action: str = STAY


class BaseTankAgent(abc.ABC):
    """Common interface for internal and external Tank Battle controllers."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.last_metrics = SearchMetrics()

    @abc.abstractmethod
    def choose_action(self, state: GameState) -> str:
        """Choose one of ALL_ACTIONS for state.current_player."""

    @staticmethod
    def _terminal_value(state: GameState, root_player: int, depth: int) -> float:
        """Return zero-sum terminal payoff with slight depth discount preferring faster wins."""
        value = state.utility(root_player)
        if value > 0:
            return value - 0.01 * depth
        if value < 0:
            return value + 0.01 * depth
        return value

    def safe_choose_action(self, state: GameState) -> str:
        """Run the bot against an immutable defensive snapshot."""
        protected_state = state.clone()
        started = time.perf_counter()
        try:
            action = self.choose_action(protected_state)
        except Exception:
            action = STAY
        elapsed_ms = (time.perf_counter() - started) * 1000.0

        if action not in ALL_ACTIONS:
            action = STAY
        self.last_metrics.elapsed_ms = (
            elapsed_ms
            if self.last_metrics.elapsed_ms == 0.0
            else max(self.last_metrics.elapsed_ms, elapsed_ms)
        )
        self.last_metrics.chosen_action = action
        return action


class DictAdapterTankAgent(BaseTankAgent):
    """Adapter for a standalone get_action(obs_dict) bot."""

    def __init__(self, name: str, function: Callable[[dict], str]) -> None:
        super().__init__(name=name)
        self._function = function

    def choose_action(self, state: GameState) -> str:
        started = time.perf_counter()
        observation = state.to_observation_dict()
        returned = self._function(observation)
        elapsed_ms = (time.perf_counter() - started) * 1000.0
        action = returned if returned in ALL_ACTIONS else STAY
        self.last_metrics = SearchMetrics(
            explored_states=1,
            elapsed_ms=elapsed_ms,
            depth_reached=1,
            best_value=0.0,
            chosen_action=action,
        )
        return action


def discover_external_agents(directory: Optional[Path] = None) -> list[BaseTankAgent]:
    """Discover OOP and dict-protocol bots in external_agents/*.py."""
    plugin_dir = directory or (Path(__file__).resolve().parent / "external_agents")
    if not plugin_dir.exists():
        return []

    agents: list[BaseTankAgent] = []
    for py_file in sorted(plugin_dir.glob("*.py")):
        if py_file.name.startswith("_"):
            continue
        try:
            spec = importlib.util.spec_from_file_location(
                f"external_bot_{py_file.stem}",
                py_file,
            )
            if spec is None or spec.loader is None:
                continue
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            oop_found = False
            for _, candidate in inspect.getmembers(module, inspect.isclass):
                try:
                    is_agent = (
                        issubclass(candidate, BaseTankAgent)
                        and candidate is not BaseTankAgent
                        and candidate is not DictAdapterTankAgent
                    )
                except TypeError:
                    is_agent = False
                if not is_agent:
                    continue
                try:
                    agents.append(candidate())
                    oop_found = True
                except Exception:
                    continue

            if not oop_found:
                function = getattr(module, "get_action", None)
                if callable(function):
                    label = getattr(module, "BOT_NAME", f"Ext:{py_file.stem}")
                    agents.append(DictAdapterTankAgent(str(label), function))
        except Exception:
            continue
    return agents
