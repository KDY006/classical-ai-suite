# Đồ Án Cuối Kỳ: Nhập Môn Trí Tuệ Nhân Tạo (503043)

Dự án cài đặt trọn vẹn 3 bài toán Trí tuệ Nhân tạo cổ điển theo nguyên lý **Lập trình hướng đối tượng (OOP)** bằng ngôn ngữ Python cho môn học **503043 – Introduction to Artificial Intelligence** (Khoa Công nghệ Thông tin – Đại học Tôn Đức Thắng):

- **Task 1 (3.0 điểm) – Bài toán N-Queen**: Mô hình hóa Logic mệnh đề dạng chuẩn hội (CNF) giải bằng bộ giải `Glucose3` (`PySAT`), Tìm kiếm cục bộ `Min-Conflicts` kết hợp Heuristic đề xuất (*Max-Conflict + Danh sách cấm Tabu thích nghi, Điều kiện ân xá & Phá cực trị cục bộ*), kèm giao diện PyGame tối giản `ui_nqueen.py` tuân thủ `UI.md`.
- **Task 2 (3.0 điểm) – Trò chơi Tank Battle (Tìm kiếm đối kháng)**: Mô hình hóa trò chơi tổng bằng không (*Zero-Sum Game*) với trạng thái bất biến (*Immutable GameState*) và cơ chế đạn bay xuyên lượt 3 ô/chu kỳ kiểm tra va chạm từng ô một; thực nghiệm 2 tầng đối sánh 4 cấu hình thuật toán (`Minimax`, `Alpha-Beta`, `Heuristic Minimax`, `Heuristic Alpha-Beta` kết hợp BFS né tường thép, Move Ordering và Transposition Table), kèm giao diện **PyGame tối giản** (`pygame_arena.py` theo `UI.md`) và cơ chế nạp động thuật toán của nhóm sinh viên khác vào thi đấu.
- **Task 3 (3.0 điểm) – Trò chơi Kakuro (Thỏa mãn ràng buộc – CSP)**: Mô hình hóa CSP $\langle X, D, C \rangle$, kết hợp tiền xử lý tổ hợp tổng (*Sum Partitions*), lan truyền ràng buộc (*Forward Checking* & *Extended AC-3 / GAC*) với bộ ba heuristic (*MRV*, *Degree*, *LCV* 1 bước), kèm giao diện **PyGame tối giản** (`visualizer_ui.py` theo `UI.md`) trực quan hóa miền ứng viên $\{1..9\}$, gạch chéo cắt tỉa, quay lui và trình soạn thảo bảng tùy chỉnh (`BoardEditor`).
- **Task 4 (1.0 điểm) – Báo cáo khoa học IEEE & Video Demo**: Mã nguồn báo cáo chuẩn hội nghị IEEE 2 cột (tối đa 05 trang) biên dịch trên Overleaf.

---

## 1. Yêu Cầu Hệ Thống & Cài Đặt Môi Trường

### 1.1. Yêu cầu phiên bản Python
- Khuyến nghị sử dụng **Python 3.10, 3.11 hoặc 3.12** (có sẵn gói cài đặt nhị phân prebuilt wheel cho `python-sat` và `pygame` trên **macOS 13.7.8 Intel Core i5**, **Windows** và **Linux**).
- Toàn bộ mã nguồn sử dụng `pathlib.Path` và `from __future__ import annotations`, đảm bảo tương thích đa nền tảng với cấu hình chấm bài **macOS 13.7.8 (Ventura) – Intel Core i5** của giảng viên.

### 1.2. Cách 1: Cài đặt trên môi trường ảo chuẩn (Khuyến nghị trên macOS / Linux / Windows)

Mở Terminal (macOS/Linux) hoặc PowerShell/CMD (Windows) tại thư mục gốc của dự án:

