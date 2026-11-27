# ĐỒ ÁN CUỐI KỲ: NHẬP MÔN TRÍ TUỆ NHÂN TẠO (503043)

> **Giải quyết các bài toán Trí tuệ Nhân tạo cổ điển bằng Logic Mệnh đề, Tìm kiếm Cục bộ, Tìm kiếm Đối kháng và Thỏa mãn Ràng buộc (CSP)** — thiết kế hoàn toàn theo nguyên lý **Lập trình hướng đối tượng (OOP)** bằng Python, tích hợp đồng bộ **03 giao diện đồ họa PyGame phong cách Tối giản (Minimalism)** và tương thích hoàn toàn môi trường chấm bài **macOS 13.7.8 (Ventura) – Intel Core i5** cũng như Windows/Linux.

---

## 1. Thông Tin Học Phần, Giảng Viên Hướng Dẫn & Thành Viên Nhóm

- **Trường:** Trường Đại học Tôn Đức Thắng (*Ton Duc Thang University*)
- **Khoa:** Khoa Công nghệ Thông tin (*Faculty of Information Technology*)
- **Học phần:** `503043` – Nhập môn Trí tuệ Nhân tạo (*Introduction to Artificial Intelligence*)
- **Giảng viên hướng dẫn:** **TS. Trịnh Hùng Cường** (`trinhhungcuong@tdtu.edu.vn`) *(đứng ở vị trí tác giả cuối cùng trong báo cáo khoa học IEEE theo quy định Nhiệm vụ 4)*
- **Môi trường chấm bài mục tiêu:** macOS 13.7.8 (Intel Core i5) / Windows / Linux — Python `3.10–3.12`

### Phân chia công việc chi tiết (4 thành viên)

| STT | Họ và tên | MSSV | Email sinh viên | Vai trò & Phụ trách chính | Hạng mục bàn giao cụ thể | Hoàn thành |
| :-: | :--- | :---: | :--- | :--- | :--- | :-: |
| 1 | **Nguyễn Văn Duy** | `52400010` | `52400010@student.tdtu.edu.vn` | **Nhóm trưởng** *(Kiến trúc OOP, `UI.md`, Tích hợp, Kiểm thử & Task 4)* | Thiết kế kiến trúc OOP chung và quy chuẩn giao diện tối giản [UI.md](UI.md); quản lý kho Git, hợp nhất mã nguồn 3 nhánh và kiểm thử tương thích macOS 13.7.8; chuẩn hóa quy ước ngôn ngữ và bộ kiểm chứng tự động (`33/33`); biên tập báo cáo khoa học IEEE ([report/main.tex](report/main.tex), [report/references.bib](report/references.bib), [report.md](report.md)), [README.md](README.md), [DEBAI.md](DEBAI.md), [PHANTICH_DEBAI.md](PHANTICH_DEBAI.md) và video demo ([demo.txt](demo.txt)). | **100%** |
| 2 | **Lê Văn Quý** | `52400153` | `52400153@student.tdtu.edu.vn` | **Thành viên — Task 1** *(N-Queen: Logic Mệnh Đề & Local Search)* | Mô hình hóa Logic mệnh đề, thuật toán phát hiện ràng buộc $\mathcal{O}(N^2)$ & chuyển đổi CNF (`base_solver.py`, `board.py`, `cnf_encoder.py`, `sat_solver.py`, `min_conflicts.py`, `main_task1.py`); đề xuất heuristic `Max-Conflict + Tabu thích nghi`; giao diện PyGame tối giản `ui_nqueen.py`; thực nghiệm và biểu đồ trong `experiments_task1.ipynb` và [TASK1.md](TASK1.md). | **100%** |
| 3 | **Huỳnh Thiên Đức** | `5240110` | `5240110@student.tdtu.edu.vn` | **Thành viên — Task 2** *(Tank Battle: Tìm Kiếm Đối Kháng & PyGame)* | Mô hình hóa Trò chơi Tổng bằng không trên `GameState` bất biến (`config.py`, `engine/`, `maps.py`) với vật lý đạn bay `3` ô/chu kỳ xử lý từng ô một; cài đặt 4 cấu hình tìm kiếm (`Minimax`, `Alpha-Beta`, `Heuristic Minimax`, `Heuristic Alpha-Beta` tích hợp hàm lượng giá BFS né tường thép, Move Ordering & Transposition Table); giao diện PyGame vector tối giản `pygame_arena.py`; cơ chế nạp động bot nhóm ngoài (`external_agents/`); thực nghiệm 2 tầng trong `benchmark_task2.ipynb` và [TASK2.md](TASK2.md). | **100%** |
| 4 | **Lê Tiến Đạt** | `52400105` | `52400105@student.tdtu.edu.vn` | **Thành viên — Task 3** *(Kakuro: Bài Toán Thỏa Mãn Ràng Buộc CSP)* | Mô hình hóa Kakuro CSP $\langle X, D, C \rangle$ và số hóa 4 bảng JSON (`5×5`, `6×6`, `8×8`, `9×9`); cài đặt `SumPartitionCatalog`, `ForwardChecker`, `ExtendedAC3Propagator` (GAC) và bộ ba heuristic `MRV/Degree/LCV` (`csp_model.py`, `propagation.py`, `solver.py`, `main_task3.py`); giao diện PyGame đa luồng `visualizer_ui.py` tích hợp trình soạn thảo `board_editor.py`; thực nghiệm 30 lần chạy trong `experiments_task3.ipynb` và [TASK3.md](TASK3.md). | **100%** |

