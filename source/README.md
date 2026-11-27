# Hướng Dẫn Cài Đặt & Chạy Mã Nguồn (`source/`)

Tài liệu hướng dẫn thiết lập môi trường và khởi chạy trực tiếp từng bài toán từ bên trong thư mục `source/`.

---

## 1. Cài Đặt Môi Trường Nhanh

Mở Terminal (macOS / Linux) hoặc PowerShell (Windows) tại thư mục `source/`:

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows PowerShell: .\.venv\Scripts\Activate.ps1
pip install -r requirement.txt
```

*(Trên máy Windows hiện tại có sẵn môi trường `F:\Python311\python.exe` đã cài đặt đủ thư viện, có thể thay lệnh `python` bên dưới bằng `& "F:\Python311\python.exe"`).*

---

## 2. Câu Lệnh Chạy Từng Task (Đứng tại thư mục `source/`)

### Task 1: Bài toán N-Queen (`Glucose3` SAT & `Min-Conflicts`)
```bash
# Mở giao diện PyGame tối giản (chạy ngay, từng bước, phát tự động, so sánh nhanh)
python task1/main_task1.py

# Chạy thực nghiệm đầy đủ trên dòng lệnh (tiếng Việt không dấu tránh lỗi font)
python task1/main_task1.py --cli

# Chạy bộ kiểm chứng tự động toán học và hiệu năng
python task1/main_task1.py --verify
```
- Notebook thực nghiệm (đã lưu đủ output tất cả các cell): `task1/experiments_task1.ipynb`.

### Task 2: Trò chơi Tank Battle (Tìm kiếm đối kháng & Giao diện PyGame tối giản)
```bash
# Mở giao diện đồ họa PyGame tối giản (1160x720, AI vs AI, Người vs AI, nạp bot nhóm ngoài)
python task2/main_task2.py

# Chạy thực nghiệm đối sánh 4 cấu hình thuật toán trên dòng lệnh (tiếng Việt không dấu)
python task2/main_task2.py --cli

# Chạy bộ kiểm chứng tự động 6 nhóm bất biến (vật lý, bất biến, 4 thuật toán, bot ngoài)
python task2/main_task2.py --verify
```
- Các điều khiển trên giao diện: chọn bản đồ, chọn bộ điều khiển `MAX` / `MIN`, `Nạp lại Bot nhóm ngoài`, `Tự chạy`/`Tạm dừng`, `Từng bước`, `Đặt lại` và thanh trượt tốc độ.
- Notebook thực nghiệm (đã lưu đủ output tiếng Việt ở tất cả các cell): `task2/benchmark_task2.ipynb`.

### Task 3: Câu đố Kakuro (Bộ giải CSP & Giao diện PyGame tối giản)
```bash
# Mở giao diện đồ họa PyGame tối giản (1160x720, trực quan CSP & trình soạn thảo)
python task3/main_task3.py

# In mô hình hóa <X, D, C>, bất biến tổng và hiệu quả tiền xử lý 2 tầng (tiếng Việt không dấu)
python task3/main_task3.py --explain-csp

# Chạy benchmark đối sánh 3 chế độ trên 4 bảng mẫu (tiếng Việt không dấu)
python task3/main_task3.py --cli --trials 10

# Chạy bộ kiểm chứng tự động 22 tiêu chí (CSP, 3 chế độ, BoardEditor và trường hợp biên)
python task3/main_task3.py --verify
```
- Các điều khiển trên giao diện: chọn nhanh bảng mẫu (`5×5`, `6×6`, `8×8`, `9×9`), chọn 3 chế độ giải (`Quay lui cơ bản`, `Kiểm tra tiến + MRV`, `AC-3 mở rộng + MRV/Bậc/LCV`), `Phát`/`Tạm dừng`, `Bước tiếp`/`Trước`, `Đặt lại`, `Bước cuối`, thanh tốc độ, và `Sửa bảng` / `Dừng & Sửa bảng` mở trình soạn thảo bảng tùy chỉnh (`BoardEditor` & `Bulk Edit`).
- Notebook thực nghiệm (đã lưu đủ output tiếng Việt ở tất cả các cell): `task3/experiments_task3.ipynb`.

---

## 3. Hướng Dẫn Tích Hợp Bot Nhóm Khác Vào Task 2 (`external_agents/`)

Đặt file `.py` chứa thuật toán của nhóm khác vào `task2/agents/external_agents/`, sau đó nhấn nút **`Nạp lại Bot`** trên giao diện PyGame của Task 2:
1. **Chuẩn OOP**: Kế thừa `task2.agents.base_agent.BaseTankAgent` và cài đặt `choose_action(self, state) -> str` (xem mẫu `sample_oop_bot.py`).
2. **Chuẩn Dictionary Adapter**: Khai báo `BOT_NAME` và hàm `def get_action(obs: dict) -> str` trả về 1 trong 6 hành động hợp lệ `"MOVE_UP"`, `"MOVE_DOWN"`, `"MOVE_LEFT"`, `"MOVE_RIGHT"`, `"FIRE"`, `"STAY"` (xem mẫu `sample_dict_bot.py`).