**Trên macOS 13.7.8 / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirement.txt
```

**Trên Windows (PowerShell):**
```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirement.txt
```

### 1.3. Cách 2: Chạy trực tiếp bằng Python 3.11 sẵn có trên máy hiện tại
Nếu trên máy Windows đã cài sẵn các thư viện trong `F:\Python311\python.exe`:
```powershell
& "F:\Python311\python.exe" -m pip install -r requirement.txt
```

---

## 2. Cấu Trúc Thư Mục Dự Án

```text
AI_final_<Project_Group_ID>_<Student_ID>/
├── README.md                           # Hướng dẫn cài đặt và vận hành chi tiết (Tiếng Việt)
├── requirement.txt                     # Danh sách thư viện Python cần thiết
├── DEBAI.md                            # Bản dịch nguyên văn đề bài gốc sang tiếng Việt
├── PHANTICH_DEBAI.md                   # Phân tích chuyên sâu đề bài, phân công 4 thành viên & vấn đáp
├── UI.md                               # Quy ước thiết kế giao diện PyGame phong cách Tối giản (Minimalism)
├── TASK1.md                            # Tài liệu tổng hợp lý thuyết, mã nguồn & thực nghiệm Nhiệm vụ 1
├── TASK2.md                            # Tài liệu tổng hợp lý thuyết, mã nguồn & thực nghiệm Nhiệm vụ 2
├── TASK3.md                            # Tài liệu tổng hợp lý thuyết, mã nguồn & thực nghiệm Nhiệm vụ 3
├── report.md                           # Toàn văn báo cáo Task 4 & mã nguồn LaTeX/BibTeX import Overleaf
├── report.pdf                          # Báo cáo khoa học chuẩn hội nghị IEEE 2 cột (<= 5 trang)
├── demo.txt                            # File chứa đường dẫn URL tới video demo của nhóm
├── report/                             # Thư mục mã nguồn LaTeX báo cáo khoa học chuẩn IEEE (Task 4)
│   ├── main.tex                        # Mã nguồn LaTeX mẫu hội nghị IEEE 2 cột (<= 5 trang)
│   ├── references.bib                  # Danh mục tài liệu tham khảo chuẩn IEEE
│   └── figures/                        # Biểu đồ thực nghiệm và ảnh chụp giao diện tự động xuất
└── source/                             # Thư mục chứa toàn bộ mã nguồn OOP của 3 Task
    ├── README.md                       # Hướng dẫn chạy trực tiếp từ bên trong thư mục source/
    ├── requirement.txt                 # Bản sao danh sách thư viện phục vụ chạy độc lập
    ├── task1/                          # TASK 1: Bài toán N-Queen (SAT Glucose3 & Min-Conflicts)
    │   ├── base_solver.py              # Lớp trừu tượng BaseNQueenSolver thống nhất hợp đồng OOP
    │   ├── board.py                    # Lớp NQueenBoard biểu diễn bàn cờ & đếm xung đột O(1) mảng phẳng
    │   ├── cnf_encoder.py              # Lớp NQueenCNFEncoder phát hiện ràng buộc & chuyển đổi CNF
    │   ├── sat_solver.py               # Lớp Glucose3NQueenSolver giải CNF bằng PySAT Glucose3
    │   ├── min_conflicts.py            # Lớp MinConflictsSolver (chuẩn, đối chứng & Tabu thích nghi)
    │   ├── ui_nqueen.py                # Giao diện PyGame tối giản (1160x720) tuân thủ UI.md
    │   ├── main_task1.py               # Điểm khởi chạy giao diện PyGame, CLI & bộ kiểm chứng Task 1
    │   └── experiments_task1.ipynb     # Jupyter Notebook thực nghiệm & biểu đồ Task 1 (giữ nguyên output)
    ├── task2/                          # TASK 2: Trò chơi Tank Battle (Tìm kiếm đối kháng & PyGame)
    │   ├── config.py                   # Hằng số trò chơi (Tank=6 HP, Base=9 HP, Wall=3 HP, Speed=3)
    │   ├── engine/
    │   │   ├── entities.py             # Các lớp thực thể bất biến OOP: Tank, Base, BrickWall, SteelWall, Bullet
    │   │   ├── game_state.py           # Lớp GameState bất biến (Zero-Sum, khóa băm TT, kiểm tra kết thúc)
    │   │   ├── game_engine.py          # Lớp TankBattleEngine xử lý RESULT(s, a) & đạn bay từng ô một
    │   │   └── maps.py                 # Bộ kịch bản bản đồ Tầng 1 (Endgame 7x7) và Tầng 2 (Arena 9x9, 11x11)
    │   ├── agents/
    │   │   ├── base_agent.py           # Lớp cơ sở BaseTankAgent & trình nạp động bot nhóm ngoài
    │   │   ├── evaluation.py           # Hàm lượng giá chiến thuật EVAL(s) & sắp xếp nước đi (Move Ordering)
    │   │   ├── minimax_agent.py        # Cấu hình 1: Thuật toán Minimax Search thuần túy
    │   │   ├── alphabeta_agent.py      # Cấu hình 2: Thuật toán Alpha-Beta Pruning thuần túy
    │   │   ├── heuristic_minimax.py    # Cấu hình 3: Thuật toán Heuristic Minimax Search (cắt độ sâu d)
    │   │   ├── heuristic_ab.py         # Cấu hình 4: Heuristic Alpha-Beta + Move Ordering + Transposition Table
    │   │   └── external_agents/        # Thư mục thả file .py của nhóm khác vào để thi đấu trực tiếp
    │   │       ├── sample_oop_bot.py   # Bot mẫu nhóm ngoài theo chuẩn kế thừa lớp BaseTankAgent
    │   │       └── sample_dict_bot.py  # Bot mẫu nhóm ngoài theo chuẩn hàm độc lập get_action(obs_dict)
    │   ├── ui/
    │   │   └── pygame_arena.py         # Giao diện PyGame vector tối giản (1160x720) tuân thủ UI.md
    │   ├── main_task2.py               # Điểm khởi chạy PyGame tối giản, CLI không dấu & --verify Task 2
    │   └── benchmark_task2.ipynb       # Jupyter Notebook thực nghiệm 4 cấu hình Task 2 (giữ nguyên output)
    └── task3/                          # TASK 3: Câu đố Kakuro (CSP, Visualizer & Board Editor)
        ├── maps/                       # Dữ liệu bản đồ Kakuro định dạng JSON
        │   ├── board_5x5_example.json  # Bảng ví dụ 5x5 trang 4 đề bài (12 ô trắng, tổng = 60)
        │   ├── board_9x9_complex.json  # Bảng kiểm thử phức tạp 9x9 trang 5 đề bài (48 ô trắng, tổng = 249)
        │   ├── board_6x6_medium.json   # Bảng kiểm thử độ ổn định 6x6 (19 ô trắng)
        │   └── board_8x8_hard.json     # Bảng kiểm thử độ ổn định 8x8 (41 ô trắng)
        ├── csp_model.py                # Các lớp OOP: CellVariable, RunConstraint, KakuroCSP
        ├── propagation.py              # Tiền xử lý Sum Partitions, Forward Checking & Extended AC-3
        ├── solver.py                   # Bộ giải KakuroSolver tích hợp MRV, Degree Heuristic và LCV
        ├── board_editor.py             # Trình chỉnh sửa, Bulk Edit, sinh đề ngẫu nhiên & lưu/nạp JSON
        ├── visualizer_ui.py            # Giao diện PyGame tối giản (1160x720) tuân thủ UI.md & trình soạn thảo
        ├── main_task3.py               # Điểm khởi chạy PyGame tối giản, --explain-csp, CLI & --verify Task 3
        └── experiments_task3.ipynb     # Jupyter Notebook đánh giá Task 3 (giữ nguyên output)
