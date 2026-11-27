"""Lop truu tuong chung cho cac bo giai bai toan N Quan Hau."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseNQueenSolver(ABC):
    """Giao dien OOP thong nhat cho bo giai SAT va tim kiem cuc bo."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Ten hien thi co dau cho giao dien do hoa va bieu do."""

    @property
    @abstractmethod
    def cli_name(self) -> str:
        """Ten hien thi khong dau cho cua so dong lenh terminal."""

    @abstractmethod
    def solve(self, n: int) -> Any:
        """Tim loi giai cho ban co kich thuoc n x n."""
