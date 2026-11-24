# Báo cáo Task 1 — Bài toán N hậu

Task 1 giải bài toán N hậu bằng hai hướng tiếp cận của trí tuệ nhân tạo. Hướng thứ nhất biểu diễn các ràng buộc bằng logic mệnh đề, chuyển chúng thành CNF và sử dụng bộ giải Glucose3. Hướng thứ hai sử dụng tìm kiếm cục bộ Min-Conflicts, sau đó đánh giá một heuristic chọn biến. Báo cáo này trình bày cách hiểu đề, phương pháp thực hiện và kết quả thực nghiệm đã lưu trong notebook.

## 1. Bài toán 8 hậu là gì?

Bài toán 8 hậu yêu cầu đặt 8 quân hậu lên bàn cờ vua kích thước 8 × 8 sao cho không có hai quân hậu nào tấn công nhau. Trong cờ vua, quân hậu có thể tấn công theo hàng ngang, cột dọc và hai hướng đường chéo. Vì vậy, một cách đặt hợp lệ phải thỏa mãn các điều kiện sau.

- Mỗi hàng có đúng một quân hậu.
- Mỗi cột có đúng một quân hậu.
- Mỗi đường chéo có nhiều nhất một quân hậu.

Ví dụ dưới đây là một cách đặt hợp lệ, với `Q` là quân hậu và `.` là ô trống.

```text
. . . Q . . . .
. Q . . . . . .
. . . . . . Q .
. . Q . . . . .
. . . . . Q . .
. . . . . . . Q
. . . . Q . . .
Q . . . . . . .
```

## 2. Bài toán N hậu là gì?

N hậu là dạng tổng quát của bài toán 8 hậu. Đầu vào là số nguyên dương N, tương ứng với bàn cờ N × N. Mục tiêu là đặt N quân hậu sao cho không có hai quân nào cùng hàng, cùng cột hoặc cùng đường chéo. Bài toán 8 hậu là trường hợp N = 8.

Một đầu ra hợp lệ là vị trí của đủ N quân hậu trên bàn cờ thỏa mãn các điều kiện trên. Chẳng hạn, chương trình có thể trả về danh sách hàng của quân hậu theo từng cột, hoặc hiển thị trực tiếp bàn cờ. Bài toán không có nghiệm với N = 2 và N = 3. Đề yêu cầu thực nghiệm Glucose3 với các giá trị N tăng dần và N ≥ 4.

## 3. Các yêu cầu cần thực hiện

Task 1 có tổng cộng 3 điểm và yêu cầu giải bài toán theo hai hướng.

### 3.1. Mô hình hóa bằng logic mệnh đề và CNF — 1 điểm

Gán mỗi ô hàng `r`, cột `c` một biến logic `P(r, c)`. Biến này nhận giá trị đúng khi ô có quân hậu và sai khi ô trống. Chương trình sinh các ràng buộc cho biết mỗi hàng phải có hậu và các cặp ô cùng hàng, cùng cột hoặc cùng đường chéo không được đồng thời có hậu.

Các ràng buộc được biểu diễn thành những mệnh đề ở dạng chuẩn hội, viết tắt là CNF. Phần phân tích cần giải thích cách xác định các ô có thể tấn công nhau và cách chuyển các ràng buộc thành mệnh đề CNF.

Với mỗi hàng, chương trình tạo một mệnh đề yêu cầu ít nhất một ô trong hàng có hậu. Chương trình cũng thêm mệnh đề tương tự cho mỗi cột. Với hai ô khác nhau nằm cùng hàng, cùng cột hoặc cùng đường chéo, chương trình tạo một mệnh đề cấm cả hai ô cùng có hậu. Hai ô `(r1, c1)` và `(r2, c2)` nằm trên cùng đường chéo khi `|r1 - r2| = |c1 - c2|`.

Ví dụ, nếu hai ô A và B cùng đường chéo, ràng buộc “nếu A có hậu thì B không có hậu” được viết thành `A → ¬B`. Sau khi chuyển sang CNF, mệnh đề tương đương là `¬A ∨ ¬B`. Các mệnh đề được nối với nhau bằng phép VÀ để tạo đầu vào cho bộ giải.

### 3.2. Giải bằng Glucose3 — 1 điểm