```

---

## 3. Hướng Dẫn Chi Tiết Cách Chạy Từng Task

Đứng tại thư mục gốc của dự án để chạy các câu lệnh bên dưới (trên máy Windows hiện tại có thể thay `python` bằng `& "F:\Python311\python.exe"` nếu chưa kích hoạt `.venv`).

---

### 3.1. Chạy Task 1: Bài Toán N-Queen (`Glucose3` SAT & `Min-Conflicts`)

#### A. Mở giao diện đồ họa PyGame tối giản (tuân thủ `UI.md`)
```bash
python source/task1/main_task1.py
```
- Chọn kích thước bàn cờ $N \in [4, 100]$, chọn thuật toán (`Glucose3 (SAT - CNF)`, `Min-Conflicts tiêu chuẩn`, `Max-Conflict thuần`, hoặc `Max-Conflict + Tabu thích nghi`), hỗ trợ **Giải ngay**, **Ngẫu nhiên**, **Từng bước**, **Phát / Tạm dừng**, thanh tốc độ và **So sánh** nhanh chuẩn vs đề xuất trên cùng bàn cờ.

#### B. Chạy thực nghiệm dòng lệnh (CLI tiếng Việt không dấu) & kiểm chứng tự động
```bash
# Chạy trọn bộ thực nghiệm (minh họa CNF, Glucose3, đối sánh 3 chiến lược Min-Conflicts)
python source/task1/main_task1.py --cli

