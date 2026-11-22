# Đặc Tả Kỹ Thuật & Kế Hoạch Triển Khai Đồ Án Cuối Kỳ AI (503043)

Tài liệu đặc tả thiết kế kỹ thuật, kiến trúc OOP, phân công nhóm 4 thành viên và lộ trình 6 tuần cho môn **503043 – Introduction to Artificial Intelligence** (Khoa CNTT – Đại học Tôn Đức Thắng).

---

## 1. Ràng Buộc Kỹ Thuật & Cấu Trúc Chung

- **Ngôn ngữ & Thiết kế**: Python 3.10+ thiết kế chuẩn Lập trình hướng đối tượng (OOP), tương thích hoàn toàn với **macOS 13.7.8 (Ventura) – Intel Core i5** và Windows/Linux (`pathlib.Path`, không phụ thuộc đường dẫn cứng).
- **Thư viện cốt lõi (`requirement.txt`)**: `python-sat`, `pygame`, `numpy`, `matplotlib`, `jupyter`, `nbclient`.
- **Cấu trúc nộp bài**: Mỗi thành viên nén thư mục theo định dạng `AI_final_<Project Group ID>_<Student ID>.zip` gồm `source/` (chứa `task1/`, `task2/`, `task3/`, `README.md`, `requirement.txt` và các file `.ipynb` giữ nguyên cell outputs), `report.pdf` (chuẩn IEEE 2 cột ≤ 5 trang), và `demo.txt`.

---

## 2. Đặc Tả Kỹ Thuật 3 Bài Toán Lập Trình

### 2.1. Task 1 (3.0 điểm): N-Queen — Propositional Logic & Local Search
1. **Mô hình hóa Logic mệnh đề & CNF (1.0đ)**:
   - Mỗi ô `(r, c)` ứng với biến mệnh đề `P(r, c)` có mã DIMACS `id(r, c) = r * N + c + 1` (`1 .. N^2`).
   - Ràng buộc *At-Least-One* cho từng hàng (và cột) cùng ràng buộc *At-Most-One* nhị nguyên `(~P(r1,c1) v ~P(r2,c2))` cho mọi cặp ô cùng hàng, cùng cột, cùng đường chéo chính và đường chéo phụ.
2. **Giải bằng `Glucose3` từ `PySAT` (1.0đ)**:
   - Thực nghiệm với `N` tăng dần (`N >= 4` đến `N = 60`), thống kê số biến, tổng số mệnh đề CNF và thời gian giải của `Glucose3`.
3. **Min-Conflicts & Heuristic đề xuất (1.0đ)**:
   - Biểu diễn 1 quân hậu/cột với bảng băm đếm xung đột hàng/chéo trong `O(1)`.
   - Đề xuất Heuristic **`TabuMaxConflict`** (ưu tiên biến có số xung đột lớn nhất kết hợp danh sách cấm ngắn hạn `Tabu Tenure` và điều kiện ân xá `Aspiration` khi triệt tiêu hoàn toàn xung đột), đối sánh công bằng với Min-Conflicts chuẩn trên cùng tập `seed` khởi tạo (`N = 8 .. 150`).

### 2.2. Task 2 (3.0 điểm): Tank Battle — Adversarial Search & PyGame
1. **Mô hình Zero-Sum Game (1.0đ)**:
   - Thông số: `Tank (HP=6, Dmg=1)`, `Base (HP=9, Dmg=1)`, `BrickWall (HP=3, Dmg=1)`, `SteelWall (bất tử - tùy chọn bản đồ)`.
   - 6 hành động: `MOVE_UP`, `MOVE_DOWN`, `MOVE_LEFT`, `MOVE_RIGHT`, `FIRE`, `STAY`. `MOVE_DIR` cập nhật hướng quay mặt sang `DIR` và tiến 1 ô nếu trống.
   - Đạn tồn tại xuyên lượt (*Persistent Bullet*, tối đa 1 viên đang bay/xe), di chuyển tốc độ **3 ô/chu kỳ**, kiểm tra va chạm tuần tự từng ô một (`cell-by-cell`) và dừng ngay khi trúng vật thể.
   - Kết thúc khi một `Base` hoặc `Tank` về `0 HP`; tiện ích `+1000` (`MAX` thắng), `-1000` (`MIN` thắng), `0` (hòa).