---

## 2. Tổng Quan 4 Nhiệm Vụ & Kết Quả Nổi Bật

| Nhiệm vụ | Trọng số | Công nghệ & Thuật toán chính | Kết quả thực nghiệm & Kiểm chứng tiêu biểu | Tài liệu chi tiết |
| :--- | :-: | :--- | :--- | :--- |
| **Task 1 — N-Queen** | **3.0đ** | Logic mệnh đề CNF + `Glucose3` (`PySAT`); `Min-Conflicts` + Heuristic đề xuất *Max-Conflict + Tabu thích nghi, Ân xá & Phá cực trị cục bộ*; PyGame `ui_nqueen.py` | `Glucose3` giải $N \in [4, 80]$ (`840.720` mệnh đề tại $N=80$); Heuristic đề xuất đạt **100%** trên mọi $N \in [8, 200]$ (50 bàn cờ/mức), giảm **74,6%** bước tại $N=8$, **58,7%** tại $N=16$ (nhanh gấp `4,6×`), **21,7%** tại $N=200$; `--verify`: **5/5 đạt**. | [TASK1.md](TASK1.md) |
| **Task 2 — Tank Battle** | **3.0đ** | Zero-Sum Game (`GameState` bất biến, `Tank=6`, `Base=9`, `Wall=3`, đạn `3` ô từng bước); 4 cấu hình (`Minimax`, `Alpha-Beta`, `Heuristic Minimax`, `Heuristic Alpha-Beta` + BFS né tường thép + TT); PyGame `pygame_arena.py` + plugin bot ngoài | `Heuristic Alpha-Beta (d=4)` giảm **890×** trạng thái ở Tầng 1 (`34` vs `30.278`, `3,84 ms`, nhanh gấp `353×`), giảm **89,5%** ở đấu trường `9×9` (`12,89 ms/lượt`), **77,8%** ở `11×11` (`68,07 ms/lượt`), toàn thắng **3/3** trận đầy máu; nạp nóng bot ngoài 2 chuẩn; `--verify`: **6/6 đạt**. | [TASK2.md](TASK2.md) |
| **Task 3 — Kakuro CSP** | **3.0đ** | CSP $\langle X, D, C \rangle$, bất biến tổng $H=V$; `SumPartitionCatalog` + `ForwardChecker` + `ExtendedAC3Propagator` (GAC) + `MRV/Degree/LCV`; PyGame đa luồng `visualizer_ui.py` + `BoardEditor` | Tiền xử lý 2 tầng rút gọn **88,9%** tổng miền, đưa **100%** ô bảng `5×5` (`12/12`) và `9×9` (`48/48`) về đơn trị; `AC-3 mở rộng` đạt cận dưới $|X|$ nút và **`0` quay lui** trên cả 4 bảng (giảm `827,8×` nút trên `5×5`, `190,4×` trên `9×9`); `BT_FC` nhanh nhất (`1,15 ms` trên `5×5`, `29,54 ms` trên `9×9`); `--verify`: **22/22 đạt**. | [TASK3.md](TASK3.md) |
| **Task 4 — Báo cáo IEEE & Demo** | **1.0đ** | Mẫu hội nghị `IEEEtran` 2 cột ($\le 5$ trang), Overleaf `pdfLaTeX + T5`, `8` hình PNG & `3` bảng tổng hợp | Hoàn thiện `report/main.tex`, `report/references.bib` (`0` lỗi kiểm toán, `8/8` hình & `8/8` trích dẫn khớp) và xuất sẵn mã nguồn import Overleaf trong `report.md`; tự đánh giá **10,0/10,0**. | [report.md](report.md) |

