"""Lop co so OOP cho tac tu xe tang, thong so tim kiem va nap dong bot ngoai."""

from __future__ import annotations

import abc
import importlib.util
import inspect
import time
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

from ..config import ALL_ACTIONS, STAY
from ..engine.game_state import GameState


def to_ascii_label(text: str) -> str:
    """Chuyen chuoi tieng Viet co dau sang khong dau ASCII an toan cho CLI."""
    replaced = text.replace("đ", "d").replace("Đ", "D")
    normalized = unicodedata.normalize("NFD", replaced)
    return "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn").encode(
        "ascii", "ignore"
    ).decode("ascii")


@dataclass(slots=True)
class SearchMetrics:
    """Thong so do luong hieu nang sau moi luot ra quyet dinh cua tac tu."""

    explored_states: int = 0
    elapsed_ms: float = 0.0
    depth_reached: int = 0
    pruned_branches: int = 0
    tt_hits: int = 0
    best_value: float = 0.0
    chosen_action: str = STAY


class BaseTankAgent(abc.ABC):
    """Giao dien OOP dung chung cho moi tac tu noi bo va bot cua nhom khac."""

    def __init__(self, name: str, cli_name: Optional[str] = None) -> None:
        self.name: str = name
        self.cli_name: str = cli_name if cli_name is not None else to_ascii_label(name)
        self.last_metrics: SearchMetrics = SearchMetrics()

    @abc.abstractmethod
    def choose_action(self, state: GameState) -> str:
        """Chon mot hanh dong thuoc ALL_ACTIONS cho state.current_player."""

    @staticmethod
    def _terminal_value(state: GameState, root_player: int, depth: int) -> float:
        """Gia tri ket thuc tong bang khong, uu tien thang som va keo dai khi thua."""
        value = state.utility(root_player)
        if value > 0:
            return value - 0.01 * depth
        if value < 0:
            return value + 0.01 * depth
        return value

    def safe_choose_action(self, state: GameState) -> str:
        """Chay tac tu tren ban chup bat bien, chan ngoai le va hanh dong sai."""
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
    """Bo chuyen doi cho bot nhom ngoai viet dang ham doc lap get_action(obs)."""

    def __init__(
        self,
        name: str,
        function: Callable[[dict], str],
        cli_name: Optional[str] = None,
    ) -> None:
        super().__init__(name=name, cli_name=cli_name)
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
    """Quet va nap dong cac bot nhom ngoai chuan OOP hoac chuan Dict trong external_agents/."""
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
                    label = str(getattr(module, "BOT_NAME", f"Bot ngoai: {py_file.stem}"))
                    cli_label = getattr(module, "BOT_CLI_NAME", None)
                    agents.append(
                        DictAdapterTankAgent(
                            name=label,
                            function=function,
                            cli_name=str(cli_label) if cli_label is not None else None,
                        )
                    )
        except Exception:
            continue
    return agents
