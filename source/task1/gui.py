"""Interactive N-Queens solver."""

from __future__ import annotations

import queue
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import ttk

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from task1.min_conflicts import MinConflictsSolver, RandomConflictedSelector, TabuMaxConflictSelector
from task1.sat_solver import Glucose3NQueenSolver

UI_FONT = "Helvetica" if sys.platform == "darwin" else ("Segoe UI" if sys.platform == "win32" else "DejaVu Sans")


class QueenWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Bài toán N Quân Hậu | Nhiệm vụ 1")
        self.root.geometry("760x680")
        self.root.minsize(560, 600)
        self.root.configure(bg="#f5f4eb")
        self.size = tk.StringVar(value="8")
        self.method = tk.StringVar(value="Glucose3 (SAT)")
        self.status = tk.StringVar(value="Chọn kích thước và thuật toán, sau đó nhấn Giải.")
        self.detail = tk.StringVar(value="")
        self.board = None
        self.results = queue.Queue()

        style = ttk.Style(root)
        style.theme_use("clam")
        style.configure("App.TFrame", background="#f5f4eb")
        style.configure("Title.TLabel", background="#f5f4eb", foreground="#3f5135",
                        font=(UI_FONT, 23, "bold"))
        style.configure("App.TLabel", background="#f5f4eb", foreground="#596e4b",
                        font=(UI_FONT, 10))
        style.configure("Status.TLabel", background="#f5f4eb", foreground="#3f5135",
                        font=(UI_FONT, 11, "bold"))
        style.configure("Solve.TButton", font=(UI_FONT, 10, "bold"), padding=(20, 8),
                        background="#769456", foreground="white", borderwidth=0)
        style.map("Solve.TButton", background=[("active", "#627f46"), ("disabled", "#a8b59c")])

        page = ttk.Frame(root, padding=24, style="App.TFrame")
        page.pack(fill="both", expand=True)
        ttk.Label(page, text="Bài Toán N Quân Hậu (N-Queen)", style="Title.TLabel").pack(anchor="w")
        ttk.Label(page, text="Xếp N quân hậu lên bàn cờ N x N sao cho không có cặp quân hậu nào tấn công nhau.",
                  style="App.TLabel").pack(anchor="w", pady=(2, 18))

        controls = ttk.Frame(page, style="App.TFrame")
        controls.pack(fill="x")
        ttk.Label(controls, text="Kích thước N", style="App.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(controls, text="Thuật toán giải", style="App.TLabel").grid(row=0, column=1, sticky="w", padx=12)
        self.size_input = ttk.Spinbox(controls, from_=4, to=50, textvariable=self.size, width=8)
        self.size_input.grid(row=1, column=0, sticky="ew", pady=(5, 0))
        self.method_input = ttk.Combobox(
            controls,
            textvariable=self.method,
            state="readonly",
            values=("Glucose3 (SAT)", "Min-Conflicts tiêu chuẩn", "Max-Conflict + Tabu (Đề xuất)"),
        )
        self.method_input.grid(row=1, column=1, sticky="ew", padx=12, pady=(5, 0))
        controls.columnconfigure(1, weight=1)
        self.button = ttk.Button(controls, text="Giải", style="Solve.TButton", command=self.start)
        self.button.grid(row=1, column=2, sticky="e", pady=(5, 0))

        self.canvas = tk.Canvas(page, highlightthickness=0, background="#f5f4eb")
        self.canvas.pack(fill="both", expand=True, pady=(18, 8))
        self.canvas.bind("<Configure>", lambda event: self.draw())
        ttk.Label(page, textvariable=self.status, style="Status.TLabel", wraplength=700).pack(anchor="w")
        ttk.Label(page, textvariable=self.detail, style="App.TLabel", wraplength=700).pack(anchor="w", pady=(3, 0))
        self.root.after(50, self.receive_result)

    def start(self):
        try:
            n = int(self.size.get())
            if not 4 <= n <= 50:
                raise ValueError
        except ValueError:
            self.status.set("Vui lòng nhập số nguyên từ 4 đến 50.")
            self.detail.set("")
            return
        self.button.configure(state="disabled")
        self.status.set("Đang tìm lời giải...")
        self.detail.set("")
        threading.Thread(target=self.solve, args=(n, self.method.get()), daemon=True).start()

    def solve(self, n, method):
        try:
            if method == "Glucose3 (SAT)":
                result = Glucose3NQueenSolver().solve(n)
                board = result.board
                solved = bool(board and board.is_valid_solution())
                detail = f"{method}  •  {result.num_clauses:,} mệnh đề CNF  •  {result.solve_time_sec * 1000:.1f} ms"
            else:
                strategy = (
                    RandomConflictedSelector()
                    if method == "Min-Conflicts tiêu chuẩn"
                    else TabuMaxConflictSelector()
                )
                result = MinConflictsSolver(strategy, max_steps=5000).solve(n)
                board = result.board
                solved = result.solved and board.is_valid_solution()
                detail = (f"{method}  •  {result.steps:,} bước  •  {result.elapsed_sec * 1000:.1f} ms"
                          f"  •  {result.remaining_conflicts} cặp xung đột")
            self.results.put((board, solved, detail))
        except Exception as exc:
            self.results.put((None, False, f"Không thể giải: {exc}"))

    def receive_result(self):
        try:
            board, solved, detail = self.results.get_nowait()
        except queue.Empty:
            pass
        else:
            self.board = board
            self.status.set("Đã tìm được lời giải." if solved else "Chưa tìm được lời giải.")
            self.detail.set(detail)
            self.button.configure(state="normal")
            self.draw()
        self.root.after(50, self.receive_result)

    def draw(self):
        self.canvas.delete("all")
        n = self.board.n if self.board else 8
        side = min(self.canvas.winfo_width(), self.canvas.winfo_height())
        cell = side / n
        left = (self.canvas.winfo_width() - side) / 2
        top = (self.canvas.winfo_height() - side) / 2
        for row in range(n):
            for col in range(n):
                x, y = left + col * cell, top + row * cell
                color = "#eae9d1" if (row + col) % 2 == 0 else "#759457"
                self.canvas.create_rectangle(x, y, x + cell, y + cell, fill=color, outline=color)
                if self.board is not None and self.board.queens[col] == row:
                    fill = "#b54f42" if self.board.conflicts_for_queen(col) else "#555553"
                    outline = "#78382f" if self.board.conflicts_for_queen(col) else "#393938"
                    self.draw_queen(x, y, cell, fill, outline)

    def draw_queen(self, x, y, cell, fill, outline):
        """Draw a scalable crown that remains visible on large boards."""
        def point(horizontal, vertical):
            return x + cell * horizontal, y + cell * vertical

        if cell < 15:
            self.canvas.create_oval(*point(.25, .25), *point(.75, .75), fill=fill, outline="")
            return

        width = max(1, cell * .018)
        crown = [
            *point(.24, .29), *point(.31, .65), *point(.69, .65), *point(.76, .29),
            *point(.62, .48), *point(.66, .22), *point(.54, .45), *point(.50, .17),
            *point(.46, .45), *point(.34, .22), *point(.38, .48),
        ]
        self.canvas.create_polygon(crown, fill=fill, outline=outline, width=width, joinstyle="round")
        for horizontal, vertical in ((.24, .27), (.34, .20), (.50, .15), (.66, .20), (.76, .27)):
            radius = cell * .045
            cx, cy = point(horizontal, vertical)
            self.canvas.create_oval(cx - radius, cy - radius, cx + radius, cy + radius,
                                    fill=fill, outline=outline, width=width)
        self.canvas.create_rectangle(*point(.30, .68), *point(.70, .78),
                                     fill=fill, outline=outline, width=width)


if __name__ == "__main__":
    window = tk.Tk()
    QueenWindow(window)
    window.mainloop()