### Nguyên tắc kiến trúc & quy ước xuyên suốt dự án
- **Tách biệt tuyệt đối Model–View:** Toàn bộ các module thuật toán lõi ở cả 3 Task có đúng **`0` lệnh `import pygame`**, cho phép chạy benchmark CLI/Notebook ở tốc độ tối đa và gắn vào giao diện PyGame qua generator/luồng nền (`iter_solve()`, `iter_match()`, `iter_steps()`).
- **Đồng bộ giao diện PyGame tối giản ([UI.md](UI.md)):** Cả 3 giao diện đều dùng cửa sổ cố định `1160 × 720` kết xuất `1:1` (không dùng `smoothscale` hay API riêng của Windows), giới hạn đúng **3 tông màu** (Giấy/Mực `#FAFAFA`/`#111827`, Xanh ngọc trầm `#0F766E`, Đỏ gạch trầm `#C83E37`) và font hệ thống đa nền tảng.
- **Quy ước ngôn ngữ chống lỗi font:** **Tiếng Việt có dấu** cho giao diện PyGame, biểu đồ Matplotlib, Markdown Notebook và tài liệu `.md`/LaTeX; **Tiếng Việt không dấu (ASCII thuần)** cho toàn bộ đầu ra CLI terminal (`--cli`, `--verify`, `--explain-*`), ngoại lệ và toàn bộ comment/docstring trong mã nguồn `.py`.

---

## 3. Cấu Trúc Thư Mục Dự Án