Đưa các mệnh đề CNF vào bộ giải Glucose3 của thư viện PySAT. Nếu tìm được nghiệm, chương trình chuyển kết quả của bộ giải thành vị trí các quân hậu và kiểm tra bàn cờ.

Thực nghiệm với nhiều giá trị N tăng dần, trong đó N ≥ 4. Với mỗi giá trị N, đề yêu cầu báo cáo số lượng mệnh đề CNF và thời gian chạy của bộ giải.

### 3.3. Giải bằng Min-Conflicts và đề xuất heuristic — 1 điểm

Min-Conflicts bắt đầu từ một cách đặt hậu có thể đang xung đột. Ở mỗi bước, thuật toán chọn một quân hậu đang bị tấn công rồi chuyển quân đó đến hàng gây ít xung đột nhất trong cùng cột. Quá trình dừng khi tìm được bàn cờ hợp lệ hoặc đạt giới hạn số bước.

Đề yêu cầu đề xuất một heuristic, tức quy tắc chọn biến, và thực nghiệm so sánh hiệu quả của heuristic đó với Min-Conflicts chuẩn. Trong phiên bản Task 1 hiện tại, cách chuẩn chọn ngẫu nhiên một quân hậu đang xung đột. Heuristic đề xuất ưu tiên quân có nhiều xung đột, kết hợp danh sách Tabu để hạn chế chọn lại những quân vừa di chuyển. Các lần thử dùng cùng các bàn cờ khởi tạo để hỗ trợ so sánh.

Heuristic Max-Conflict + Tabu hoạt động theo các bước sau.

1. Xác định các quân hậu đang xung đột và số quân mà mỗi quân đang tấn công.
2. Ưu tiên quân có nhiều xung đột nhất trong số những quân hiện không bị Tabu. Nếu nhiều quân có cùng mức xung đột cao nhất, thuật toán chọn ngẫu nhiên một quân trong số đó.
3. Sau khi chọn quân, Min-Conflicts xét các hàng trong cùng cột và chọn hàng gây ít xung đột nhất. Khi có nhiều hàng cùng tốt nhất, code ưu tiên chọn một hàng khác với vị trí hiện tại.
4. Đưa cột vừa chọn vào danh sách Tabu trong một số bước, nhằm hạn chế chọn lại ngay. Thời gian Tabu được tính theo N và nằm trong khoảng từ 2 đến 8 bước.

Code có thêm **điều kiện ân xá (aspiration)**. Một quân đang bị Tabu vẫn có thể được chọn nếu mọi xung đột còn lại đều liên quan đến quân đó và có một hàng cho phép di chuyển quân đến mà không tạo thêm xung đột. Nếu không có quân xung đột nào được phép chọn theo Tabu, thuật toán chọn trong toàn bộ các quân đang xung đột.

Khi số xung đột không tốt hơn mức tốt nhất đã ghi nhận trong 16 bước liên tiếp, code xóa danh sách Tabu và chọn ngẫu nhiên một quân đang xung đột. Cách này tạo thêm cơ hội khám phá các trạng thái khác. Min-Conflicts có thể hết giới hạn bước trước khi tìm được nghiệm, nên kết quả mỗi lượt cũng cần ghi nhận thành công hay thất bại.

## 4. Kết quả thực nghiệm

Các số liệu dưới đây được lấy từ output đã lưu trong `experiments_task1.ipynb`. Thời gian phụ thuộc vào máy và điều kiện chạy.

### 4.1. Kết quả Glucose3

| N | Số biến | Số mệnh đề CNF | Thời gian solver (ms) |
|---:|---:|---:|---:|
| 4 | 16 | 84 | 0,72 |
| 8 | 64 | 744 | 0,62 |
| 16 | 256 | 6.352 | 16,60 |
| 50 | 2.500 | 203.450 | 67,66 |
| 60 | 3.600 | 352.940 | 191,85 |

Notebook chạy Glucose3 với các kích thước 4, 8, 12, 16, 20, 25, 30, 35, 40, 50 và 60. Số mệnh đề tăng khi kích thước bàn cờ tăng. Thời gian ở bảng bao gồm khởi tạo solver, nạp mệnh đề, giải và lấy mô hình.

### 4.2. So sánh Min-Conflicts

