# Đồ Án Cuối Kỳ: Nhập Môn Trí Tuệ Nhân Tạo (503043)

Dự án cài đặt trọn vẹn 3 bài toán Trí tuệ Nhân tạo cổ điển theo nguyên lý **Lập trình hướng đối tượng (OOP)** bằng ngôn ngữ Python cho môn học **503043 – Introduction to Artificial Intelligence** (Khoa Công nghệ Thông tin – Đại học Tôn Đức Thắng):

- **Task 1 (3.0 điểm) – Bài toán N-Queen**: Mô hình hóa Logic mệnh đề dạng chuẩn hội (CNF) giải bằng bộ giải `Glucose3` (`PySAT`), Tìm kiếm cục bộ `Min-Conflicts` kết hợp Heuristic đề xuất (*Max-Conflict + Danh sách cấm ngắn hạn Tabu & Điều kiện ân xá Aspiration*), kèm giao diện bàn cờ trực quan `gui.py`.
- **Task 2 (3.0 điểm) – Trò chơi Tank Battle (Tìm kiếm đối kháng)**: Mô hình hóa trò chơi tổng bằng không (*Zero-Sum Game*) với trạng thái bất biến (*Immutable GameState*) và cơ chế đạn bay xuyên lượt 3 ô/chu kỳ kiểm tra va chạm từng ô một; thực nghiệm 2 tầng đối sánh 4 cấu hình thuật toán (`Minimax`, `Alpha-Beta`, `Heuristic Minimax`, `Heuristic Alpha-Beta`), kèm giao diện **PyGame Arena** tích hợp bộ sprite Kenney (CC0) và cơ chế nạp động thuật toán của nhóm sinh viên khác vào thi đấu.
- **Task 3 (3.0 điểm) – Trò chơi Kakuro (Thỏa mãn ràng buộc – CSP)**: Mô hình hóa CSP $\langle X, D, C \rangle$, kết hợp tiền xử lý tổ hợp tổng (*Sum Partitions*), lan truyền ràng buộc (*Forward Checking* & *Extended AC-3*) với bộ ba heuristic (*MRV*, *Degree*, *LCV*), kèm giao diện **PyGame Visualizer & Board Editor** trực quan hóa miền ứng viên $\{1..9\}$, hiệu ứng cắt tỉa miền, quay lui và trình soạn thảo câu đố tùy chỉnh.
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
├── DESIGN_SPECIFICATION.md             # Tài liệu đặc tả kỹ thuật, toán học & phân công 4 thành viên
├── demo.txt                            # File chứa đường dẫn URL tới video demo của nhóm
├── report/                             # Thư mục mã nguồn báo cáo khoa học chuẩn IEEE (Task 4)
│   ├── main.tex                        # Mã nguồn LaTeX mẫu hội nghị IEEE 2 cột (<= 5 trang)
│   ├── references.bib                  # Danh mục tài liệu tham khảo chuẩn IEEE
│   └── figures/                        # Biểu đồ thực nghiệm và ảnh chụp giao diện tự động xuất
└── source/                             # Thư mục chứa toàn bộ mã nguồn OOP của 3 Task
    ├── README.md                       # Hướng dẫn chạy trực tiếp từ bên trong thư mục source/
    ├── requirement.txt                 # Bản sao danh sách thư viện phục vụ chạy độc lập
    ├── task1/                          # TASK 1: Bài toán N-Queen (SAT Glucose3 & Min-Conflicts)
    │   ├── board.py                    # Lớp NQueenBoard biểu diễn bàn cờ & đếm xung đột O(1)
    │   ├── cnf_encoder.py              # Lớp NQueenCNFEncoder sinh ràng buộc & chuyển đổi CNF
    │   ├── sat_solver.py               # Lớp Glucose3NQueenSolver giải CNF bằng PySAT Glucose3
    │   ├── min_conflicts.py            # Lớp MinConflictsSolver (bản chuẩn & bản Max-Conflict + Tabu)
    │   ├── gui.py                      # Giao diện Tkinter giải & vẽ trực quan bàn cờ N-Queen
    │   ├── main_task1.py               # Chương trình chạy thực nghiệm nhanh Task 1 trên dòng lệnh
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
    │   │   ├── assets/                 # Bộ sprite Kenney Top-down Tanks Redux (CC0) kèm CREDITS.txt
    │   │   └── pygame_arena.py         # Giao diện đồ họa PyGame Arena 2 cột tự co giãn
    │   ├── main_task2.py               # Điểm khởi chạy giao diện PyGame hoặc benchmark dòng lệnh Task 2
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
        ├── visualizer_ui.py            # Giao diện PyGame hiển thị miền {1..9}, cắt tỉa, quay lui & soạn thảo
        ├── README.md                   # Tài liệu hướng dẫn chuyên sâu riêng cho Task 3
        ├── main_task3.py               # Điểm khởi chạy giao diện Kakuro Visualizer hoặc benchmark CLI
        └── experiments_task3.ipynb     # Jupyter Notebook đánh giá Task 3 (giữ nguyên output)