2. **4 cấu hình thuật toán & Thực nghiệm 2 tầng (1.5đ)**:
   - Cài đặt: `MinimaxAgent`, `AlphaBetaAgent`, `HeuristicMinimaxAgent`, `HeuristicAlphaBetaAgent` (kèm `Move Ordering` và `Transposition Table`).
   - Thực nghiệm Tầng 1 trên bộ thế cờ *Endgame sát nút* (`7×7`, `1–2 HP`) để cả 4 thuật toán duyệt tới trạng thái kết thúc thật; Tầng 2 trên bản đồ chuẩn (`9×9`, `11×11` đầy máu) đo hiệu năng cắt độ sâu thời gian thực.
3. **PyGame Arena & Nạp thuật toán nhóm ngoài (0.5đ)**:
   - Tự động nạp file `.py` từ `source/task2/agents/external_agents/` hỗ trợ cả kế thừa `BaseTankAgent` lẫn hàm `get_action(obs_dict)`, truyền bản sao sâu chống sửa trạng thái gốc, hỗ trợ đấu `Human vs AI` và `AI vs AI`.

### 2.3. Task 3 (3.0 điểm): Kakuro — CSP Solver & Visualization UI
1. **Mô hình hóa CSP & Bộ giải (2.0đ)**:
   - Chính xác hóa dữ liệu đề gốc: Bảng mẫu `5×5` có **12 biến ô trắng** (tổng gợi ý = `60`); bảng phức tạp `9×9` có **48 biến ô trắng** (tổng gợi ý = `249`), kèm thêm bảng `6×6` và `8×8` kiểm chứng độ ổn định.
   - 3 cấp độ giải: `Plain Backtracking`, `Backtracking + Forward Checking`, và `Backtracking + Extended AC-3 (Sum Partitions + cận tổng min/max + Alldiff) + MRV + Degree + LCV`.
2. **Giao diện trực quan hóa bằng PyGame (1.0đ)**:
   - Vẽ ô đen chéo chuẩn Kakuro, lưới ứng viên `3×3` (`{1..9}`) trong từng ô trắng, đổi màu trực quan biến chọn bởi MRV, giá trị bị cắt tỉa bởi Constraint Propagation và bước quay lui Backtracking; hỗ trợ `Step`, `Auto Play`, thanh trượt tốc độ, đổi thuật toán và đổi bản đồ.

---

## 3. Phân Công Nhóm 4 Thành Viên & Lộ Trình 06 Tuần

- **Thành viên 1 (Project Lead)**: Phụ trách trọn vẹn **Task 1**, thiết lập Git repo, `README.md`, `requirement.txt`, và kiểm thử tương thích macOS 13.7.8.
- **Thành viên 2 (Adversarial Search & Engine Lead)**: Phụ trách **Task 2.1 & 2.2** (`engine/`, 4 lớp agent tìm kiếm đối kháng, hàm lượng giá `EVAL(s)`, `benchmark_task2.ipynb`).
- **Thành viên 3 (CSP Core & Benchmark Lead)**: Phụ trách **Task 3.1 & 3.2** (`maps/`, `csp_model.py`, `propagation.py`, `solver.py`, `experiments_task3.ipynb`).
- **Thành viên 4 (UI, Integration & IEEE Report Lead)**: Phụ trách **Task 2.3** (`pygame_arena.py`, plugin `external_agents/`), **Task 3.3** (`visualizer_ui.py`), tổng hợp báo cáo LaTeX IEEE **Task 4** (`report/main.tex` ≤ 5 trang) và video demo.
