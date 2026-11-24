# Đặc Tả Kỹ Thuật & Phân Công Triển Khai Đồ Án Cuối Kỳ AI (503043)

Tài liệu tổng hợp thiết kế toán học, kiến trúc hướng đối tượng (OOP) và phân công thực tế nhóm 4 thành viên cho môn **503043 – Introduction to Artificial Intelligence** (Khoa CNTT – Đại học Tôn Đức Thắng).

---

## 1. Ràng Buộc Kỹ Thuật & Cấu Trúc Chung

- **Ngôn ngữ & Thiết kế**: Python 3.10+ thiết kế chuẩn Lập trình hướng đối tượng (OOP), sử dụng `pathlib.Path` và `from __future__ import annotations` tương thích hoàn toàn với cấu hình chấm bài **macOS 13.7.8 (Ventura) – Intel Core i5**, Windows và Linux.
- **Thư viện cốt lõi (`requirement.txt`)**: `python-sat`, `pygame`, `numpy`, `matplotlib`, `pandas`, `jupyter`, `nbclient`.
- **Cấu trúc nộp bài**: Mỗi thành viên nén thư mục theo định dạng `AI_final_<Project Group ID>_<Student ID>.zip` gồm `source/` (`task1/`, `task2/`, `task3/`, `README.md`, `requirement.txt` và 3 file `.ipynb` lưu nguyên toàn bộ cell outputs), `report.pdf` (chuẩn IEEE 2 cột ≤ 5 trang), và `demo.txt`.

---

## 2. Đặc Tả Kỹ Thuật 3 Bài Toán Lập Trình

### 2.1. Task 1 (3.0 điểm): N-Queen — Propositional Logic & Local Search
1. **Mô hình hóa Logic mệnh đề & CNF (1.0đ)**:
   - Mỗi ô `(r, c)` ứng với biến mệnh đề `P(r, c)` ánh xạ sang số nguyên dương DIMACS `id(r, c) = r * N + c + 1` (`1 .. N^2`).
   - Ràng buộc *At-Least-One* cho từng hàng và từng cột kết hợp ràng buộc *At-Most-One* nhị nguyên `(~P(r1,c1) v ~P(r2,c2))` cho mọi cặp ô cùng hàng, cùng cột, cùng đường chéo chính và đường chéo phụ.
2. **Giải bằng `Glucose3` từ `PySAT` (1.0đ)**:
   - Thực nghiệm với `N` tăng dần từ `N = 4` đến `N = 60`, thống kê số biến, tổng số mệnh đề CNF và thời gian chạy.
3. **Min-Conflicts, Heuristic đề xuất & Giao diện trực quan (1.0đ)**:
   - Biểu diễn trạng thái đầy đủ 1 quân hậu/cột với bảng đếm xung đột cập nhật gia tăng `O(1)`.
   - Đề xuất Heuristic **`TabuMaxConflict`** (ưu tiên cột nhiều xung đột nhất kết hợp danh sách cấm ngắn hạn `Tabu` và điều kiện ân xá `Aspiration`), đối sánh trên 30 bàn cờ khởi tạo ngẫu nhiên dùng chung cho mỗi mức `N = 8 .. 150`, kèm giao diện trực quan `gui.py`.

### 2.2. Task 2 (3.0 điểm): Tank Battle — Adversarial Search & PyGame Arena
1. **Mô hình Zero-Sum Game với Trạng Thái Bất Biến (1.0đ)**:
   - Thực thể bất biến (`frozen=True`): `Tank (HP=6, Dmg=1)`, `Base (HP=9, Dmg=1)`, `BrickWall (HP=3, Dmg=1)`, `SteelWall (bất tử)`.
   - 6 hành động: `MOVE_UP`, `MOVE_DOWN`, `MOVE_LEFT`, `MOVE_RIGHT`, `FIRE`, `STAY`. Đạn tồn tại xuyên lượt (*Persistent Bullet*), tốc độ **3 ô/chu kỳ**, kiểm tra va chạm tuần tự từng ô một (`cell-by-cell`).