# Chạy bộ kiểm chứng toán học & hiệu năng tự động
python source/task1/main_task1.py --verify

# Tuỳ chỉnh tham số thực nghiệm CLI
python source/task1/main_task1.py --cli --sat-sizes 4 8 16 32 50 --mc-sizes 8 16 32 64 100 150 200 --trials 50
```

---

### 3.2. Chạy Task 2: Trò Chơi Tank Battle (Tìm Kiếm Đối Kháng & PyGame Tối Giản)

#### A. Khởi chạy Giao diện Đồ họa PyGame Tối giản (Yêu cầu 2.3 — tuân thủ `UI.md`)
```bash
python source/task2/main_task2.py
```
**Hướng dẫn sử dụng bảng điều khiển tiếng Việt trên cửa sổ PyGame (`1160 × 720`):**
- **Cấu hình:** Nhấn `Bản đồ: ...` để đổi giữa 6 kịch bản Tầng 1 (*7x7*) và Tầng 2 (*9x9, 11x11*); nhấn `MAX: ...` / `MIN: ...` để chọn đủ 4 cấu hình thuật toán, `Người chơi (Bàn phím)` (`WASD`/mũi tên đi, `Space` bắn, `Enter` chờ) hoặc các bot nhóm ngoài; nhấn `Nạp lại Bot nhóm ngoài` để quét nạp nóng từ `external_agents/`.
- **Điều khiển:** `Tự chạy` / `Tạm dừng` (`Space`), `Từng bước` (`→`), `Đặt lại` (`R`) và thanh trượt tốc độ (`60–800 ms/lượt`).

#### B. Chạy Benchmark CLI (tiếng Việt không dấu) & Kiểm chứng tự động (`--verify`)
```bash
python source/task2/main_task2.py --cli
python source/task2/main_task2.py --verify
```

#### C. Tích hợp thuật toán của nhóm sinh viên khác vào thi đấu (Yêu cầu 2.3)
Chép file `.py` của nhóm khác vào `source/task2/agents/external_agents/` và bấm **`Nạp lại Bot`**. Hỗ trợ tự động 2 chuẩn:
1. **Kế thừa lớp `BaseTankAgent`**: Override `choose_action(self, state: GameState) -> str` (xem mẫu `sample_oop_bot.py`).
2. **Hàm độc lập `get_action(obs: dict) -> str`**: Nhận `dict` trạng thái độc lập và trả về 1 trong 6 hành động `"MOVE_UP"`, `"MOVE_DOWN"`, `"MOVE_LEFT"`, `"MOVE_RIGHT"`, `"FIRE"`, `"STAY"` (xem mẫu `sample_dict_bot.py`).

---

### 3.3. Chạy Task 3: Trò Chơi Kakuro (Bộ Giải CSP, Visualizer & Board Editor Tối Giản)

#### A. Khởi chạy Giao diện PyGame Tối giản (Yêu cầu 3.3 — tuân thủ `UI.md`)
```bash
python source/task3/main_task3.py
```
**Hướng dẫn sử dụng bảng điều khiển tiếng Việt trên cửa sổ `1160 × 720` (3 tông màu tối giản):**
- **Trực quan hóa miền giá trị, cắt tỉa & quay lui**:
  - Ô trắng chưa gán hiển thị **lưới ứng viên $3 \times 3$ (`1..9`)** mảnh màu xám trung tính.
  - **Viền Đậm (`#111827`) trên nền Xám Nhạt**: Ô biến đang được chọn (`SELECT_VAR` / `ASSIGN`).
  - **Số Đỏ gạch chéo (`#C83E37`)**: Ứng viên bị loại bởi **Constraint Propagation** (`PRUNE`); dấu `×` đỏ trên nền đỏ nhạt báo miền rỗng.
  - **Nền Đỏ Nhạt + Viền Đỏ**: Từ chối giá trị (`REJECT`), ngõ cụt (`FAILURE`) hoặc bước **Backtrack** khôi phục miền.
  - **Số Đen kèm góc `G`**: Chữ số cho trước (`given`); **Số Xanh Ngọc Trầm (`#0F766E`)**: Chữ số đã gán hợp lệ (toàn lưới phủ xanh ngọc nhạt khi `SOLVED`).