```text
AI_final_<Project_Group_ID>_<Student_ID>/
├── README.md                           # Tài liệu tổng quan dự án, phân công nhóm & hướng dẫn chạy
├── requirement.txt                     # Danh sách thư viện Python cần thiết
├── DEBAI.md                            # Bản dịch nguyên văn đề bài gốc (2627-HK1-AI-CK.pdf)
├── PHANTICH_DEBAI.md                   # Phân tích chuyên sâu đề bài, phân công 4 thành viên & vấn đáp
├── UI.md                               # Quy ước thiết kế giao diện PyGame Tối giản (Minimalism)
├── TASK1.md                            # Tài liệu tổng hợp lý thuyết, OOP & thực nghiệm Nhiệm vụ 1
├── TASK2.md                            # Tài liệu tổng hợp lý thuyết, OOP & thực nghiệm Nhiệm vụ 2
├── TASK3.md                            # Tài liệu tổng hợp lý thuyết, OOP & thực nghiệm Nhiệm vụ 3
├── report.md                           # Toàn văn báo cáo Task 4 + mã nguồn LaTeX/BibTeX import Overleaf
├── report.pdf                          # Báo cáo khoa học chuẩn hội nghị IEEE 2 cột (<= 5 trang)
├── demo.txt                            # Đường dẫn URL video demo của nhóm
├── report/                             # Mã nguồn LaTeX báo cáo khoa học IEEE (Task 4)
│   ├── main.tex                        # Mã nguồn IEEEtran 2 cột (tương thích Overleaf pdfLaTeX + T5)
│   ├── references.bib                  # 08 tài liệu tham khảo chuẩn IEEE
│   └── figures/                        # Bộ 08 hình ảnh (biểu đồ thực nghiệm + 3 ảnh giao diện PyGame)
│       ├── task1_glucose3_scaling.png
│       ├── task1_min_conflicts_comparison.png
│       ├── task1_nqueen_ui.png
│       ├── task2_four_algo_comparison.png
│       ├── task2_tier2_9x9_vs_11x11.png
│       ├── task2_arena_ui.png
│       ├── task3_csp_benchmark.png
│       └── task3_kakuro_ui.png
└── source/                             # Toàn bộ mã nguồn OOP độc lập của 3 nhiệm vụ
    ├── README.md                       # Hướng dẫn chạy trực tiếp từ bên trong thư mục source/
    ├── requirement.txt                 # Bản sao danh sách thư viện phục vụ chạy độc lập
    ├── task1/                          # TASK 1: Bài toán N-Queen (SAT Glucose3 & Min-Conflicts)
    │   ├── __init__.py
    │   ├── base_solver.py              # Lớp trừu tượng BaseNQueenSolver(ABC)
    │   ├── board.py                    # NQueenBoard với 3 mảng đếm xung đột O(1)
    │   ├── cnf_encoder.py              # PropositionalVariableMapper & NQueenCNFEncoder
    │   ├── sat_solver.py               # Glucose3NQueenSolver (PySAT CDCL)
    │   ├── min_conflicts.py            # MinConflictsSolver & AdaptiveTabuMaxConflictSelector
    │   ├── ui_nqueen.py                # Giao diện PyGame tối giản MinimalNQueenUI (1160x720)
    │   ├── main_task1.py               # Điểm khởi chạy PyGame, --explain-cnf, --cli, --verify
    │   └── experiments_task1.ipynb     # Notebook thực nghiệm Task 1 (đã lưu đủ 100% outputs)
    ├── task2/                          # TASK 2: Trò chơi Tank Battle (Tìm kiếm đối kháng)
    │   ├── __init__.py
    │   ├── config.py                   # Hằng số luật chơi (Tank=6, Base=9, Wall=3, Speed=3)
    │   ├── engine/
    │   │   ├── __init__.py
    │   │   ├── entities.py             # Thực thể bất biến: Tank, Base, BrickWall, SteelWall, Bullet
    │   │   ├── game_state.py           # GameState bất biến (Zero-Sum, khóa TT, kiểm tra kết thúc)
    │   │   ├── game_engine.py          # TankBattleEngine: RESULT(s,a), đạn 3 ô từng bước, iter_match()
    │   │   └── maps.py                 # 6 kịch bản Tầng 1 (7x7) và Tầng 2 (9x9, 11x11)
    │   ├── agents/
    │   │   ├── __init__.py
    │   │   ├── base_agent.py           # BaseTankAgent, DictAdapterTankAgent & trình nạp động bot ngoài
    │   │   ├── evaluation.py           # TacticalEvaluator: EVAL(s) BFS né tường thép & Move Ordering
    │   │   ├── minimax_agent.py        # Cấu hình 1: Minimax thuần
    │   │   ├── alphabeta_agent.py      # Cấu hình 2: Alpha-Beta thuần
    │   │   ├── heuristic_minimax.py    # Cấu hình 3: Heuristic Minimax (độ sâu d)
    │   │   ├── heuristic_ab.py         # Cấu hình 4: Heuristic Alpha-Beta + Move Ordering + TT
    │   │   └── external_agents/        # Thư mục thả bot nhóm ngoài để thi đấu trực tiếp
    │   │       ├── __init__.py
    │   │       ├── sample_oop_bot.py   # Mẫu chuẩn kế thừa BaseTankAgent
    │   │       └── sample_dict_bot.py  # Mẫu chuẩn hàm độc lập get_action(obs_dict)
    │   ├── ui/
    │   │   ├── __init__.py
    │   │   └── pygame_arena.py         # Giao diện PyGame vector tối giản TankBattleArenaUI (1160x720)
    │   ├── main_task2.py               # Điểm khởi chạy PyGame, --explain-model, --cli, --verify
    │   └── benchmark_task2.ipynb       # Notebook thực nghiệm Task 2 (đã lưu đủ 100% outputs)
    └── task3/                          # TASK 3: Câu đố Kakuro (CSP, Visualizer & Board Editor)
        ├── __init__.py
        ├── maps/                       # 4 bảng Kakuro định dạng JSON chuẩn
        │   ├── board_5x5_example.json  # Bảng ví dụ 5x5 trang 4 đề bài (12 biến, tổng H=V=60)
        │   ├── board_6x6_medium.json   # Bảng trung bình 6x6 (19 biến, tổng H=V=106)
        │   ├── board_8x8_hard.json     # Bảng nâng cao 8x8 (41 biến, tổng H=V=248)
        │   └── board_9x9_complex.json  # Bảng phức tạp 9x9 trang 5 đề bài (48 biến, tổng H=V=249)
        ├── csp_model.py                # CellVariable, RunConstraint, KakuroCSP
        ├── propagation.py              # SumPartitionCatalog, ForwardChecker, ExtendedAC3Propagator
        ├── solver.py                   # KakuroSolver (3 chế độ, MRV/Bậc/LCV, iter_steps, cancel_event)
        ├── board_editor.py             # BoardEditor (tạo bảng, Bulk Edit, sinh gợi ý mới, JSON I/O)
        ├── visualizer_ui.py            # Giao diện PyGame tối giản KakuroVisualizerUI (1160x720)
        ├── main_task3.py               # Điểm khởi chạy PyGame, --explain-csp, --cli, --verify
        └── experiments_task3.ipynb     # Notebook thực nghiệm Task 3 (đã lưu đủ 100% outputs)
```

