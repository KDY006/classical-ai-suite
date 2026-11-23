# Đồ Án Cuối Kỳ: Nhập Môn Trí Tuệ Nhân Tạo (503043)

Dự án cài đặt trọn vẹn 3 bài toán Trí tuệ Nhân tạo cổ điển theo nguyên lý **Lập trình hướng đối tượng (OOP)** bằng ngôn ngữ Python cho môn học **503043 – Introduction to Artificial Intelligence** (Khoa Công nghệ Thông tin – Đại học Tôn Đức Thắng):

- **Task 1 (3.0 điểm) – Bài toán N-Queen**: Mô hình hóa Logic mệnh đề dạng chuẩn hội (CNF) giải bằng bộ giải `Glucose3` (`PySAT`) và Tìm kiếm cục bộ `Min-Conflicts` kết hợp Heuristic đề xuất (*Max-Conflict + Danh sách cấm ngắn hạn Tabu & Điều kiện ân xá Aspiration*).
- **Task 2 (3.0 điểm) – Trò chơi Tank Battle (Tìm kiếm đối kháng)**: Mô hình hóa trò chơi tổng bằng không (*Zero-Sum Game*) với cơ chế đạn bay xuyên lượt 3 ô/chu kỳ kiểm tra va chạm từng ô một, thực nghiệm đối sánh 4 cấu hình thuật toán (`Minimax`, `Alpha-Beta`, `Heuristic Minimax`, `Heuristic Alpha-Beta`), kèm giao diện **PyGame Arena** hỗ trợ nạp động thuật toán của các nhóm sinh viên khác vào thi đấu.
- **Task 3 (3.0 điểm) – Trò chơi Kakuro (Thỏa mãn ràng buộc – CSP)**: Mô hình hóa CSP $\langle X, D, C \rangle$, kết hợp tiền xử lý tổ hợp tổng (*Sum Partitions*), lan truyền ràng buộc (*Forward Checking* & *Extended AC-3*) với bộ ba heuristic (*MRV*, *Degree*, *LCV*), kèm giao diện **PyGame Visualizer** trực quan hóa miền giá trị ứng viên $\{1..9\}$, quá trình cắt tỉa miền và quá trình quay lui (*Backtracking*).
- **Task 4 (1.0 điểm) – Báo cáo khoa học IEEE & Video Demo**: Mã nguồn báo cáo chuẩn hội nghị IEEE 2 cột (tối đa 05 trang) sẵn sàng biên dịch trên Overleaf.

---

## 1. Yêu Cầu Hệ Thống & Cài Đặt Môi Trường

### 1.1. Yêu cầu phiên bản Python
- Khuyến nghị sử dụng **Python 3.10, 3.11 hoặc 3.12** (để thư viện `python-sat` và `pygame` có sẵn gói cài đặt nhị phân prebuilt wheel trên cả **macOS 13.7.8 Intel Core i5**, **Windows** và **Linux** mà không cần biên dịch C++).
- Toàn bộ đường dẫn file trong dự án sử dụng `pathlib.Path` chuẩn đa nền tảng, tương thích 100% với cấu hình chấm bài **macOS 13.7.8 (Ventura) – Intel Core i5** của giảng viên.

### 1.2. Cách 1: Cài đặt trên môi trường ảo chuẩn (Khuyến nghị trên macOS / Linux / Windows)

Mở Terminal (trên macOS/Linux) hoặc PowerShell/CMD (trên Windows) tại thư mục gốc của dự án:

**Trên macOS 13.7.8 / Linux:**
```bash
# Bước 1: Tạo môi trường ảo Python
python3 -m venv .venv

# Bước 2: Kích hoạt môi trường ảo
source .venv/bin/activate

# Bước 3: Nâng cấp pip và cài đặt toàn bộ thư viện bắt buộc
pip install --upgrade pip
pip install -r requirement.txt
```