- **Chế độ Giải**: Chọn nhanh bảng mẫu (`5×5`, `6×6`, `8×8`, `9×9`), chọn 3 chế độ giải (`Quay lui cơ bản`, `Kiểm tra tiến + MRV`, `AC-3 mở rộng + MRV/Bậc/LCV`), điều khiển `Phát` / `Tạm dừng` (`Space`), `Bước tiếp` / `Trước` (`Phải`/`Trái`), `Đặt lại` (`0`), `Bước cuối`, `Giải lại`, thanh tốc độ (`25–1000 ms/bước`) và nút `Sửa bảng` / `Dừng & Sửa bảng` (`Esc`).
- **Chế độ Soạn thảo (`BoardEditor`) & Sửa nhanh (`Bulk Edit`)**: Tạo bảng mới `3×3`–`9×9`, đổi `Ô trắng` / `Ô đen / gợi ý`, chỉnh `Tổng ngang` / `Tổng dọc`, nhập `Số cho trước`, `Sửa nhanh (Bulk)`, `Sinh gợi ý mới` đảm bảo có nghiệm, `Kiểm tra hợp lệ`, `Lưu JSON` / `Mở JSON` trong `maps/custom/` và `Giải bảng hiện tại`.

#### B. Chạy CLI (tiếng Việt không dấu), giải thích CSP & kiểm chứng 22 tiêu chí
```bash
python source/task3/main_task3.py --explain-csp
python source/task3/main_task3.py --cli --trials 10
python source/task3/main_task3.py --verify
```

---

## 4. Mở & Kiểm Tra 3 File Jupyter Notebook Thực Nghiệm (`.ipynb`)

Cả 3 file Notebook đã được chạy hoàn chỉnh và **lưu nguyên 100% kết quả đầu ra cùng biểu đồ ở toàn bộ các cell**:
1. `source/task1/experiments_task1.ipynb`
2. `source/task2/benchmark_task2.ipynb`
3. `source/task3/experiments_task3.ipynb`

Mở trực tiếp trên VS Code hoặc chạy `jupyter lab` tại thư mục gốc để xem chi tiết.

---

## 5. Biên Dịch Báo Cáo IEEE (Task 4) & Quy Cách Đóng Gói Nộp Bài

1. **Biên dịch `report.pdf` trên Overleaf (xem chi tiết tại `report.md`)**:
   - Tải toàn bộ thư mục `report/` (`main.tex`, `references.bib` và thư mục `figures/` gồm 8 ảnh PNG) lên Overleaf — hoặc copy–paste trực tiếp khối `main.tex` và `references.bib` từ `report.md`.
   - Chọn trình biên dịch **pdfLaTeX** (mặc định của Overleaf), kiểm tra lại Họ tên, MSSV, Email của 4 thành viên và giảng viên hướng dẫn **TS. Trịnh Hùng Cường** ở vị trí tác giả cuối cùng trong khối `\author{...}`.
   - Biên dịch, xác nhận tổng số trang $\le 5$ trang (2 cột chuẩn IEEE), tải file PDF và đặt tại thư mục gốc dưới tên `report.pdf`.
2. **Cập nhật `demo.txt` & Đóng gói cá nhân**:
   - Dán URL công khai của video demo vào `demo.txt`.
   - Khi nén bài nộp cá nhân, tạo thư mục đúng định dạng `AI_final_<Project Group ID>_<Student ID>` chứa đủ `source/`, `report.pdf`, `demo.txt` (cùng `README.md` và `requirement.txt`), nén thành file `.zip` nộp lên hệ thống trước hạn.