---

## 4. Cài Đặt Môi Trường

Mở Terminal (**macOS 13.7.8 / Linux**) hoặc PowerShell (**Windows**) tại thư mục gốc dự án:

### Trên macOS 13.7.8 (Intel Core i5) / Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirement.txt
```

### Trên Windows (PowerShell)
```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirement.txt
```
*(Nếu trên máy Windows đã cài sẵn môi trường ở `F:\Python311\python.exe`, có thể thay `python` trong các câu lệnh bên dưới bằng `& "F:\Python311\python.exe"`.)*

### Kiểm chứng nhanh toàn bộ hệ thống (33 tiêu chí tự động)
```bash
python source/task1/main_task1.py --verify
python source/task2/main_task2.py --verify
python source/task3/main_task3.py --verify
```
Kết quả kỳ vọng: Task 1 đạt **`5/5`**, Task 2 đạt **`6/6`**, Task 3 đạt **`22/22`** (100% ASCII thuần, không lỗi font).

---

## 5. Hướng Dẫn Chạy Chi Tiết Từng Nhiệm Vụ

Đứng tại thư mục gốc dự án để thực thi các lệnh dưới đây.

### 5.1. Nhiệm vụ 1 — Bài Toán N Quân Hậu (`source/task1/`)

#### A. Mở giao diện PyGame tối giản (`MinimalNQueenUI` — `1160 × 720`)
```bash
python source/task1/main_task1.py
```
- **Thao tác:** Chọn nhanh $N \in \{4, 8, 12, 16, 20, 32, 50\}$ hoặc điều chỉnh tự do $N \in [4, 100]$ qua nút `-`/`+`; chọn 4 thuật toán (`Glucose3`, `Min-Conflicts tiêu chuẩn`, `Max-Conflict thuần`, `Max-Conflict + Tabu thích nghi`); hỗ trợ **Giải ngay** (`Enter`), **Ngẫu nhiên** (`R`), **Từng bước** (`Phải`/`S`), **Phát / Tạm dừng** (`Space`), thanh tốc độ (`1–60 bước/giây`), và nút **So sánh** đối chứng trực tiếp bản chuẩn vs. đề xuất trên cùng bàn cờ.
- **Trực quan hóa:** Vương miện hậu vector (xanh ngọc khi hợp lệ, đen khi an toàn, đỏ gạch trên nền đỏ nhạt kèm **tia tấn công nét đứt** khi $N \le 20$, viền đậm `2px` tại cột vừa dời) và bảng phân rã mệnh đề `ALO`/`AMO` + thống kê CDCL của `Glucose3`.

#### B. Dòng lệnh CLI (ASCII không dấu) & Xuất ảnh headless
```bash
python source/task1/main_task1.py --explain-cnf 4
python source/task1/main_task1.py --cli
python source/task1/main_task1.py --verify
python source/task1/main_task1.py --headless-screenshot preview_t1.png --screenshot-mode conflicts
```

---

### 5.2. Nhiệm vụ 2 — Trò Chơi Đấu Tăng (`source/task2/`)

#### A. Mở giao diện đấu trường PyGame vector tối giản (`TankBattleArenaUI` — `1160 × 720`)
```bash
python source/task2/main_task2.py
```
- **Thao tác:** Đổi 6 kịch bản Tầng 1 (`7×7`) và Tầng 2 (`9×9`, `11×11`); chọn bộ điều khiển `MAX`/`MIN` giữa 4 cấu hình thuật toán, `Người chơi (Bàn phím)` (`WASD`/mũi tên đi, `Space` bắn, `Enter` chờ) hoặc các bot nhóm ngoài; nhấn **Nạp lại Bot nhóm ngoài** để quét nạp nóng từ `external_agents/`; điều khiển **Tự chạy / Tạm dừng** (`Space`), **Từng bước** (`→`), **Đặt lại** (`R`) và thanh tốc độ (`60–800 ms/lượt`).

#### B. Tích hợp thuật toán của nhóm sinh viên khác vào thi đấu (`external_agents/`)
Chép tệp `.py` của nhóm khác vào `source/task2/agents/external_agents/` và bấm **Nạp lại Bot nhóm ngoài**. Hệ thống hỗ trợ tự động 2 chuẩn và bọc lớp cách ly `GameState` bất biến + `safe_choose_action()`:
1. **Chuẩn OOP:** Kế thừa `BaseTankAgent` và ghi đè `choose_action(self, state: GameState) -> str` (xem `sample_oop_bot.py`).
2. **Chuẩn Dict Adapter:** Khai báo `BOT_NAME` và hàm `get_action(obs: dict) -> str` trả về 1 trong 6 hành động `"MOVE_UP"`, `"MOVE_DOWN"`, `"MOVE_LEFT"`, `"MOVE_RIGHT"`, `"FIRE"`, `"STAY"` (xem `sample_dict_bot.py`).

#### C. Dòng lệnh CLI (ASCII không dấu) & Xuất ảnh headless
```bash
python source/task2/main_task2.py --explain-model
python source/task2/main_task2.py --cli
python source/task2/main_task2.py --verify
python source/task2/main_task2.py --headless-screenshot preview_t2.png --map crossfire_9x9 --turns 9
```

---

### 5.3. Nhiệm vụ 3 — Câu Đố Kakuro CSP (`source/task3/`)

#### A. Mở giao diện PyGame tối giản & Trình soạn thảo (`KakuroVisualizerUI` — `1160 × 720`)
```bash
python source/task3/main_task3.py
```
- **Trực quan hóa 3 tông tối giản:**
  - Ô trắng chưa gán hiển thị **lưới ứng viên $3\times 3$ (`1..9`)** màu xám trung tính; chữ số cho trước (`given`) màu mực đen kèm ký hiệu góc `G`; chữ số đã gán hợp lệ màu xanh ngọc trầm (`#0F766E`).
  - **Viền đậm `#111827` trên nền xám nhạt:** Ô biến đang được chọn (`SELECT_VAR` / `ASSIGN`).
  - **Chữ số đỏ gạch chéo (`#C83E37`):** Ứng viên bị cắt tỉa khi lan truyền (`PRUNE`); dấu `×` đỏ trên nền đỏ nhạt báo miền rỗng; nền/viền đỏ nhạt đánh dấu `REJECT` / `FAILURE` / `BACKTRACK`.
