# Task 3: Trò Chơi Kakuro (Constraint Satisfaction Problems – CSP)

Đồ án cuối kỳ môn Nhập môn Trí tuệ nhân tạo (503043). Task 3 mô hình hóa Kakuro bằng CSP, cài đặt bộ giải hướng đối tượng (OOP), đánh giá thực nghiệm và trực quan hóa quá trình giải bằng PyGame. Giao diện sử dụng tiếng Anh.

---

## 1. Yêu Cầu Hệ Thống & Cài Đặt Môi Trường

### 1.1. Yêu cầu phiên bản Python

- Khuyến nghị Python 3.10–3.12, theo README chung của dự án; dùng môi trường ảo riêng hoặc môi trường ảo đã có của nhóm.
- Hệ điều hành Windows, macOS hoặc Linux. Bộ giải CLI chỉ dùng thư viện chuẩn Python; giao diện cần `pygame`, Notebook cần `numpy`, `pandas`, `matplotlib`, Jupyter và `nbclient` nếu thực thi tự động.
- Danh sách thư viện riêng cho Task 3 nằm trong `requirement.txt`. Không cần `python-sat` (thư viện của Task 1). Không thay thế file requirement chung của nhóm bằng file này.

### 1.2. Cài đặt trên môi trường ảo (khuyến nghị)

Mở Terminal tại thư mục `source/task3/` (hoặc `task3/` nếu giải nén riêng).

**Windows PowerShell:**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirement.txt
```

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirement.txt
```

Nếu đã kích hoạt môi trường chung của dự án, bỏ qua hai lệnh đầu. Nếu chỉ chạy giao diện, có thể cài `python -m pip install pygame`. CLI không cần cài thêm thư viện ngoài Python.

---

## 2. Cấu Trúc Thư Mục Dự Án

```text
task3/
├── __init__.py                  # Các lớp công khai của package
├── csp_model.py                 # CellVariable, RunConstraint, KakuroCSP
├── propagation.py               # SumPartitionCatalog, ForwardChecker, ExtendedAC3Propagator
├── solver.py                    # KakuroSolver, SolverMode, SolverStep, KakuroSolveResult
├── board_editor.py              # BoardEditor: chỉnh sửa, tạo, lưu/mở bảng
├── visualizer_ui.py             # ControlButton, KakuroVisualizerUI (PyGame)
├── main_task3.py                # Điểm khởi chạy GUI và CLI
├── experiments_task3.ipynb      # Notebook thực nghiệm, lưu output
├── README.md
├── requirement.txt
├── maps/
│   ├── board_5x5_example.json
│   ├── board_6x6_medium.json
│   ├── board_8x8_hard.json
│   └── board_9x9_complex.json
└── figures/                     # Biểu đồ do Notebook tạo
    └── task3_csp_benchmark.png
```

`maps/custom/` được tạo khi lưu bảng tùy chỉnh lần đầu. Mã nguồn không phụ thuộc đường dẫn ổ đĩa Windows.

### 2.1. Mô hình CSP (Yêu cầu 3.1)

- **X (Variables):** mỗi ô trắng là một biến, định danh bằng tọa độ `(row, col)` tính từ 0 trong Python/JSON; UI hiển thị tọa độ từ 1.
- **D (Domains):** các chữ số 1–9, hoặc miền đơn nếu ô có số nhập trước (given digit).
- **C (Constraints):** mỗi dãy trắng liên tiếp ngang/dọc phải có tổng bằng gợi ý (Exact Sum) và các chữ số đôi một khác nhau (AllDifferent). Mỗi ô trắng phải có cả hai dãy. `verify_solution()` kiểm tra đủ biến, miền, givens và toàn bộ dãy.

### 2.2. Bộ giải (Yêu cầu 3.2)

| Chế độ | Phương pháp |
|---|---|
| `PLAIN_BT` – Baseline Backtracking | Thứ tự hàng/cột, ứng viên tăng dần, kiểm tra AllDifferent và cận tổng của phép gán. |
| `BT_FC` – BT + Forward Checking + MRV | Tiền xử lý Sum Partitions, Forward Checking theo tổ hợp tổng còn lại và MRV. |
| `BT_MAC_HEURISTICS` – BT + Extended AC-3 + MRV/Degree/LCV | Tiền xử lý, Forward Checking, kiểm tra hỗ trợ trên dãy bằng Extended AC-3 (hướng GAC), MRV, Degree phá hòa và LCV. |

Extended AC-3 dùng hàng đợi các dãy liên quan và kiểm tra tổ hợp chữ số khác nhau phù hợp miền hiện tại, có kiểm tra cận tổng min/max. LCV thử lan truyền trên bản sao trạng thái và ưu tiên ứng viên khả thi làm mất ít lựa chọn nhất. Khi quay lui, bộ giải khôi phục miền đã lưu. Mặc định tìm nghiệm đầu tiên, không kiểm tra tính duy nhất.

