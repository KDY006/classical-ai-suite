"""Mo hinh hoa Logic menh de va chuyen doi rang buoc N Quan Hau sang CNF."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations


class PropositionalVariableMapper:
    """Anh xa song anh giua o ban co (row, col) va bien logic DIMACS 1..N^2."""

    def __init__(self, n: int) -> None:
        if n < 1:
            raise ValueError("Kich thuoc ban co phai la so nguyen duong")
        self.n: int = n
        self.num_variables: int = n * n

    def to_var(self, row: int, col: int) -> int:
        """Chuyen toa do (row, col) sang chi so bien nguyen duong DIMACS."""
        if not (0 <= row < self.n and 0 <= col < self.n):
            raise ValueError("Toa do o nam ngoai pham vi ban co")
        return row * self.n + col + 1

    def to_coord(self, variable: int) -> tuple[int, int]:
        """Chuyen bien DIMACS (hoac literal am) ve toa do (row, col)."""
        if not 1 <= abs(variable) <= self.num_variables:
            raise ValueError("Chi so bien nam ngoai pham vi ban co")
        return divmod(abs(variable) - 1, self.n)

    def to_symbol(self, row: int, col: int) -> str:
        """Tra ve ky hieu bien logic dang chuoi P(row,col)."""
        if not (0 <= row < self.n and 0 <= col < self.n):
            raise ValueError("Toa do o nam ngoai pham vi ban co")
        return f"P({row},{col})"


@dataclass(frozen=True)
class PropositionalRule:
    """Mo ta tung buoc chuyen doi mot rang buoc tu Logic menh de sang CNF."""

    category: str
    logical_expr: str
    cnf_expr: str
    dimacs_clause: tuple[int, ...]


@dataclass(frozen=True)
class CNFEncodingStats:
    """Thong ke chi tiet so luong bien va menh de CNF theo tung nhom rang buoc."""

    n: int
    num_variables: int
    row_alo_clauses: int
    col_alo_clauses: int
    row_amo_clauses: int
    col_amo_clauses: int
    main_diag_amo_clauses: int
    anti_diag_amo_clauses: int

    @property
    def diag_amo_clauses(self) -> int:
        """Tong so menh de khong tan cong tren ca hai he duong cheo."""
        return self.main_diag_amo_clauses + self.anti_diag_amo_clauses

    @property
    def total_clauses(self) -> int:
        """Tong so menh de CNF sinh ra cho toan ban co."""
        return (
            self.row_alo_clauses
            + self.col_alo_clauses
            + self.row_amo_clauses
            + self.col_amo_clauses
            + self.main_diag_amo_clauses
            + self.anti_diag_amo_clauses
        )


class NQueenCNFEncoder:
    """Phat hien rang buoc ban co N-Queen va chuyen doi sang dang chuan hoi CNF."""

    def __init__(self, n: int, include_col_alo: bool = True) -> None:
        self.mapper = PropositionalVariableMapper(n)
        self.n: int = n
        self.include_col_alo: bool = include_col_alo

    def discover_constraint_groups(self) -> dict[str, list[list[tuple[int, int]]]]:
        """Thuat toan O(N^2) phat hien 4 ho nhom tuyen tinh chi phoi quan hau."""
        n = self.n
        rows = [[(r, c) for c in range(n)] for r in range(n)]
        columns = [[(r, c) for r in range(n)] for c in range(n)]

        main_diags: dict[int, list[tuple[int, int]]] = {}
        anti_diags: dict[int, list[tuple[int, int]]] = {}
        for r in range(n):
            for c in range(n):
                main_diags.setdefault(r - c, []).append((r, c))
                anti_diags.setdefault(r + c, []).append((r, c))

        return {
            "rows": rows,
            "columns": columns,
            "main_diagonals": [cells for cells in main_diags.values() if len(cells) >= 2],
            "anti_diagonals": [cells for cells in anti_diags.values() if len(cells) >= 2],
        }

    def explain_cnf_conversion(self, sample_limit: int = 2) -> list[PropositionalRule]:
        """Minh hoa tuong minh quy trinh chuyen doi rang buoc sang CNF va DIMACS."""
        if sample_limit < 1:
            raise ValueError("So luong vi du minh hoa phai lon hon hoac bang 1")

        groups = self.discover_constraint_groups()
        mapper = self.mapper
        rules: list[PropositionalRule] = []

        # 1. Rang buoc ton tai it nhat mot quan hau tren moi hang (ALO)
        for row_cells in groups["rows"][:sample_limit]:
            expr = " v ".join(mapper.to_symbol(r, c) for r, c in row_cells)
            clause = tuple(mapper.to_var(r, c) for r, c in row_cells)
            rules.append(PropositionalRule("Ton tai theo hang (ALO)", expr, expr, clause))

        # 2. Rang buoc ton tai it nhat mot quan hau tren moi cot (ALO, tuy chon)
        if self.include_col_alo:
            for col_cells in groups["columns"][:sample_limit]:
                expr = " v ".join(mapper.to_symbol(r, c) for r, c in col_cells)
                clause = tuple(mapper.to_var(r, c) for r, c in col_cells)
                rules.append(PropositionalRule("Ton tai theo cot (ALO)", expr, expr, clause))

        # 3. Rang buoc khong tan cong theo cap (AMO): P(a) => ~P(b) equiv ~P(a) v ~P(b)
        amo_specs = (
            ("Khong tan cong cung hang (AMO)", groups["rows"]),
            ("Khong tan cong cung cot (AMO)", groups["columns"]),
            ("Khong tan cong cheo chinh (AMO)", groups["main_diagonals"]),
            ("Khong tan cong cheo phu (AMO)", groups["anti_diagonals"]),
        )
        for category, cell_groups in amo_specs:
            added = 0
            for cell_group in cell_groups:
                for (r1, c1), (r2, c2) in combinations(cell_group, 2):
                    s1 = mapper.to_symbol(r1, c1)
                    s2 = mapper.to_symbol(r2, c2)
                    v1 = mapper.to_var(r1, c1)
                    v2 = mapper.to_var(r2, c2)
                    rules.append(
                        PropositionalRule(
                            category=category,
                            logical_expr=f"{s1} => ~{s2}",
                            cnf_expr=f"~{s1} v ~{s2}",
                            dimacs_clause=(-v1, -v2),
                        )
                    )
                    added += 1
                    if added >= sample_limit:
                        break
                if added >= sample_limit:
                    break

        return rules

    def encode(self) -> tuple[list[list[int]], CNFEncodingStats]:
        """Sinh toan bo danh sach menh de CNF dang DIMACS va thong ke chi tiet."""
        n = self.n
        groups = self.discover_constraint_groups()

        row_vars = [[r * n + c + 1 for r, c in grp] for grp in groups["rows"]]
        col_vars = [[r * n + c + 1 for r, c in grp] for grp in groups["columns"]]
        main_vars = [[r * n + c + 1 for r, c in grp] for grp in groups["main_diagonals"]]
        anti_vars = [[r * n + c + 1 for r, c in grp] for grp in groups["anti_diagonals"]]

        clauses: list[list[int]] = list(row_vars)
        row_alo = len(row_vars)

        col_alo = 0
        if self.include_col_alo:
            clauses.extend(col_vars)
            col_alo = len(col_vars)

        amo_counts: list[int] = []
        for var_groups in (row_vars, col_vars, main_vars, anti_vars):
            before = len(clauses)
            for grp in var_groups:
                clauses.extend([-first, -second] for first, second in combinations(grp, 2))
            amo_counts.append(len(clauses) - before)

        stats = CNFEncodingStats(
            n=n,
            num_variables=n * n,
            row_alo_clauses=row_alo,
            col_alo_clauses=col_alo,
            row_amo_clauses=amo_counts[0],
            col_amo_clauses=amo_counts[1],
            main_diag_amo_clauses=amo_counts[2],
            anti_diag_amo_clauses=amo_counts[3],
        )
        return clauses, stats

    def theoretical_clause_count(self) -> int:
        """Tinh chinh xac tong so menh de CNF theo cong thuc dong ly thuyet."""
        n = self.n
        alo_count = 2 * n if self.include_col_alo else n
        return alo_count + n * n * (n - 1) + n * (n - 1) * (2 * n - 1) // 3