- **Chế độ Giải:** Chọn nhanh 4 bảng mẫu (`5×5`, `6×6`, `8×8`, `9×9`), chọn 3 chế độ giải (`Quay lui cơ bản`, `Kiểm tra tiến + MRV`, `AC-3 mở rộng + MRV/Bậc/LCV`), điều khiển **Phát / Tạm dừng** (`Space`), **Bước tiếp / Trước** (`Phải`/`Trái`), **Đặt lại** (`0`), **Bước cuối**, **Giải lại**, thanh tốc độ (`25–1000 ms/bước`) và **Sửa bảng / Dừng & Sửa bảng** (`Esc` — hủy luồng giải nền an toàn).
- **Chế độ Soạn thảo (`BoardEditor`) & Sửa nhanh (`Bulk Edit`):** Tạo bảng `3×3..9×9`, đổi `Ô trắng`/`Ô đen / gợi ý` tự đồng bộ dãy, nhập `Tổng ngang`/`Tổng dọc` hoặc `Số cho trước`, **Sửa nhanh (Bulk)** nhập đồng thời nhiều dòng (`#`, `0`, `1–9`, `N/D`), **Sinh gợi ý mới** đảm bảo có nghiệm, **Kiểm tra hợp lệ**, **Lưu JSON / Mở JSON** tại `maps/custom/` và **Giải bảng hiện tại**.