Mỗi phương pháp được chạy 30 lần cho mỗi kích thước N trên cùng tập bàn cờ ban đầu. Mỗi lần chạy có giới hạn 2.500 bước.

| N | Phương pháp | Tỷ lệ thành công | Số bước trung bình | Thời gian trung bình (ms) |
|---:|---|---:|---:|---:|
| 8 | Chọn ngẫu nhiên | 100% | 44,37 | 0,38 |
| 8 | Max-Conflict + Tabu | 93,33% | 181,67 | 2,25 |
| 16 | Chọn ngẫu nhiên | 100% | 96,00 | 1,79 |
| 16 | Max-Conflict + Tabu | 100% | 30,73 | 1,16 |
| 64 | Chọn ngẫu nhiên | 100% | 107,17 | 4,14 |
| 64 | Max-Conflict + Tabu | 100% | 63,27 | 2,80 |
| 150 | Chọn ngẫu nhiên | 100% | 179,53 | 17,47 |
| 150 | Max-Conflict + Tabu | 100% | 125,07 | 20,16 |

Trong lần thực nghiệm được lưu, heuristic cần ít bước trung bình hơn ở N = 16, 64 và 150. Tại N = 8, heuristic có tỷ lệ thành công thấp hơn và cần nhiều bước hơn. Tại N = 150, heuristic cần ít bước hơn nhưng thời gian trung bình cao hơn. Vì vậy, cần xem đồng thời tỷ lệ thành công, số bước và thời gian khi đánh giá. Các giá trị trung bình bao gồm cả lượt chưa tìm được nghiệm.

## 5. Sản phẩm đầu ra của Task 1

- **Mã nguồn OOP** mô hình hóa bàn cờ, tạo CNF, giải bằng Glucose3 và giải bằng hai phiên bản Min-Conflicts. Mã được đặt trong `source/task1/`.
- **Nghiệm N hậu** thể hiện vị trí N quân hậu khi thuật toán tìm được bàn cờ hợp lệ. Nếu Min-Conflicts hết số bước cho phép, chương trình thông báo chưa tìm được nghiệm trong lượt chạy đó.
- **Bảng và biểu đồ thực nghiệm Glucose3** thể hiện số mệnh đề CNF và thời gian chạy theo N. Phần thời gian solver hiện được đo bao gồm khởi tạo solver, nạp mệnh đề, giải và lấy mô hình.
- **Bảng và biểu đồ so sánh Min-Conflicts** thể hiện tỷ lệ tìm được nghiệm, số bước trung bình và thời gian trung bình của hai cách chọn biến. Trung bình bao gồm cả lượt chưa tìm được nghiệm.
- **Notebook `experiments_task1.ipynb`** chứa các bước thực nghiệm, bảng và biểu đồ. File được lưu kèm kết quả đầu ra của các ô code.
- **Giao diện `gui.py`** hiển thị bàn cờ, cho phép chọn kích thước và thuật toán, sau đó hiển thị kết quả. Quân hậu màu đỏ thể hiện quân đang xung đột.
- **Nội dung Task 1 trong báo cáo chung** trình bày cách mô hình hóa, phương pháp giải và kết quả thực nghiệm.

Chạy giao diện từ thư mục gốc của dự án bằng lệnh `python source/task1/gui.py`. Chạy thực nghiệm trên dòng lệnh bằng `python source/task1/main_task1.py`.

### Vai trò các file chính

| File | Vai trò |
|---|---|
| `board.py` | Lưu vị trí hậu theo từng cột, đếm xung đột và kiểm tra nghiệm. |
| `cnf_encoder.py` | Ánh xạ ô cờ thành biến logic và sinh các mệnh đề CNF. |
| `sat_solver.py` | Gọi Glucose3, lấy nghiệm và ghi thời gian thực hiện. |
| `min_conflicts.py` | Cài đặt Min-Conflicts, cách chọn ngẫu nhiên và heuristic Max-Conflict + Tabu. |
| `main_task1.py` | Chạy thực nghiệm trên dòng lệnh và in bảng kết quả. |
| `gui.py` | Hiển thị bàn cờ và kết quả của thuật toán người dùng chọn. Giao diện nhận N từ 4 đến 50. |
| `experiments_task1.ipynb` | Chạy thực nghiệm, lưu các bảng số liệu và biểu đồ. |
