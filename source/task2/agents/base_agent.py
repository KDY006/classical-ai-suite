"""Base agent interface, telemetry metrics, and external student bot plugin loader."""

from __future__ import annotations

import abc
import importlib.util
import inspect
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List, Optional

from ..config import ALL_ACTIONS, STAY
from ..engine.game_state import GameState


@dataclass
class SearchMetrics:
    """Performance telemetry collected during a single move decision."""

    explored_states: int = 0
    elapsed_ms: float = 0.0
    depth_reached: int = 0
    pruned_branches: int = 0
    tt_hits: int = 0
    best_value: float = 0.0
    chosen_action: str = STAY


class BaseTankAgent(abc.ABC):
    """Abstract base class for all internal and external Tank Battle controllers."""

    def __init__(self, name: str) -> None:
        self.name: str = name
        self.last_metrics: SearchMetrics = SearchMetrics()

    @abc.abstractmethod
    def choose_action(self, state: GameState) -> str:
        """Select one action from ``ALL_ACTIONS`` for ``state.current_player``."""

    def safe_choose_action(self, state: GameState) -> str:
        """Invoke ``choose_action`` on a defensive clone so state cannot be mutated."""
        state_copy = state.clone()
        t0 = time.perf_counter()
        try:
            action = self.choose_action(state_copy)
        except Exception:
            action = STAY
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        if action not in ALL_ACTIONS:
            action = STAY
        if self.last_metrics.elapsed_ms <= 0.0:
            self.last_metrics.elapsed_ms = elapsed_ms
        self.last_metrics.chosen_action = action
        return action


class DictAdapterTankAgent(BaseTankAgent):
    """Wraps a standalone ``get_action(obs_dict)`` function from another student group."""

    def __init__(self, name: str, fn: Callable[[dict], str]) -> None:
        super().__init__(name=name)
        self._fn = fn

    def choose_action(self, state: GameState) -> str:
        t0 = time.perf_counter()
        obs = state.to_observation_dict()
        action = self._fn(obs)
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        self.last_metrics = SearchMetrics(
            explored_states=1,
            elapsed_ms=elapsed_ms,
            depth_reached=1,
            chosen_action=action if action in ALL_ACTIONS else STAY,
        )
        return self.last_metrics.chosen_action


def discover_external_agents(directory: Optional[Path] = None) -> List[BaseTankAgent]:
    """Dynamically load external bot implementations from ``external_agents/*.py``.

    Supports two integration protocols for seamless inter-group competitions:
      1. Subclassing ``BaseTankAgent`` with a zero-argument constructor.
      2. Exposing a module-level ``get_action(obs_dict: dict) -> str`` function
         (optional ``BOT_NAME: str`` attribute for display).
    """
    ext_dir = directory or (Path(__file__).resolve().parent / "external_agents")
    if not ext_dir.exists():
        return []

    loaded_agents: List[BaseTankAgent] = []
    for py_file in sorted(ext_dir.glob("*.py")):
        if py_file.name.startswith("_"):
            continue
        module_name = f"external_bot_{py_file.stem}"
        try:
            spec = importlib.util.spec_from_file_location(module_name, py_file)
            if spec is None or spec.loader is None:
                continue
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            found_subclass = False
            for _, obj in inspect.getmembers(module, inspect.isclass):
                if (
                    issubclass(obj, BaseTankAgent)
                    and obj is not BaseTankAgent
                    and obj is not DictAdapterTankAgent
                ):
                    instance = obj()
                    loaded_agents.append(instance)
                    found_subclass = True

            if not found_subclass and hasattr(module, "get_action") and callable(module.get_action):
                bot_label = getattr(module, "BOT_NAME", f"Ext:{py_file.stem}")
                loaded_agents.append(DictAdapterTankAgent(str(bot_label), module.get_action))
        except Exception:
            continue

    return loaded_agents