```

---

## 3. Hướng Dẫn Chi Tiết Cách Chạy Từng Task

Đứng tại thư mục gốc của dự án để chạy các câu lệnh bên dưới (trên máy Windows hiện tại có thể thay `python` bằng `& "F:\Python311\python.exe"` nếu chưa kích hoạt `.venv`).

---

### 3.1. Chạy Task 1: Bài Toán N-Queen (`Glucose3` SAT & `Min-Conflicts`)

#### A. Mở giao diện đồ họa bàn cờ N-Queen
```bash
python source/task1/gui.py
```
- Chọn kích thước bàn cờ $N \in [4, 50]$, chọn thuật toán (`Glucose3`, `Min-Conflicts`, hoặc `Max-Conflict + Tabu`) rồi nhấn **Giải**.

#### B. Chạy chương trình thực nghiệm dòng lệnh (CLI)
```bash
python source/task1/main_task1.py
```
- Tuỳ chỉnh tham số thực nghiệm:
```bash
python source/task1/main_task1.py --sat-sizes 4 8 16 32 50 --mc-sizes 8 16 32 64 100 150 --trials 30 --max-steps 2500
```

---

### 3.2. Chạy Task 2: Trò Chơi Tank Battle (Tìm Kiếm Đối Kháng & PyGame Arena)

#### A. Khởi chạy Giao diện Đồ họa PyGame Arena (Yêu cầu 2.3)
```bash
python source/task2/main_task2.py
```
**Hướng dẫn sử dụng bảng điều khiển trên cửa sổ PyGame Arena:**
- **Nút bản đồ (`Classic Battle City (9x9)`, ...)**: Nhấn để chuyển đổi giữa 6 kịch bản bản đồ Tầng 1 (Endgame `7x7`) và Tầng 2 (Full Arena `9x9`, `11x11`).
- **Nút `MAX: ...` (Xe Xanh)** và **`MIN: ...` (Xe Đỏ)**: Nhấn để chọn bộ điều khiển cho từng bên: `Heuristic Alpha-Beta (d=4)`, `Heuristic Minimax (d=3)`, `Pure Alpha-Beta (cap=6)`, `Pure Minimax (cap=5)`, `Human` (bàn phím `WASD`/mũi tên + `Space` bắn + `Enter` đứng yên), hoặc các bot nhóm ngoài trong `external_agents/`.
- **Các nút điều khiển trận đấu**: `Play` / `Pause` (chạy tự động), `Step` (chạy từng lượt), `Reset` (khởi động lại ván), `-` / `+` (chỉnh tốc độ), `Reload bots` (quét nạp nóng bot mới trong `external_agents/`).

#### B. Chạy Benchmark đối sánh 4 thuật toán trên Terminal (CLI)
```bash
python source/task2/main_task2.py --cli
```

#### C. Tích hợp thuật toán của nhóm sinh viên khác vào thi đấu (Yêu cầu 2.3)
Chép file `.py` của nhóm khác vào `source/task2/agents/external_agents/` và bấm **`Reload bots`**. Hỗ trợ tự động 2 chuẩn:
1. **Kế thừa lớp `BaseTankAgent`**: Override `choose_action(self, state: GameState) -> str` (xem mẫu `sample_oop_bot.py`).
2. **Hàm độc lập `get_action(obs: dict) -> str`**: Nhận `dict` trạng thái độc lập và trả về 1 trong 6 hành động `"MOVE_UP"`, `"MOVE_DOWN"`, `"MOVE_LEFT"`, `"MOVE_RIGHT"`, `"FIRE"`, `"STAY"` (xem mẫu `sample_dict_bot.py`).

---

### 3.3. Chạy Task 3: Trò Chơi Kakuro (Bộ Giải CSP, Visualizer & Board Editor)

#### A. Khởi chạy Giao diện PyGame Kakuro Visualizer & Board Editor (Yêu cầu 3.3)
```bash
python source/task3/main_task3.py
```
**Hướng dẫn sử dụng bảng điều khiển trên cửa sổ Kakuro Visualizer:**
- **Trực quan hóa miền giá trị, cắt tỉa & quay lui**:
  - Ô trắng chưa gán hiển thị **lưới ứng viên $3 \times 3$ (`1..9`)** còn lại trong miền $D_i$.
  - **Viền Xanh Dương**: Ô biến đang được chọn (`SELECT_VAR` / `ASSIGN`).
  - **Nền Đỏ Nhạt + Số Đỏ gạch ngang**: Ứng viên bị loại bởi **Constraint Propagation** (`PRUNE`); chữ `x` báo miền rỗng.
  - **Nền Cam**: Từ chối giá trị, ngõ cụt hoặc bước **Backtrack** khôi phục miền.
  - **Chữ Tím (`G`)**: Chữ số cho trước (`given digit`); **Nền Xanh Lá**: Đã tìm được nghiệm hợp lệ (`SOLVED`).
- **Nút điều khiển ở `Solver Mode`**:
  - `Switch Preset` (đổi bảng `5x5`, `9x9`, `6x6`, `8x8`), nút chọn chế độ giải (`Advanced: AC-3 + MRV/Degree/LCV`, `Backtracking + FC + MRV`, `Basic Backtracking`), `Auto Play` / `Pause` (`Space`), `Previous Step` / `Next Step` (mũi tên `Trái`/`Phải`), `Reset` (`0`), `Final State`, thanh kéo `Speed`, `Solve Again`, và `Edit Board` / `Stop & Edit` (`Esc` – dừng luồng giải nền để chỉnh sửa bảng).
- **Chế độ `Board Editor`**:
  - Cho phép tạo bảng mới `3x3`–`9x9`, đổi loại ô Trắng/Đen, sửa tổng ngang/dọc, nhập số cho trước (`given`), sửa hàng loạt `Bulk Edit All Cells`, sinh ngẫu nhiên bộ tổng có nghiệm `Randomize All Clues`, kiểm tra hợp lệ và lưu/mở file JSON trong `maps/custom/`.

#### B. Chạy Benchmark đánh giá bộ giải Kakuro trên Terminal (CLI)
```bash
python source/task3/main_task3.py --cli
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

1. **Biên dịch `report.pdf` trên Overleaf**:
   - Tải toàn bộ thư mục `report/` (`main.tex`, `references.bib` và thư mục `figures/`) lên Overleaf.
   - Điền Họ tên, MSSV và Email thực tế của 4 thành viên vào khối `\author{...}` trong `main.tex` (giữ tên giảng viên **Thanh-An Nguyen** ở vị trí tác giả cuối cùng).
   - Biên dịch và tải file PDF đặt vào thư mục gốc dưới tên `report.pdf`.
2. **Cập nhật `demo.txt` & Đóng gói cá nhân**:
   - Dán URL công khai của video demo vào `demo.txt`.
   - Khi nén bài nộp cá nhân, tạo thư mục đúng định dạng `AI_final_<Project Group ID>_<Student ID>` chứa đủ `source/`, `report.pdf`, `demo.txt` (cùng `README.md` và `requirement.txt`), nén thành file `.zip` nộp lên hệ thống trước hạn.
