"""Editable draft; validation and solving use the same CSP model as preset boards."""
from copy import deepcopy
import json
import random
from pathlib import Path
from .csp_model import KakuroCSP


class BoardEditor:
    def __init__(self, csp):
        self.name = csp.name
        self.grid = deepcopy(csp.raw_grid)
        self.givens = dict(csp.givens)

    @property
    def rows(self):
        return len(self.grid)

    @property
    def cols(self):
        return len(self.grid[0])

    def run_cells(self, pos, direction):
        r, c = pos
        dr, dc = (0, 1) if direction == 'across' else (1, 0)
        r, c = r + dr, c + dc
        cells = []
        while r < self.rows and c < self.cols and self.grid[r][c] == 'W':
            cells.append((r, c))
            r, c = r + dr, c + dc
        return cells

    def synchronize_clues(self):
        # Keep existing sums where the direction survives. New runs receive a
        # feasible example sum, which is editable; this is not a uniqueness guarantee.
        for r in range(self.rows):
            for c in range(self.cols):
                old = self.grid[r][c]
                if old == 'W':
                    continue
                clues = {}
                for direction in ('across', 'down'):
                    cells = self.run_cells((r, c), direction)
                    if cells:
                        default = sum((rr + cc) % 9 + 1 for rr, cc in cells)
                        clues[direction] = old.get(direction, default) if isinstance(old, dict) else default
                self.grid[r][c] = clues or 'B'

    def set_cell_type(self, pos, white):
        r, c = pos
        if white and (r == 0 or c == 0):
            raise ValueError('The first row and column must contain black or clue cells.')
        if (self.grid[r][c] == 'W') == white:
            return
        self.grid[r][c] = 'W' if white else 'B'
        self.givens.pop(pos, None)
        self.synchronize_clues()

    def set_clue(self, pos, direction, value):
        if direction not in ('across', 'down') or not self.run_cells(pos, direction):
            raise ValueError('There is no white-cell run in this direction.')
        r, c = pos
        if self.grid[r][c] == 'W' or type(value) is not int or not 1 <= value <= 45:
            raise ValueError('A clue sum must be an integer from 1 to 45.')
        cell = self.grid[r][c]
        clues = dict(cell) if isinstance(cell, dict) else {}
        clues[direction] = value
        self.grid[r][c] = clues

    def set_given(self, pos, value):
        r, c = pos
        if self.grid[r][c] != 'W' or type(value) is not int or not 0 <= value <= 9:
            raise ValueError('White cells accept digits 1-9; use 0 to clear.')
        if value:
            self.givens[pos] = value
        else:
            self.givens.pop(pos, None)

    @classmethod
    def new(cls, size):
        if not 3 <= size <= 9:
            raise ValueError('Board size must be between 3 and 9.')
        grid = [['B' if r == 0 or c == 0 else 'W' for c in range(size)] for r in range(size)]
        for i in range(1, size):
            grid[0][i] = {'down': sum((r+i)%9+1 for r in range(1,size))}
            grid[i][0] = {'across': sum((i+c)%9+1 for c in range(1,size))}
        return cls(KakuroCSP(f'Custom Board {size}x{size}', grid))

    def bulk_rows(self):
        """One editable token per cell: #, 0, digit, or across/down."""
        return [' '.join(str(self.givens.get((r,c), 0)) if cell == 'W'
                         else f"{cell.get('across',0)}/{cell.get('down',0)}" if isinstance(cell,dict)
                         else '#' for c,cell in enumerate(row))
                for r,row in enumerate(self.grid)]

    def apply_bulk_rows(self, rows):
        """Atomically replace all cells and givens; reject malformed layouts."""
        if len(rows) != self.rows:
            raise ValueError(f'Expected {self.rows} rows.')
        grid, givens = [], {}
        for r,line in enumerate(rows):
            tokens = line.split()
            if len(tokens) != self.cols:
                raise ValueError(f'Row {r+1}: expected {self.cols} cells separated by spaces.')
            row = []
            for c, token in enumerate(tokens):
                if token == '#': row.append('B')
                elif token in '0123456789' and len(token) == 1:
                    row.append('W')
                    if token != '0': givens[r,c] = int(token)
                elif '/' in token:
                    parts = token.split('/')
                    if len(parts) != 2 or not all(x.isascii() and x.isdigit() and len(x)<=2 for x in parts):
                        raise ValueError(f'Cell ({r+1},{c+1}): use across/down, e.g. 17/0.')
                    a,d = map(int, parts)
                    if not (0 <= a <= 45 and 0 <= d <= 45):
                        raise ValueError(f'Cell ({r+1},{c+1}): clue must be 0-45.')
                    row.append({k:v for k,v in [('across',a),('down',d)] if v} or 'B')
                else:
                    raise ValueError(f'Cell ({r+1},{c+1}): invalid token {token!r}.')
            grid.append(row)
        candidate = KakuroCSP(self.name, grid, givens=givens)
        self.grid, self.givens = deepcopy(candidate.raw_grid), dict(candidate.givens)

    def randomize_clues(self, rng=None):
        """Keep the layout; derive all clues from a fresh valid digit pattern.
        Clear old givens because they may conflict. No answer is stored.
        This guarantees existence, not uniqueness or every sum changing.
        """
        rng = rng or random.Random()
        csp = self.to_csp()
        old = self.grid
        for _ in range(100):
            digits = list(range(1,10)); rng.shuffle(digits)
            ro, co = list(range(9)), list(range(9))
            rng.shuffle(ro); rng.shuffle(co)
            assignment = {(r,c): digits[(ro[r]+co[c])%9] for r,c in csp.variables}
            grid = deepcopy(old)
            for run in csp.runs:
                r,c = run.clue_pos
                key = 'across' if run.orientation == 'ACROSS' else 'down'
                grid[r][c][key] = sum(assignment[v.pos] for v in run.variables)
            if grid != old:
                break
        self.grid, self.givens = grid, {}

    def to_csp(self):
        return KakuroCSP(self.name, self.grid, givens=self.givens)

    def validate(self):
        csp = self.to_csp()
        for run in csp.runs:
            if not run.is_consistent_partial(csp.givens):
                r, c = run.clue_pos
                direction = 'across' if run.orientation == 'ACROSS' else 'down'
                raise ValueError(f'Conflict at {direction} clue ({r+1}, {c+1}): invalid sum or given digits.')
        return csp

    def save(self, path):
        self.to_csp()  # only structurally valid drafts can be saved
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        data = {'name': self.name, 'grid': self.grid, 'givens': [
            {'row': r, 'col': c, 'value': v} for (r,c),v in sorted(self.givens.items())]}
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

    @classmethod
    def load(cls, path):
        return cls(KakuroCSP.from_json(Path(path)))