---

## 3. Hướng Dẫn Chi Tiết Cách Chạy Task 3

### A. Khởi chạy giao diện trực quan hóa PyGame (Yêu cầu 3.3)

Đứng tại thư mục `task3/`:

```bash
python main_task3.py
```

Nếu đứng tại thư mục gốc `classical-ai-suite/`, chạy `python source/task3/main_task3.py`. Giao diện mở ở Solver Mode, bảng mẫu 5x5 và chế độ Advanced.

**Ký hiệu và màu sắc:** ô đen không có số dùng để ngăn cách; số ở nửa trên bên phải là tổng ngang (`across`), số ở nửa dưới bên trái là tổng dọc (`down`). Ô trắng hiển thị ứng viên 1–9 hoặc số lớn đã gán. Màu tím/G là given digit; xanh dương là ô đang xét; đỏ và gạch ngang là ứng viên bị loại; cam là từ chối/ngõ cụt/quay lui; nền xanh lá ở bước nghiệm. Dấu `x` báo miền rỗng.

| Nút Solver Mode | Chức năng |
|---|---|
| `Switch Preset` | Luân phiên 5x5, 9x9, 6x6, 8x8. |
| Nút tên thuật toán | Chuyển giữa Advanced, FC + MRV và Basic. |
| `Auto Play / Pause` (`Space`) | Phát/tạm dừng lịch sử giải. |
| `Previous Step / Next Step` (mũi tên trái/phải) | Lùi/tiến một sự kiện. |
| `Reset` (`0`) / `Final State` | Về bước đầu / cuối (cuối có thể là vô nghiệm hoặc giới hạn). |
| `Speed` | Điều chỉnh 25–1200 ms/step (mặc định 220). |
| `Solve Again` | Tính lại bộ giải trên dữ liệu hiện tại. |
| `Edit Board / Stop & Edit` (`Esc`) | Hủy tìm kiếm đang chạy hoặc dừng phát để chỉnh sửa đầu vào. |

Bộ giải tính toán trên luồng nền khi khởi chạy phiên giải mới từ giao diện, rồi UI phát lại snapshot. Việc khởi tạo cửa sổ và `_reload_problem()` hiện vẫn tính đồng bộ. Hủy là cơ chế hợp tác (Event), không phải tiếp tục nhánh tìm kiếm cũ. `Assigned Cells` là số biến đã gán ở bước hiện tại, `Nodes Tried` là lượt thử ứng viên (kể cả bị từ chối), `Backtracks` là lượt hủy phép gán đã thực hiện, `Solve Time` là thời gian tìm kiếm/tiền xử lý và ghi trace nếu bật (không gồm thời gian phát lại hay kiểm tra nghiệm cuối ngoài bộ đếm). `Step` là số sự kiện đã ghi, không phải số nút. UI giới hạn 30.000 sự kiện và giữ sự kiện kết thúc; bộ giải mặc định giới hạn 300.000 lượt thử. `NODE_LIMIT` không đồng nghĩa vô nghiệm.

### B. Chỉnh sửa và tạo bảng (Board Editor)

Nhấn `Edit Board` hoặc `Stop & Edit`. Chọn ô đen để sửa `Across sum` / `Down sum`, ô trắng để nhập `Given digit` (1–9, 0 hoặc Delete để xóa). Enter áp dụng; `Make White` / `Make Black` đổi loại ô, tự đồng bộ hướng gợi ý; hàng/cột đầu không được chuyển thành ô trắng bằng thao tác này.

| Nút | Chức năng |
|---|---|
| `Choose Preset`, `Restore Preset` | Chọn hoặc khôi phục bảng mẫu. |
| `Size`, `Create Board` | Chọn kích thước 3x3–9x9 và tạo bảng vuông mới. |
| `Clear Given`, `Clear All Givens` | Xóa số nhập trước, giữ gợi ý. |
| `Bulk Edit All Cells` | Chỉnh sửa toàn bộ dữ liệu theo từng hàng. |
| `Randomize All Clues` | Giữ bố cục, sinh tổng từ một cấu hình chữ số hợp lệ, xóa givens; đảm bảo tồn tại nghiệm, không đảm bảo duy nhất hoặc mọi tổng đều đổi. |
| `Validate Board` | Kiểm tra cấu trúc và cận tổng/givens cục bộ; chưa chứng minh có nghiệm toàn cục. |
| `Save JSON`, `Load JSON` | Lưu/mở dữ liệu; tên tương đối nằm dưới `maps/custom/`. UI chỉ nhận bảng 3–9 hàng/cột. |
| `SOLVE CURRENT BOARD` | Khởi tạo CSP mới từ dữ liệu hiện tại và chạy thuật toán đã chọn. |