**Trên Windows (PowerShell):**
```powershell
# Bước 1: Tạo môi trường ảo (dùng Python 3.11 nếu máy cài nhiều bản Python)
py -3.11 -m venv .venv
# Hoặc nếu chỉ có 1 bản Python chuẩn: python -m venv .venv

# Bước 2: Kích hoạt môi trường ảo
.\.venv\Scripts\Activate.ps1

# Bước 3: Cài đặt toàn bộ thư viện trong requirement.txt
pip install -r requirement.txt
```

### 1.3. Cách 2: Chạy trực tiếp bằng Python 3.11 sẵn có trên máy hiện tại
Nếu trên máy Windows của bạn đã cài đặt sẵn các thư viện trong `F:\Python311\python.exe`, bạn có thể gọi trực tiếp trình thông dịch này mà không cần tạo lại môi trường ảo:
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
├── report/                             # Thư mục báo cáo khoa học chuẩn IEEE (Task 4)
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
    │   ├── main_task1.py               # Chương trình chạy thực nghiệm nhanh Task 1 trên dòng lệnh
    │   ├── gui.py                      # Giao diện bàn cờ N-Queen
    │   └── experiments_task1.ipynb     # Notebook thực nghiệm Task 1
    ├── task2/                          # TASK 2: Trò chơi Tank Battle (Tìm kiếm đối kháng & PyGame)
    │   ├── config.py                   # Hằng số trò chơi (Tank=6 HP, Base=9 HP, Wall=3 HP, Speed=3)
    │   ├── engine/
    │   │   ├── entities.py             # Các lớp thực thể OOP: Tank, Base, BrickWall, SteelWall, Bullet
    │   │   ├── game_state.py           # Lớp GameState (trạng thái Zero-Sum, sao chép nhanh, kiểm tra kết thúc)
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
    │   │   └── pygame_arena.py         # Giao diện đồ họa PyGame Arena trực quan
    │   ├── main_task2.py               # Điểm khởi chạy giao diện PyGame hoặc benchmark dòng lệnh Task 2
    │   └── benchmark_task2.ipynb       # Jupyter Notebook thực nghiệm 4 cấu hình Task 2 (giữ nguyên output)
    └── task3/                          # TASK 3: Câu đố Kakuro (CSP & Giao diện trực quan hóa)
        ├── maps/                       # Dữ liệu bản đồ Kakuro định dạng JSON
        │   ├── board_5x5_example.json  # Bảng ví dụ 5x5 trang 4 đề bài (12 ô trắng, tổng = 60)
        │   ├── board_9x9_complex.json  # Bảng kiểm thử phức tạp 9x9 trang 5 đề bài (48 ô trắng, tổng = 249)
        │   ├── board_6x6_medium.json   # Bảng kiểm thử độ ổn định 6x6 (19 ô trắng)
        │   └── board_8x8_hard.json     # Bảng kiểm thử độ ổn định 8x8 (41 ô trắng)
        ├── csp_model.py                # Các lớp OOP: CellVariable, RunConstraint, KakuroCSP
        ├── propagation.py              # Tiền xử lý Sum Partitions, Forward Checking & Extended AC-3
        ├── solver.py                   # Bộ giải KakuroSolver tích hợp MRV, Degree Heuristic và LCV
        ├── visualizer_ui.py            # Giao diện PyGame hiển thị miền giá trị {1..9}, cắt tỉa & quay lui
        ├── main_task3.py               # Điểm khởi chạy giao diện Kakuro Visualizer hoặc benchmark CLI
        └── experiments_task3.ipynb     # Jupyter Notebook đánh giá Task 3 (giữ nguyên output)