#### B. Dòng lệnh CLI (ASCII không dấu) & Xuất ảnh headless
```bash
python source/task3/main_task3.py --explain-csp
python source/task3/main_task3.py --cli --trials 10
python source/task3/main_task3.py --verify
python source/task3/main_task3.py --headless-screenshot preview_t3.png --screenshot-mode prune
```

---

## 6. Kiểm Tra 3 Sổ Tay Thực Nghiệm Jupyter (`.ipynb`)

Cả 3 sổ tay thực nghiệm đã được chạy hoàn chỉnh không lỗi và **lưu nguyên 100% kết quả đầu ra (bảng số liệu + biểu đồ) ở toàn bộ các cell** theo đúng quy định Mục III đề bài:
1. [source/task1/experiments_task1.ipynb](source/task1/experiments_task1.ipynb)
2. [source/task2/benchmark_task2.ipynb](source/task2/benchmark_task2.ipynb)
3. [source/task3/experiments_task3.ipynb](source/task3/experiments_task3.ipynb)

Mở trực tiếp bằng VS Code hoặc chạy `jupyter lab` tại thư mục gốc để xem chi tiết.

---

## 7. Biên Dịch Báo Cáo IEEE (Task 4) Trên Overleaf & Quy Cách Nộp Bài

### 7.1. Biên dịch `report.pdf` thủ công trên Overleaf
Xem hướng dẫn chi tiết cùng mã nguồn copy–paste trong [report.md](report.md):
1. Nén nội dung thư mục `report/` (`main.tex`, `references.bib` và thư mục `figures/` gồm **8 ảnh PNG**) thành file `.zip`, mở Overleaf chọn **New Project → Upload Project** *(hoặc tạo Blank Project, copy–paste Phần 3 & Phần 4 từ `report.md` và upload 8 ảnh vào thư mục `figures/`)*.
2. Giữ trình biên dịch **pdfLaTeX** (mặc định của Overleaf), kiểm tra lại danh sách tác giả (4 thành viên + **TS. Trịnh Hùng Cường** ở vị trí cuối cùng) và xác nhận độ dài báo cáo **$\le 5$ trang** (2 cột chuẩn IEEE).
3. Nhấn **Recompile**, tải PDF về và lưu đè thành `report.pdf` tại thư mục gốc dự án.

### 7.2. Đóng gói nộp bài cá nhân (theo Mục III `DEBAI.md`)
1. Cập nhật đường dẫn URL công khai của video demo vào [demo.txt](demo.txt).
2. Mỗi thành viên tự tạo thư mục đặt đúng tên `AI_final_<Project_Group_ID>_<Student_ID>` chứa đầy đủ:
   - `source/` *(đã dọn sạch `__pycache__`, giữ nguyên `source/README.md`, `source/requirement.txt` và 100% outputs trong 3 file `.ipynb`)*
   - `report.pdf`
   - `demo.txt`
   - `README.md` và `requirement.txt`
3. Nén thành tệp `.zip` tương ứng với MSSV cá nhân (`52400010`, `52400153`, `5240110`, `52400105`) và nộp lên hệ thống trước thời hạn.