**Bulk Edit:** mỗi hàng có đúng số token bằng số cột, phân cách bằng dấu cách. `#` = ô đen, `0` = ô trắng trống, `1`–`9` = given digit, `A/D` = tổng ngang/dọc (0 = không có hướng đó). Ví dụ:

```text
# 0/4 0/6
3/0 1 0
7/0 0 4
```

Chọn trường hàng, Ctrl+A để xóa nội dung cũ, nhập lại, Enter; nhấn `APPLY ALL CHANGES` để áp dụng đồng thời. `Clear All Digits` xóa givens trong bản nháp; `Cancel Changes` hủy bản nháp. Dữ liệu cấu trúc không hợp lệ sẽ bị từ chối. Bảng có cấu trúc hợp lệ vẫn có thể vô nghiệm.

**Định dạng JSON:** `B` là ô đen, `W` là ô trắng, object chứa `across`/`down` là gợi ý; `givens` là danh sách tùy chọn, tọa độ từ 0. Ví dụ tương ứng bảng trên:

```json
{
  "name": "Custom 3x3",
  "grid": [["B", {"down": 4}, {"down": 6}],
           [{"across": 3}, "W", "W"],
           [{"across": 7}, "W", "W"]],
  "givens": [{"row": 1, "col": 1, "value": 1},
             {"row": 2, "col": 2, "value": 4}]
}
```

### C. Chạy Benchmark đánh giá bộ giải Kakuro trên Terminal (CLI)

```bash
python main_task3.py --cli
```

CLI chạy 4 bảng x 3 thuật toán, mỗi cấu hình một lần, không mở PyGame. Các cột `Vars`, `Nodes`, `Backtracks`, `Time (ms)`, `Valid` được in trên Terminal. Bảng mẫu hiện tại:

| Bảng | Số ô trắng | Số dãy (mỗi dãy gồm Sum + AllDifferent) |
|---|---:|---:|
| 5x5 | 12 | 8 |
| 6x6 | 19 | 12 |
| 8x8 | 41 | 22 |
| 9x9 | 48 | 28 |

Số biến lấy từ JSON trong phiên bản này, không lấy từ tài liệu phân tích ban đầu.

Có thể xuất ảnh minh họa bằng `python main_task3.py --headless-screenshot kakuro.png` (cần PyGame, sử dụng SDL dummy driver, chọn bảng 9x9 và Forward Checking).

---

## 4. Hướng Dẫn Mở & Chạy Jupyter Notebook Thực Nghiệm

```bash
python -m jupyter notebook experiments_task3.ipynb
```

Hoặc mở file trong VS Code với Python/Jupyter extension, chọn kernel của môi trường đã cài thư viện, chọn Run All rồi lưu file. Notebook hỗ trợ chạy từ thư mục task3, source hoặc gốc dự án. Không mở GUI khi đo thời gian.

Notebook chạy 30 lần cho mỗi cấu hình (360 lượt đo, sau lượt làm nóng riêng), kiểm tra nghiệm bằng `verify_solution()`, trình bày trung bình/độ lệch chuẩn thời gian, nút, quay lui, ứng viên bị loại và tỷ lệ thành công; vẽ biểu đồ trong `figures/`. Các chỉ số nút/quay lui là lượt đếm thực, không bao gồm thao tác thử trên bản sao của LCV; `Pruned Values` không tính phép gán hoặc các lần thử LCV, có thể đếm lại ứng viên được khôi phục rồi bị loại. Đo thời gian bằng `perf_counter()` trong solver, không bật trace. Không kỳ vọng Advanced luôn nhanh nhất vì chi phí lan truyền và LCV. Notebook còn in nghiệm 9x9 và kiểm tra chức năng dữ liệu tùy chỉnh, vô nghiệm, hủy và giới hạn tìm kiếm.

Kết quả thời gian phụ thuộc máy/kernels. Chạy lại trên máy cá nhân và lưu toàn bộ output trước khi nộp. Các bảng mẫu trong mã nguồn chưa được đối chiếu độc lập với hình trong đề gốc.

---

## 5. Kiểm Tra Trước Khi Nộp Bài

- Chạy CLI và kiểm tra `Valid=True` trên tất cả cấu hình.
- Mở GUI, thử chỉnh sửa một ô và nhiều ô, tạo tổng mới, lưu/mở JSON, dừng giải rồi giải lại, Auto Play/Pause và từng bước.
- Chạy Notebook, giữ output và biểu đồ. Nếu nhóm cần dùng hình trong báo cáo IEEE, sao chép từ `task3/figures/` sang thư mục báo cáo theo cấu trúc chung.
- Bản cập nhật tài liệu không thay đổi mã nguồn Python hay dữ liệu JSON. UI cần được kiểm thử trực tiếp trên máy có PyGame; không xác nhận tương thích macOS chỉ từ kết quả CLI.