```

---

## 3. Hướng Dẫn Chi Tiết Cách Chạy Từng Task

Bạn có thể đứng tại thư mục gốc của dự án để chạy các câu lệnh dưới đây (trên máy của bạn hiện tại, có thể thay chữ `python` bằng `& "F:\Python311\python.exe"` nếu chưa kích hoạt `.venv`).

---

### 3.1. Chạy Task 1: Bài Toán N-Queen (`Glucose3` SAT & `Min-Conflicts`)

Mở giao diện bàn cờ:

```bash
python source/task1/gui.py
```

#### A. Chạy chương trình thực nghiệm dòng lệnh (CLI)
```bash
python source/task1/main_task1.py
```
Khi chạy lệnh trên, chương trình sẽ tự động thực hiện:
1. Mã hóa bài toán N-Queen sang dạng chuẩn hội (CNF) và giải bằng `Glucose3` (`PySAT`) với các kích thước $N \in \{4, 8, 12, 16, 20, 30, 40, 50\}$, in bảng thống kê số biến ($N^2$), tổng số mệnh đề CNF, thời gian mã hóa, thời gian giải và kiểm chứng tính hợp lệ của nghiệm.
2. In trực quan bàn cờ mẫu $8 \times 8$ tìm được bởi `Glucose3`.
3. Chạy thực nghiệm đối sánh công bằng trên cùng tập trạng thái khởi tạo ngẫu nhiên giữa **Min-Conflicts tiêu chuẩn** và **Heuristic đề xuất (Max-Conflict + Tabu)** với $N \in \{8, 16, 32, 64, 100\}$, báo cáo tỷ lệ thành công (`Success Rate`), số bước sửa trung bình (`Avg Steps`) và thời gian chạy (`Avg Time`).

#### B. Tùy chỉnh tham số dòng lệnh cho Task 1
Bạn có thể truyền tham số tùy chỉnh kích thước bàn cờ, số lần chạy lặp và số bước tối đa:
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
- **Nút `Map: ...`**: Nhấn chuột để chuyển đổi qua lại giữa 6 kịch bản bản đồ:
  - *Classic Battle City (9x9)*, *Open Crossfire (9x9)*, *Fortress Siege (11x11)* (Bản đồ đầy đủ máu: Tank = 6 HP, Base = 9 HP, Tường gạch = 3 HP).
  - *Endgame Center Duel (7x7)*, *Endgame Base Race (7x7)*, *Endgame Corner Ambush (7x7)* (Kịch bản sát nút dùng để kiểm thử cả Minimax thuần và Alpha-Beta thuần).
- **Nút `MAX: ...` (Xe tăng Xanh – Người chơi 1)** và **`MIN: ...` (Xe tăng Đỏ – Người chơi 2)**: Nhấn để chọn thuật toán điều khiển cho từng bên, bao gồm:
  - `Heuristic Alpha-Beta (d=4)`
  - `Heuristic Minimax (d=3)`
  - `Pure Alpha-Beta (cap=6)`
  - `Pure Minimax (cap=5)`
  - `Human (WASD + Space)` (Chế độ người chơi trực tiếp bằng bàn phím!)
  - Các bot của nhóm khác nằm trong thư mục `external_agents/` (ví dụ: `Ext: BaseHunter (Dict API)`, `Ext: GreedyStriker (OOP)`).
- **Nút `Auto Play / Pause`**: Tự động chạy liên tục trận đấu giữa 2 AI hoặc tạm dừng.
- **Nút `Step 1 Turn`**: Chạy từng lượt một để quan sát kỹ hướng xoay xe tăng, đường đạn bay 3 ô/chu kỳ và thông số duyệt cây tìm kiếm ở bảng bên phải.
- **Nút `Reset Match`**: Khởi tạo lại ván đấu về trạng thái ban đầu.
- **Nút `Speed -` / `Speed +`**: Giảm hoặc tăng tốc độ diễn hoạt giữa các lượt.
- **Nút `Reload external_agents/*.py`**: Quét và nạp lại ngay lập tức các file bot mới vừa được chép vào thư mục `source/task2/agents/external_agents/` mà không cần tắt game.
- **Phím tắt khi chọn chế độ `Human (WASD + Space)`**:
  - `W` / `Mũi tên Lên`: `MOVE_UP`
  - `S` / `Mũi tên Xuống`: `MOVE_DOWN`
  - `A` / `Mũi tên Trái`: `MOVE_LEFT`
  - `D` / `Mũi tên Phải`: `MOVE_RIGHT`
  - `Space` (Phím cách): `FIRE` (Bắn đạn)
  - `Enter`: `STAY` (Đứng yên)
  - `ESC`: Thoát cửa sổ game.

#### B. Chạy Benchmark đối sánh 4 thuật toán trên Terminal (Không mở cửa sổ đồ họa)
```bash
python source/task2/main_task2.py --cli
```

#### C. Hướng dẫn tích hợp thuật toán của nhóm sinh viên khác vào thi đấu (Yêu cầu 2.3)
Để đưa thuật toán của một nhóm khác vào thi đấu trên cùng môi trường, chỉ cần chép file `.py` của nhóm đó vào thư mục `source/task2/agents/external_agents/`. Hệ thống hỗ trợ tự động **2 chuẩn giao tiếp**:

- **Chuẩn 1 – Kế thừa lớp OOP `BaseTankAgent`** (xem mẫu tại `source/task2/agents/external_agents/sample_oop_bot.py`):
  ```python
  from task2.agents.base_agent import BaseTankAgent
  from task2.engine.game_state import GameState

  class MyGroupTankBot(BaseTankAgent):
      def __init__(self) -> None:
          super().__init__(name="Group 02 Bot")

      def choose_action(self, state: GameState) -> str:
          # Trả về 1 trong 6 chuỗi: "MOVE_UP", "MOVE_DOWN", "MOVE_LEFT", "MOVE_RIGHT", "FIRE", "STAY"
          return "FIRE"
  ```
- **Chuẩn 2 – Hàm độc lập `get_action(obs_dict)` không phụ thuộc class nội bộ** (xem mẫu tại `source/task2/agents/external_agents/sample_dict_bot.py`):
  ```python
  BOT_NAME = "Group 03 Bot"

  def get_action(obs: dict) -> str:
      # obs chứa toàn bộ thông tin: rows, cols, current_player, tanks, bases, brick_walls, steel_walls, bullets, legal_actions
      legal = obs["legal_actions"]
      return "FIRE" if "FIRE" in legal else legal[0]
  ```

---

### 3.3. Chạy Task 3: Trò Chơi Kakuro (Bộ Giải CSP & Giao Diện Trực Quan Hóa)

#### A. Khởi chạy Giao diện Trực quan hóa PyGame Kakuro Visualizer (Yêu cầu 3.3)
```bash
python source/task3/main_task3.py
```
**Hướng dẫn sử dụng bảng điều khiển trên cửa sổ Kakuro Visualizer:**
- **Hiển thị trực quan trên lưới Kakuro**:
  - **Ô đen có gạch chéo**: Nửa dưới bên trái (màu xanh nhạt) là tổng gợi ý cột dọc (`down`); nửa trên bên phải (màu vàng) là tổng gợi ý hàng ngang (`across`).
  - **Ô trắng chưa gán giá trị**: Hiển thị **lưới ứng viên $3 \times 3$ các chữ số từ `1` đến `9`** đang còn nằm trong miền giá trị hiện tại $D_i$ của biến đó.
  - **Viền Xanh Dương (`SELECT_VAR` / `ASSIGN`)**: Biến đang được chọn bởi heuristic **MRV + Degree** và giá trị đang thử gán theo thứ tự **LCV**.
  - **Nền Hồng + Chữ số Đỏ (`PRUNE`)**: Hiển thị trực tiếp các chữ số ứng viên vừa bị loại bỏ khỏi miền giá trị bởi quá trình **Lan truyền ràng buộc (Constraint Propagation)**.
  - **Viền Cam (`BACKTRACK`)**: Phát hiện ngõ cụt (miền rỗng) và thực hiện thao tác quay lui, khôi phục lại miền giá trị trước đó.
  - **Nền Xanh Lá (`SOLVED`)**: Bàn cờ đã được giải hoàn tất và vượt qua bước kiểm tra 100% ràng buộc `AllDiff` + `Exact Sum`.
- **Các nút điều khiển bên phải**:
  - **`Board: ...`**: Chuyển đổi qua lại giữa 4 bảng câu đố: *Example Board (5x5 - Spec Page 4)*, *Complex Test Board (9x9 - Spec Page 5)*, *Medium Benchmark Board (6x6)* và *Hard Benchmark Board (8x8)*.
  - **`Mode: ...`**: Chuyển đổi giữa 3 cấp độ thuật toán giải để quan sát sự khác biệt:
    1. `BT + Extended AC-3 + MRV/Degree/LCV` (Giải bảng `9x9` chỉ với đúng 48 nút, 0 lần quay lui).
    2. `Backtracking + Forward Checking` (Rất trực quan để xem cả hiệu ứng cắt tỉa miền màu đỏ lẫn các bước quay lui màu cam).
    3. `Baseline Backtracking` (Quay lui cơ bản không cắt tỉa miền).
  - **`Auto Play / Pause`** (hoặc phím `Space`): Tự động chạy từng bước giải.
  - **`Step <` / `Step >`** (hoặc phím mũi tên `Trái` / `Phải`): Lùi 1 bước hoặc tiến 1 bước để phân tích chi tiết từng thao tác của thuật toán.
  - **`Reset (0)`**: Quay về bước khởi tạo đầu tiên.
  - **`Speed -` / `Speed +`**: Điều chỉnh tốc độ chạy tự động.
  - **`Jump to Solved State`**: Nhảy tới ngay trạng thái nghiệm hoàn chỉnh cuối cùng.

#### B. Chạy Benchmark đánh giá bộ giải Kakuro trên Terminal (CLI)
```bash
python source/task3/main_task3.py --cli
```

---

## 4. Hướng Dẫn Mở & Chạy Các File Jupyter Notebook Thực Nghiệm (`.ipynb`)

Theo quy định nộp bài tại Mục III của đề bài, cả 3 file Notebook dưới đây **đã được chạy sẵn và lưu nguyên vẹn 100% kết quả đầu ra (bảng số liệu + biểu đồ) ở tất cả các cell**:
1. `source/task1/experiments_task1.ipynb`
2. `source/task2/benchmark_task2.ipynb`
3. `source/task3/experiments_task3.ipynb`

Nếu muốn mở xem hoặc chạy lại trên máy:
- **Cách 1 (Trong Visual Studio Code)**: Mở trực tiếp file `.ipynb` trong VS Code, chọn Kernel Python (ví dụ `.venv` hoặc `Python 3.11.9 (F:\Python311\python.exe)`).
- **Cách 2 (Bằng Jupyter Lab / Jupyter Notebook trên trình duyệt)**:
  ```bash
  jupyter lab
  # Hoặc: jupyter notebook
  ```

---

## 5. Hướng Dẫn Biên Dịch Báo Cáo IEEE (Task 4) & Đóng Gói Nộp Bài

### 5.1. Biên dịch báo cáo `report.pdf` trên Overleaf
1. Truy cập [Overleaf](https://www.overleaf.com/), chọn **New Project** $\to$ **Upload Project** (hoặc tạo Blank Project).
2. Tải lên toàn bộ các file trong thư mục `report/` bao gồm:
   - `main.tex`
   - `references.bib`
   - Thư mục `figures/` (chứa các ảnh biểu đồ thực nghiệm `.png`).
3. Mở `main.tex`, thay thế Họ tên, Mã số sinh viên và Email thực tế của 4 thành viên trong nhóm ở khối `\author{...}` (giữ nguyên tên giảng viên hướng dẫn **Thanh-An Nguyen** ở vị trí tác giả cuối cùng theo đúng yêu cầu đề bài).
4. Nhấn **Recompile** và tải file PDF xuống, đổi tên thành `report.pdf` và đặt vào thư mục gốc của dự án.

### 5.2. Cập nhật link video demo và nén file nộp bài cá nhân
1. Dán đường dẫn công khai (YouTube Unlisted hoặc Google Drive đã bật quyền *Anyone with the link can view*) của video demo vào file `demo.txt`.
2. Mỗi thành viên tạo bản sao thư mục dự án, đặt tên thư mục và nén thành file `.zip` theo đúng cú pháp bắt buộc:
   ```text
   AI_final_<Project Group ID>_<Student ID>.zip
   ```
   *(Ví dụ: `AI_final_Group05_52400001.zip`)*.