2. **4 cấu hình thuật toán & Thực nghiệm 2 tầng (1.5đ)**:
   - Cài đặt `MinimaxAgent`, `AlphaBetaAgent`, `HeuristicMinimaxAgent`, `HeuristicAlphaBetaAgent` (kèm `Move Ordering` và `Transposition Table`).
   - Thực nghiệm Tầng 1 trên bộ thế cờ *Endgame sát nút* (`7×7`, `1–2 HP`) để đối sánh chính xác cả 4 cấu hình; Tầng 2 trên bản đồ chuẩn (`9×9`, `11×11` đầy máu) khảo sát độ sâu `d = 2..4`.
3. **PyGame Arena & Nạp thuật toán nhóm ngoài (0.5đ)**:
   - Giao diện 2 cột tự co giãn tích hợp bộ sprite Kenney (CC0), hỗ trợ `AI vs AI`, `Human vs AI` và nạp động file `.py` từ `external_agents/` theo cả chuẩn OOP `BaseTankAgent` lẫn hàm `get_action(obs_dict)`.

### 2.3. Task 3 (3.0 điểm): Kakuro — CSP Solver, Visualizer & Board Editor
1. **Mô hình hóa CSP & Bộ giải (2.0đ)**:
   - Kiểm thử trên 4 bảng: bảng mẫu `5×5` (**12 biến**, tổng gợi ý `60`), bảng phức tạp `9×9` (**48 biến**, tổng gợi ý `249`), cùng 2 bảng kiểm thử độ ổn định `6×6` (**19 biến**) và `8×8` (**41 biến**).
   - 3 cấp độ giải: `Baseline Backtracking`, `BT + Forward Checking + MRV`, và `BT + Extended AC-3 + MRV/Degree/LCV` (giải toàn bộ các bảng với `0` lần quay lui).
2. **Giao diện PyGame Visualizer & Board Editor (1.0đ)**:
   - Hiển thị lưới ứng viên `3×3` (`{1..9}`), tô màu trực quan biến chọn, ứng viên bị cắt tỉa và bước quay lui trên luồng nền có thể hủy (`Stop & Edit`), tích hợp trình soạn thảo bảng `BoardEditor` (sửa từng ô, `Bulk Edit`, sinh đề ngẫu nhiên, lưu/nạp JSON).

---

## 3. Phân Công Thực Tế Nhóm 4 Thành Viên

| Vai trò & Thành viên | Phạm vi phụ trách chính | Sản phẩm bàn giao |
| :--- | :--- | :--- |
| **Thành viên 1 (Nhóm trưởng)** | Kiến trúc tổng thể OOP, quản lý nhánh & hợp nhất Git, kiểm thử tích hợp đa nền tảng (macOS 13.7.8), biên tập Báo cáo khoa học IEEE (**Task 4**) & Video Demo | Cấu trúc repo gốc, `README.md`, `requirement.txt`, `report/main.tex` (`report.pdf`), `demo.txt`, rà soát tích hợp 3 Task |
| **Thành viên 2 (Quý)** | Phụ trách trọn vẹn **Task 1 (N-Queen)**: mã hóa CNF, bộ giải `Glucose3`, thuật toán `Min-Conflicts` & Heuristic `Max-Conflict + Tabu`, giao diện `gui.py` và thực nghiệm | Toàn bộ `source/task1/*`, `experiments_task1.ipynb` và biểu đồ thực nghiệm Task 1 |
| **Thành viên 3 (Huỳnh Thiện Đức)** | Phụ trách trọn vẹn **Task 2 (Tank Battle)**: lõi mô phỏng bất biến, 4 cấu hình tìm kiếm đối kháng, hàm lượng giá `EVAL(s)`, giao diện PyGame Arena (sprite Kenney) & nạp bot ngoài | Toàn bộ `source/task2/*`, `benchmark_task2.ipynb` và bộ biểu đồ/hình ảnh Task 2 |
| **Thành viên 4 (Lê Tiến Đạt)** | Phụ trách trọn vẹn **Task 3 (Kakuro CSP)**: mô hình CSP, tiền xử lý `Sum Partitions`, `Forward Checking` & `Extended AC-3`, heuristic `MRV/Degree/LCV`, `BoardEditor` & PyGame Visualizer | Toàn bộ `source/task3/*`, `experiments_task3.ipynb` và biểu đồ thực nghiệm Task 3 |
