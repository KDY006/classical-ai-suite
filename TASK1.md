# TỔNG HỢP HOÀN THIỆN NHIỆM VỤ 1 — BÀI TOÁN N QUÂN HẬU (N-QUEEN)

> Tài liệu tổng hợp toàn bộ cơ sở lý thuyết, kiến trúc Lập trình hướng đối tượng (OOP), thiết kế giao diện PyGame tối giản, kết quả thực nghiệm và hướng dẫn kiểm thử cho **Nhiệm vụ 1 (3.0 điểm)** — Học phần **503043: Nhập môn Trí tuệ Nhân tạo** (Đại học Tôn Đức Thắng).

---

## 1. Đối Chiếu Mức Độ Hoàn Thành Theo Đề Bài & Quy Ước Thiết Kế

| Hạng mục yêu cầu | Tiêu chuẩn tham chiếu | Mức độ hoàn thành & sản phẩm bàn giao |
| :--- | :--- | :--- |
| **Yêu cầu 1.1 (1.0đ):** Mô hình Logic mệnh đề, thuật toán phát hiện ràng buộc & chuyển đổi CNF | [DEBAI.md](file:///d:/3.1.%20AI/Final/DEBAI.md) (II.a.1) | **100%** — Tách tường minh `PropositionalVariableMapper`, thuật toán phát hiện 4 họ nhóm tuyến tính $\mathcal{O}(N^2)$ (`discover_constraint_groups`), minh họa từng bước chuyển đổi sang CNF (`explain_cnf_conversion`), mã hóa DIMACS và kiểm chứng công thức đóng trong [cnf_encoder.py](file:///d:/3.1.%20AI/Final/source/task1/cnf_encoder.py). |
| **Yêu cầu 1.2 (1.0đ):** Giải bằng `Glucose3` (`PySAT`), thực nghiệm $N \ge 4$ tăng dần, báo cáo mệnh đề CNF & thời gian | [DEBAI.md](file:///d:/3.1.%20AI/Final/DEBAI.md) (II.a.2) | **100%** — Cài đặt `Glucose3NQueenSolver` trong [sat_solver.py](file:///d:/3.1.%20AI/Final/source/task1/sat_solver.py), đo lặp lấy trung vị 3 lần có warm-up trên 15 mốc $N \in [4, 80]$, thu thập thống kê `decisions`/`conflicts`/`propagations`/`restarts`, kiểm chứng `UNSAT` tại $N=2,3$ và xuất biểu đồ [task1_glucose3_scaling.png](file:///d:/3.1.%20AI/Final/report/figures/task1_glucose3_scaling.png). |
| **Yêu cầu 1.3 (1.0đ):** `Min-Conflicts` (Lecture 08) + đề xuất heuristic chọn biến + thực nghiệm so sánh | [DEBAI.md](file:///d:/3.1.%20AI/Final/DEBAI.md) (II.a.3) | **100%** — Cài đặt `MinConflictsSolver` cùng 3 chiến lược chọn biến (`Min-Conflicts` tiêu chuẩn, `Max-Conflict` thuần đối chứng, `Max-Conflict + Tabu thích nghi` đề xuất) trong [min_conflicts.py](file:///d:/3.1.%20AI/Final/source/task1/min_conflicts.py); đối sánh công bằng trên 50 bàn cờ chung/mức $N \in [8, 200]$ và xuất biểu đồ [task1_min_conflicts_comparison.png](file:///d:/3.1.%20AI/Final/report/figures/task1_min_conflicts_comparison.png). |
| **Nguyên lý OOP & macOS 13.7.8 (Intel Core i5)** | [DEBAI.md](file:///d:/3.1.%20AI/Final/DEBAI.md) (Notice) | **100%** — Kế thừa lớp trừu tượng chung `BaseNQueenSolver` và `VariableSelectionStrategy`, tách rời hoàn toàn Model–View (6 module lõi không import `pygame`), dùng `pathlib.Path`, `from __future__ import annotations`, không dùng `Tkinter`. |
| **Giao diện PyGame phong cách Tối giản** | [UI.md](file:///d:/3.1.%20AI/Final/UI.md) | **100%** — Giao diện [ui_nqueen.py](file:///d:/3.1.%20AI/Final/source/task1/ui_nqueen.py) kích thước chuẩn `1160 × 720`, giới hạn 3 tông màu (Giấy/Mực, Xanh ngọc trầm `#0F766E`, Đỏ gạch trầm `#C83E37`), khoảng trắng rộng kiểu Notion/Medium, hỗ trợ chạy trực tiếp, từng bước, phát tự động, so sánh nhanh và chụp ảnh headless. |
| **Quy ước ngôn ngữ & Cell outputs Notebook** | Yêu cầu dự án & Mục III | **100%** — Tiếng Việt có dấu trên PyGame UI, Matplotlib, Notebook Markdown & `TASK1.md`; tiếng Việt không dấu (ASCII thuần) trên CLI terminal (`0` ký tự ngoài ASCII), ngoại lệ và toàn bộ comment/docstring mã nguồn; giữ nguyên 100% outputs trên [experiments_task1.ipynb](file:///d:/3.1.%20AI/Final/source/task1/experiments_task1.ipynb). |

---

## 2. Kiến Trúc OOP & Tổ Chức Mã Nguồn (`source/task1/`)

Toàn bộ Nhiệm vụ 1 nằm gọn và độc lập trong thư mục `source/task1/`, gồm 8 tệp Python và 1 sổ tay Jupyter:

| Tệp | Tầng kiến trúc | Vai trò & Lớp OOP chính |
| :--- | :--- | :--- |
| [base_solver.py](file:///d:/3.1.%20AI/Final/source/task1/base_solver.py) | Lõi OOP (trừu tượng) | Lớp trừu tượng `BaseNQueenSolver(ABC)` thống nhất giao diện `name`, `cli_name`, `solve(n)` cho cả SAT và Tìm kiếm cục bộ. |
| [board.py](file:///d:/3.1.%20AI/Final/source/task1/board.py) | Lõi Mô hình trạng thái | Lớp `NQueenBoard` quản lý trạng thái đầy đủ bằng 3 mảng phẳng $\mathcal{O}(1)$ (`_row_counts`, `_main_diag_counts`, `_anti_diag_counts`), cập nhật gia tăng tổng xung đột `move_queen()`, `best_rows_for_column()`, `attacking_pairs()`, `from_sat_model()`, `is_valid_solution()`. |
| [cnf_encoder.py](file:///d:/3.1.%20AI/Final/source/task1/cnf_encoder.py) | Lõi Logic mệnh đề | `PropositionalVariableMapper`, `PropositionalRule`, `CNFEncodingStats`, `NQueenCNFEncoder` (tách 2 pha phát hiện nhóm ràng buộc và chuyển đổi CNF). |
| [sat_solver.py](file:///d:/3.1.%20AI/Final/source/task1/sat_solver.py) | Lõi Bộ giải SAT | `SATSolveResult`, `Glucose3NQueenSolver(BaseNQueenSolver)` hỗ trợ đo trung vị đa lặp và trích xuất thống kê CDCL nội bộ từ `Glucose3.accum_stats()`. |
| [min_conflicts.py](file:///d:/3.1.%20AI/Final/source/task1/min_conflicts.py) | Lõi Tìm kiếm cục bộ | `StepSnapshot`, `LocalSearchResult`, `VariableSelectionStrategy(ABC)`, `RandomConflictedSelector`, `PureMaxConflictSelector`, `AdaptiveTabuMaxConflictSelector`, `MinConflictsSolver(BaseNQueenSolver)` (cung cấp song song `solve()` tốc độ cao và generator `iter_solve()` cho UI). |
| [__init__.py](file:///d:/3.1.%20AI/Final/source/task1/__init__.py) | Giao diện gói | Export sạch toàn bộ API công khai của Nhiệm vụ 1. |
| [ui_nqueen.py](file:///d:/3.1.%20AI/Final/source/task1/ui_nqueen.py) | Giao diện (View) | `MinimalNQueenUI` bằng PyGame thuần tuân thủ tuyệt đối [UI.md](file:///d:/3.1.%20AI/Final/UI.md) (`1160 × 720`, 3 tông màu, vương miện vector, tia xung đột nét đứt, mô phỏng từng bước và so sánh nhanh). |
| [main_task1.py](file:///d:/3.1.%20AI/Final/source/task1/main_task1.py) | Điều phối & CLI | `Task1ExperimentRunner` quản lý khởi chạy PyGame mặc định, chế độ `--cli`, `--explain-cnf`, `--verify`, và `--headless-screenshot`. |
| [experiments_task1.ipynb](file:///d:/3.1.%20AI/Final/source/task1/experiments_task1.ipynb) | Sổ tay thực nghiệm | Thực nghiệm đầy đủ 3 phần 1.1, 1.2, 1.3 đã chạy sẵn giữ nguyên 100% bảng và đồ thị đầu ra. |

```mermaid
classDiagram
    class BaseNQueenSolver {
        <<abstract>>
        +name
        +cli_name
        +solve(n)
    }
    class Glucose3NQueenSolver
    class MinConflictsSolver
    class NQueenCNFEncoder
    class PropositionalVariableMapper
    class NQueenBoard
    class VariableSelectionStrategy {
        <<abstract>>
        +select_column()
        +notify_move()
    }
    class RandomConflictedSelector
    class PureMaxConflictSelector
    class AdaptiveTabuMaxConflictSelector
    class MinimalNQueenUI
    class Task1ExperimentRunner

    BaseNQueenSolver <|-- Glucose3NQueenSolver
    BaseNQueenSolver <|-- MinConflictsSolver
    Glucose3NQueenSolver --> NQueenCNFEncoder
    NQueenCNFEncoder --> PropositionalVariableMapper
    MinConflictsSolver --> VariableSelectionStrategy
    VariableSelectionStrategy <|-- RandomConflictedSelector
    VariableSelectionStrategy <|-- PureMaxConflictSelector
    VariableSelectionStrategy <|-- AdaptiveTabuMaxConflictSelector
    Glucose3NQueenSolver ..> NQueenBoard
    MinConflictsSolver ..> NQueenBoard
    MinimalNQueenUI --> Glucose3NQueenSolver
    MinimalNQueenUI --> MinConflictsSolver
    Task1ExperimentRunner --> Glucose3NQueenSolver
    Task1ExperimentRunner --> MinConflictsSolver
```

---

## 3. Yêu Cầu 1.1 — Mô Hình Logic Mệnh Đề & Quy Trình Chuyển Đổi CNF

### 3.1. Các thành phần của mô hình Logic mệnh đề
- **Tập biến mệnh đề:** Bàn cờ $N \times N$ có đúng $N^2$ ô $(r, c)$ với $r, c \in \{0, \dots, N-1\}$. Gán cho mỗi ô một biến mệnh đề $P_{r,c} \in \{\text{True}, \text{False}\}$ (`True` nếu ô chứa quân hậu, `False` nếu trống).
- **Ánh xạ song ánh sang chuẩn DIMACS (`PySAT`):**
  $$\text{id}(r, c) = r \cdot N + c + 1 \in \{1, \dots, N^2\}, \qquad (r, c) = \text{divmod}(v - 1, N)$$
- **Thuật toán phát hiện ràng buộc (`discover_constraint_groups` – độ phức tạp $\mathcal{O}(N^2)$):**
  Duyệt qua mọi ô $(r, c)$ đúng một lần để gom các ô có khả năng tương tác vào 4 họ nhóm tuyến tính:
  1. $N$ nhóm **hàng** (cùng $r$), mỗi nhóm $N$ ô.
  2. $N$ nhóm **cột** (cùng $c$), mỗi nhóm $N$ ô.
  3. $2N - 3$ nhóm **đường chéo chính** có độ dài $\ge 2$ (cùng hiệu $r - c$).
  4. $2N - 3$ nhóm **đường chéo phụ** có độ dài $\ge 2$ (cùng tổng $r + c$).

### 3.2. Quy trình chuyển đổi các ràng buộc sang Dạng chuẩn hội (CNF)
1. **Ràng buộc tồn tại (*At-Least-One* – ALO):** Mỗi hàng $r$ (và bổ sung mỗi cột $c$ nhằm tăng cường lan truyền đơn vị *Unit Propagation* cho `Glucose3`) phải có ít nhất một quân hậu:
   $$\bigvee_{c=0}^{N-1} P_{r,c}, \qquad \bigvee_{r=0}^{N-1} P_{r,c}$$
   Các công thức này đã là tuyển của các literal dương nên ở sẵn dạng chuẩn CNF.
2. **Ràng buộc không tấn công (*Pairwise At-Most-One* – AMO):** Với mọi cặp ô phân biệt $(r_1, c_1) \prec (r_2, c_2)$ thuộc cùng một nhóm hàng, cột hoặc đường chéo, nếu ô thứ nhất có hậu thì ô thứ hai không được có hậu:
   $$P_{r_1,c_1} \Rightarrow \neg P_{r_2,c_2}$$
   Áp dụng luật khử phép kéo theo ($\alpha \Rightarrow \beta \equiv \neg\alpha \vee \beta$), ta thu trực tiếp mệnh đề nhị nguyên chuẩn CNF (không phát sinh bước phân phối hay biến phụ Tseitin):
   $$\neg P_{r_1,c_1} \vee \neg P_{r_2,c_2} \quad \longleftrightarrow \quad [-\text{id}(r_1, c_1),\ -\text{id}(r_2, c_2)]$$

### 3.3. Minh họa chuyển đổi thực tế với $N = 4$ (trích từ `NQueenCNFEncoder(4)`)

| Loại ràng buộc | Biểu thức Logic mệnh đề | Dạng chuẩn hội (CNF) | Mệnh đề DIMACS |
| :--- | :--- | :--- | :--- |
| Tồn tại theo hàng (ALO) | `P(0,0) v P(0,1) v P(0,2) v P(0,3)` | `P(0,0) v P(0,1) v P(0,2) v P(0,3)` | `[1, 2, 3, 4]` |
| Tồn tại theo cột (ALO) | `P(0,0) v P(1,0) v P(2,0) v P(3,0)` | `P(0,0) v P(1,0) v P(2,0) v P(3,0)` | `[1, 5, 9, 13]` |
| Không tấn công cùng hàng (AMO) | `P(0,0) => ~P(0,1)` | `~P(0,0) v ~P(0,1)` | `[-1, -2]` |
| Không tấn công cùng cột (AMO) | `P(0,0) => ~P(1,0)` | `~P(0,0) v ~P(1,0)` | `[-1, -5]` |
| Không tấn công chéo chính (AMO) | `P(0,0) => ~P(1,1)` | `~P(0,0) v ~P(1,1)` | `[-1, -6]` |
| Không tấn công chéo phụ (AMO) | `P(0,1) => ~P(1,0)` | `~P(0,1) v ~P(1,0)` | `[-2, -5]` |

### 3.4. Công thức đóng & Kiểm chứng độ chính xác số mệnh đề
Tổng số mệnh đề CNF (khi bật ALO cột) tuân theo công thức đóng bậc ba $\mathcal{O}(N^3)$:
$$|C_{\text{CNF}}(N)| = 2N + 2N\binom{N}{2} + 2\left[\binom{N}{2} + 2\sum_{k=2}^{N-1}\binom{k}{2}\right] = 2N + N^2(N - 1) + \frac{N(N - 1)(2N - 1)}{3}$$

Kiểm chứng thực tế trên cả 2 chế độ và trường hợp vô nghiệm $N = 2, 3$ (khớp 100% giữa công thức lý thuyết và số mệnh đề sinh bởi `encode()`):

| $N$ | Số biến ($N^2$) | ALO (Hàng+Cột) | AMO Hàng+Cột | AMO Đường chéo | Tổng CNF (có ALO cột) | Tổng CNF (chỉ ALO hàng) | Trạng thái SAT |
| :-: | :-: | :-: | :-: | :-: | :-: | :-: | :--- |
| 1 | 1 | 2 | 0 | 0 | 2 | 1 | Có nghiệm hợp lệ |
| 2 | 4 | 4 | 4 | 2 | 10 | 8 | Vô nghiệm (`UNSAT`) |
| 3 | 9 | 6 | 18 | 10 | 34 | 31 | Vô nghiệm (`UNSAT`) |
| 4 | 16 | 8 | 48 | 28 | 84 | 80 | Có nghiệm hợp lệ |
| 8 | 64 | 16 | 448 | 280 | 744 | 736 | Có nghiệm hợp lệ |
| 12 | 144 | 24 | 1.584 | 1.012 | 2.620 | 2.608 | Có nghiệm hợp lệ |
| 16 | 256 | 32 | 3.840 | 2.480 | 6.352 | 6.336 | Có nghiệm hợp lệ |
| 20 | 400 | 40 | 7.600 | 4.940 | 12.580 | 12.560 | Có nghiệm hợp lệ |
| 30 | 900 | 60 | 26.100 | 17.110 | 43.270 | 43.240 | Có nghiệm hợp lệ |
| 50 | 2.500 | 100 | 122.500 | 80.850 | 203.450 | 203.400 | Có nghiệm hợp lệ |

---

## 4. Yêu Cầu 1.2 — Thực Nghiệm Bộ Giải SAT `Glucose3` (`PySAT`)

Thực nghiệm chạy qua [experiments_task1.ipynb](file:///d:/3.1.%20AI/Final/source/task1/experiments_task1.ipynb) trên 15 kích thước tăng dần $N \in [4, 80]$, đo **trung vị 3 lần chạy** sau warm-up và kiểm chứng độc lập 100% nghiệm bằng `board.is_valid_solution()`:

| $N$ | Số biến ($N^2$) | Tổng mệnh đề CNF | Mã hóa CNF (ms) | Giải `Glucose3` (ms) | Tổng thời gian (ms) | Quyết định | Xung đột CDCL | Lan truyền đơn vị | Hợp lệ |
| :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: |
| 4 | 16 | 84 | 0,27 | 0,66 | 0,94 | 12 | 2 | 28 | Đúng |
| 6 | 36 | 302 | 0,39 | 0,63 | 1,02 | 18 | 7 | 96 | Đúng |
| 8 | 64 | 744 | 0,55 | 0,91 | 1,46 | 39 | 21 | 295 | Đúng |
| 10 | 100 | 1.490 | 0,59 | 1,19 | 1,78 | 39 | 14 | 266 | Đúng |
| 12 | 144 | 2.620 | 1,93 | 2,49 | 4,42 | 75 | 34 | 557 | Đúng |
| 16 | 256 | 6.352 | 5,87 | 27,44 | 33,31 | 1.195 | 952 | 15.473 | Đúng |
| 20 | 400 | 12.580 | 11,55 | 24,35 | 35,90 | 542 | 167 | 4.101 | Đúng |
| 25 | 625 | 24.850 | 12,81 | 31,66 | 44,46 | 475 | 212 | 5.629 | Đúng |
| 30 | 900 | 43.270 | 24,34 | 47,61 | 71,95 | 632 | 137 | 5.390 | Đúng |
| 35 | 1.225 | 69.090 | 135,00 | 148,17 | 283,17 | 3.268 | 1.336 | 40.766 | Đúng |
| 40 | 1.600 | 103.560 | 206,11 | 160,62 | 366,73 | 1.809 | 312 | 13.695 | Đúng |
| 50 | 2.500 | 203.450 | 249,04 | 251,49 | 500,52 | 1.842 | 250 | 12.301 | Đúng |
| 60 | 3.600 | 352.940 | 468,16 | 428,38 | 896,55 | 2.593 | 203 | 16.204 | Đúng |
| 70 | 4.900 | 562.030 | 746,27 | 739,37 | 1.485,63 | 5.197 | 355 | 34.306 | Đúng |
| 80 | 6.400 | 840.720 | 1.104,58 | 1.426,62 | 2.531,19 | 7.154 | 276 | 34.903 | Đúng |

- **Biểu đồ trực quan:** [task1_glucose3_scaling.png](file:///d:/3.1.%20AI/Final/report/figures/task1_glucose3_scaling.png).
- **Nhận xét chuyên môn:** Tổng số mệnh đề tăng đúng theo quy luật bậc ba $\mathcal{O}(N^3)$ (từ `84` mệnh đề ở $N=4$ lên `840.720` mệnh đề ở $N=80$). Nhờ cơ chế học mệnh đề từ xung đột (**CDCL**) và lan truyền đơn vị nhanh bằng C++, `Glucose3` tìm ra nghiệm hợp lệ cho $N=50$ chỉ trong `251,49 ms` và $N=80$ trong `1,43 s`; tuy nhiên ở quy mô $N \ge 60$, chi phí tạo và nạp hàng trăm nghìn mệnh đề nhị nguyên (cỡ $\mathcal{O}(N^3)$) trở thành nút thắt chính chiếm tới gần một nửa tổng thời gian chạy.

---

## 5. Yêu Cầu 1.3 — `Min-Conflicts` & Heuristic Chọn Biến Đề Xuất

### 5.1. Thiết kế biểu diễn trạng thái & Heuristic `Max-Conflict + Tabu thích nghi`
- **Biểu diễn trạng thái đầy đủ:** Mảng một chiều `queens[c] = r` (mỗi cột đúng 1 quân hậu) đi kèm 3 mảng phẳng đếm tần suất hàng (`n`), đường chéo chính (`2n - 1`, chỉ số `r - c + n - 1`) và đường chéo phụ (`2n - 1`, chỉ số `r + c`). Mọi phép truy vấn xung đột và cập nhật `move_queen()` chạy trong thời gian **$\mathcal{O}(1)$** không cần băm `dict`/`Counter`.
- **Phân tích hạn chế của các chiến lược cơ sở:**
  - *Min-Conflicts tiêu chuẩn (Lecture 08 – chọn ngẫu nhiên đều):* Tránh kẹt tốt ở $N$ lớn nhưng chọn thừa nhiều cột chỉ có `1` xung đột thay vì ưu tiên các cột đang gây `3–4` xung đột, đồng thời có thể mắc kẹt ở cực trị cục bộ chặt (`1` cặp xung đột) trên bàn cờ nhỏ ($N=8, 16$).
  - *Max-Conflict thuần túy (Đối chứng):* Luôn chọn cột nhiều xung đột nhất giúp giảm nhanh xung đột ban đầu nhưng rất dễ dao động lặp chu trình trên vùng bình nguyên, khiến tỷ lệ thành công tụt xuống `92%` ở $N=16$ và số bước tăng vọt gấp đôi bản chuẩn.
- **4 cơ chế phối hợp trong Heuristic đề xuất (`AdaptiveTabuMaxConflictSelector`):**
  1. *Ưu tiên bậc xung đột cực đại kèm phá hòa theo tuổi (`1` lượt duyệt $\mathcal{O}(|C|)$):* Chọn cột chưa bị cấm có số xung đột lớn nhất; nếu đồng hạng, ưu tiên cột có thời gian chưa di chuyển `step - last_moved[col]` lớn nhất để phân tán sửa lỗi khắp bàn cờ.
  2. *Thời hạn cấm Tabu thích nghi theo quy mô tập xung đột $k = |C|$:*
     $$T_{\text{eff}}(k) = \begin{cases} 0 & \text{nếu } k \le 2 \\ \min\Big(\max(2, \min(6, \text{round}(0{,}10 N))),\ \lfloor k / 2 \rfloor\Big) & \text{nếu } k \ge 3 \end{cases}$$
     Cách co giãn này khắc phục triệt để lỗi khóa vòng lặp 2–3 bước khi $k$ nhỏ trên $N=8$ và ở giai đoạn cuối trên $N$ lớn, đảm bảo luôn còn ít nhất một nửa số cột xung đột khả dụng.
  3. *Điều kiện ân xá nhẹ ($\mathcal{O}(1)$-gated Aspiration):* Chỉ kiểm tra nước đi giải quyết ngay (`conflicts_if_placed == 0`) cho cột đang bị cấm khi `total_conflicts <= 2` và `score == total_conflicts`, vừa chốt nghiệm tức thì vừa loại bỏ hoàn toàn chi phí quét dư thừa ở $N$ lớn.
  4. *Thoát bình nguyên & phá cực trị cục bộ chặt:* Theo dõi số bước đình trệ với ngưỡng thích nghi $\tau = \max(4, \min(12, \lfloor N / 2 \rfloor + 1))$. Khi kẹt đúng cực trị chặt `1` cặp xung đột (hoặc đình trệ liên tiếp 3 chu kỳ), heuristic chủ động chọn một cột **chưa xung đột** để di chuyển sang hàng tối ưu khác hàng hiện tại, phá vỡ ngay thế khóa mà các cột đang xung đột không thể tự thoát.

### 5.2. Kết quả đối sánh công bằng (50 bàn cờ khởi tạo chung / mức $N$, `max_steps = 2500`)

| $N$ | Phương pháp chọn biến | Tỷ lệ thành công | Số bước TB | Trung vị bước | Thời gian TB (ms) | Giảm bước so với chuẩn |
| :-: | :--- | :-: | :-: | :-: | :-: | :-: |
| **8** | Min-Conflicts tiêu chuẩn (Ngẫu nhiên) | 98,0% | 94,42 | 32,0 | 1,74 | — |
| **8** | Max-Conflict thuần (Đối chứng) | 96,0% | 146,40 | 32,0 | 4,38 | -55,1% |
| **8** | **Max-Conflict + Tabu thích nghi (Đề xuất)** | **100,0%** | **23,98** | **21,5** | **1,41** | **+74,6%** |
| **16** | Min-Conflicts tiêu chuẩn (Ngẫu nhiên) | 98,0% | 116,92 | 48,0 | 10,37 | — |
| **16** | Max-Conflict thuần (Đối chứng) | 92,0% | 253,66 | 49,0 | 32,42 | -117,0% |
| **16** | **Max-Conflict + Tabu thích nghi (Đề xuất)** | **100,0%** | **48,26** | **35,5** | **2,26** | **+58,7%** |
| **32** | Min-Conflicts tiêu chuẩn (Ngẫu nhiên) | 100,0% | 81,60 | 69,5 | 4,31 | — |
| **32** | Max-Conflict thuần (Đối chứng) | 100,0% | 68,60 | 64,0 | 3,33 | +15,9% |
| **32** | **Max-Conflict + Tabu thích nghi (Đề xuất)** | **100,0%** | **70,10** | **47,5** | **3,62** | **+14,1%** |
| **64** | Min-Conflicts tiêu chuẩn (Ngẫu nhiên) | 100,0% | 101,94 | 98,5 | 6,93 | — |
| **64** | Max-Conflict thuần (Đối chứng) | 100,0% | 92,48 | 94,5 | 9,96 | +9,3% |
| **64** | **Max-Conflict + Tabu thích nghi (Đề xuất)** | **100,0%** | **70,28** | **65,5** | **8,03** | **+31,1%** |
| **100** | Min-Conflicts tiêu chuẩn (Ngẫu nhiên) | 100,0% | 136,96 | 132,0 | 17,74 | — |
| **100** | Max-Conflict thuần (Đối chứng) | 100,0% | 120,46 | 117,0 | 21,47 | +12,0% |
| **100** | **Max-Conflict + Tabu thích nghi (Đề xuất)** | **100,0%** | **109,28** | **92,5** | **17,82** | **+20,2%** |
| **150** | Min-Conflicts tiêu chuẩn (Ngẫu nhiên) | 100,0% | 172,44 | 163,5 | 36,76 | — |
| **150** | Max-Conflict thuần (Đối chứng) | 100,0% | 151,62 | 143,0 | 34,37 | +12,1% |
| **150** | **Max-Conflict + Tabu thích nghi (Đề xuất)** | **100,0%** | **134,86** | **124,5** | **25,92** | **+21,8%** |
| **200** | Min-Conflicts tiêu chuẩn (Ngẫu nhiên) | 100,0% | 202,76 | 202,0 | 61,21 | — |
| **200** | Max-Conflict thuần (Đối chứng) | 100,0% | 176,20 | 167,5 | 49,39 | +13,1% |
| **200** | **Max-Conflict + Tabu thích nghi (Đề xuất)** | **100,0%** | **158,78** | **152,0** | **32,69** | **+21,7%** |

- **Biểu đồ đối sánh & đường cong hội tụ:** [task1_min_conflicts_comparison.png](file:///d:/3.1.%20AI/Final/report/figures/task1_min_conflicts_comparison.png).
- **Nhận xét nổi bật:**
  1. **Tỷ lệ thành công tuyệt đối `100,0%` trên toàn bộ 7 mức kích thước ($N = 8..200$)** — vượt qua cả `Min-Conflicts` tiêu chuẩn (`98%` ở $N=8, 16$) lẫn `Max-Conflict` thuần (`92%` ở $N=16$).
  2. **Giảm mạnh số bước sửa xung đột trên mọi $N$:** giảm `74,6%` ở $N=8$, `58,7%` ở $N=16$, `31,1%` ở $N=64$ và `21,7%` ở $N=200$ (trung vị bước cũng luôn thấp nhất ở tất cả các mức $N$).
  3. **Nhanh hơn rõ rệt về thời gian thực thi:** ở $N=16$ nhanh gấp `4,6` lần (`2,26 ms` vs `10,37 ms`), ở $N=150$ nhanh hơn `29,5%`, và ở $N=200$ nhanh gần gấp đôi (`32,69 ms` vs `61,21 ms`).

---

## 6. Giao Diện PyGame Tối Giản (`ui_nqueen.py`) Tuân Thủ `UI.md`

Giao diện [ui_nqueen.py](file:///d:/3.1.%20AI/Final/source/task1/ui_nqueen.py) được thiết kế lại hoàn toàn bằng **PyGame** (thay thế `Tkinter` cũ) theo đúng quy chuẩn **Tối giản (Minimalism)** trong [UI.md](file:///d:/3.1.%20AI/Final/UI.md):
- **Cửa sổ chuẩn `1160 × 720`:** Vừa vặn hoàn toàn trên màn hình laptop macOS 13.7.8 và Windows; bố cục 2 vùng thoáng (bàn cờ bên trái ~67%, sidebar 3 khối bên phải ~33%) ngăn cách bởi đường kẻ mảnh `1px`.
- **Giới hạn đúng 3 tông màu:** Trung tính Giấy & Mực (`#FAFAFA`, `#FFFFFF`, `#F3F4F6`, `#E5E7EB`, `#111827`, `#6B7280`), Xanh ngọc trầm (`#0F766E` cho nút chính và nghiệm hợp lệ), Đỏ gạch trầm (`#C83E37` cho quân hậu và tia nét đứt xung đột).
- **Trực quan hóa thuật toán & tương tác mượt:**
  - Chọn nhanh $N \in \{4, 8, 12, 16, 20, 32, 50\}$ hoặc điều chỉnh tự do $N \in [4, 100]$ bằng nút `-` / `+`.
  - Chuyển đổi giữa 4 chế độ (`Glucose3`, `Min-Conflicts tiêu chuẩn`, `Max-Conflict thuần`, `Max-Conflict + Tabu thích nghi`).
  - Hỗ trợ `Giải ngay`, `Ngẫu nhiên`, `Từng bước`, `Phát / Tạm dừng`, thanh trượt tốc độ (`1–60 bước/giây`), nút `So sánh` chạy trực tiếp chuẩn vs đề xuất trên đúng cùng bàn cờ khởi tạo, và phím tắt (`Enter`, `Space`, `Right`/`S`, `R`, `Esc`).
  - Hiển thị trực tiếp bảng thông số phân rã mệnh đề CNF (`ALO`/`AMO`) và thống kê `Glucose3` khi giải SAT.
  - **Ảnh chụp minh họa:** [task1_nqueen_ui.png](file:///d:/3.1.%20AI/Final/report/figures/task1_nqueen_ui.png).

---

## 7. Hướng Dẫn Chạy & Kiểm Chứng Tự Động

Đứng tại thư mục gốc dự án (thay `python` bằng `& "F:\Python311\python.exe"` nếu chạy trực tiếp trên máy Windows hiện tại):

```bash
# 1. Mo giao dien PyGame toi gian (mac dinh)
python source/task1/main_task1.py

# 2. Chay bo kiem chung tu dong toan dien (5 nhom assertion toan hoc & hieu nang)
python source/task1/main_task1.py --verify

# 3. Chay tron bo thuc nghiem CLI (tieng Viet khong dau, khong loi font terminal)
python source/task1/main_task1.py --cli

# 4. Chi xem minh hoa mo hinh Logic menh de & chuyen doi CNF cho N = 4
python source/task1/main_task1.py --explain-cnf 4

# 5. Xuat anh chup giao dien PyGame o che do khong cua so (conflicts / sat / solved)
python source/task1/main_task1.py --headless-screenshot task1_preview.png --screenshot-mode sat
```

---

## 8. Trọng Tâm Chuẩn Bị Phỏng Vấn Vấn Đáp (Task 1)

1. **Tại sao SAT cần $N^2$ biến mệnh đề trong khi `Min-Conflicts` chỉ cần mảng độ dài $N$?**
   - Trong Logic mệnh đề, mỗi biến chỉ nhận giá trị nhị phân `True`/`False`, nên phải gán 1 biến $P_{r,c}$ cho từng ô để biểu diễn sự có mặt của quân hậu. Trong tìm kiếm cục bộ CSP, ta khai thác sẵn ràng buộc "mỗi cột đúng 1 quân hậu" bằng cách chọn mỗi cột là 1 biến miền $\{0, \dots, N-1\}$, rút không gian trạng thái từ $2^{N^2}$ xuống $N^N$.
2. **Giải thích thuật toán tìm ràng buộc và cách chuyển sang CNF không cần biến phụ?**
   - Duyệt bàn cờ $\mathcal{O}(N^2)$ gom các ô cùng hàng ($r$), cùng cột ($c$), cùng đường chéo chính ($r - c$) và cùng đường chéo phụ ($r + c$). Ràng buộc tồn tại là tuyển sẵn dạng CNF; ràng buộc không tấn công theo cặp $P(a) \Rightarrow \neg P(b)$ chỉ cần bước khử phép kéo theo thành $(\neg P(a) \vee \neg P(b))$ là đạt ngay CNF nhị nguyên.
3. **Tại sao thời gian giải của `Glucose3` tăng nhanh khi $N \ge 60$?**
   - Số mệnh đề AMO tăng theo bậc ba $\mathcal{O}(N^3)$ (`840.720` mệnh đề tại $N=80$), khiến cả bước mã hóa ở Python lẫn bước nạp và lan truyền đơn vị trong bộ giải SAT đều mở rộng nhanh theo $N^3$.
4. **Tại sao `Max-Conflict` thuần hay thất bại ở $N=8, 16$, và Heuristic đề xuất khắc phục ra sao?**
   - `Max-Conflict` thuần có tính tất định cao nên dễ mắc kẹt vào chu trình 2–3 cột trên bình nguyên (`92%` ở $N=16$, `253,7` bước). Heuristic đề xuất dùng danh sách cấm Tabu có thời hạn thích nghi $T_{\text{eff}}(k) = \min(T_{\max}, \lfloor k/2 \rfloor)$ (tự tắt khi $k \le 2$), phá hòa theo tuổi chưa di chuyển, ân xá khi có thể kết thúc ngay, và nhiễu động 1 cột chưa xung đột khi mắc kẹt cực trị chặt `1` cặp xung đột — giúp đạt `100%` thành công trên mọi $N$ và giảm tới `74,6%` số bước ở $N=8$.
5. **Tại sao tách riêng `solve()` và `iter_solve()` trong `MinConflictsSolver`?**
   - Để tách tuyệt đối tầng Logic và tầng Giao diện (Model–View): `solve()` chạy tốc độ tối đa không tạo overhead đối tượng khi chạy 50 lượt benchmark trong Notebook/CLI, trong khi `iter_solve()` dùng `yield` phát từng `StepSnapshot` bất biến để PyGame vẽ hoạt ảnh mượt và có thể tạm dừng/chạy từng bước bất cứ lúc nào.
