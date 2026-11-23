# Hướng Dẫn Cài Đặt & Chạy Mã Nguồn (`source/`)

Tài liệu này hướng dẫn cách thiết lập môi trường và khởi chạy trực tiếp từng bài toán từ bên trong thư mục `source/`.

---

## 1. Cài Đặt Môi Trường Nhanh

Mở Terminal (macOS / Linux) hoặc PowerShell (Windows) tại thư mục `source/`:

```bash
# Tạo và kích hoạt môi trường ảo Python (khuyến nghị Python 3.10 - 3.12)
python3 -m venv .venv
source .venv/bin/activate          # Trên Windows PowerShell: .\.venv\Scripts\Activate.ps1

# Cài đặt các thư viện bắt buộc
pip install -r requirement.txt
```

*(Lưu ý: Trên máy Windows hiện tại có sẵn môi trường `F:\Python311\python.exe` đã cài đặt đủ thư viện, bạn có thể thay lệnh `python` bên dưới bằng `& "F:\Python311\python.exe"`).*

---

## 2. Câu Lệnh Chạy Từng Task (Đứng tại thư mục `source/`)

### Task 1: Bài toán N-Queen (Logic mệnh đề `Glucose3` & Tìm kiếm cục bộ `Min-Conflicts`)

Mở giao diện bàn cờ, chọn kích thước và thuật toán rồi nhấn **Solve**:

```bash
python task1/gui.py
```

Giao diện sử dụng Tkinter của Python. Quân hậu màu đỏ cho biết quân đó đang xung đột.

```bash
# Chạy thực nghiệm mặc định (Glucose3 với N=4..50 và đối sánh Min-Conflicts với N=8..100)
python task1/main_task1.py

# Hoặc tùy chỉnh kích thước bàn cờ và số lần thử nghiệm
python task1/main_task1.py --sat-sizes 4 8 16 32 50 --mc-sizes 8 16 32 64 100 --trials 30 --max-steps 2500
```
- Notebook thực nghiệm (đã lưu kết quả và biểu đồ): `task1/experiments_task1.ipynb`.

### Task 2: Trò chơi Tank Battle (Tìm kiếm đối kháng & Giao diện PyGame Arena)
```bash
# Mở giao diện đồ họa PyGame Arena (chọn bản đồ, chọn AI vs AI, Người vs AI, nạp bot nhóm ngoài)
python task2/main_task2.py

# Chạy thực nghiệm đối sánh 4 cấu hình thuật toán trên dòng lệnh (CLI)
python task2/main_task2.py --cli
```
- File Notebook thực nghiệm (đã lưu sẵn toàn bộ kết quả đầu ra và biểu đồ): `task2/benchmark_task2.ipynb`.

### Task 3: Câu đố Kakuro (Bộ giải CSP & Giao diện trực quan hóa PyGame)
```bash
# Mở giao diện đồ họa PyGame Kakuro Visualizer (trực quan hóa miền giá trị {1..9}, cắt tỉa & quay lui)
python task3/main_task3.py

# Chạy kiểm thử toàn bộ 4 bảng Kakuro với 3 chế độ giải trên dòng lệnh (CLI)
python task3/main_task3.py --cli
```
- File Notebook thực nghiệm (đã lưu sẵn toàn bộ kết quả đầu ra và biểu đồ): `task3/experiments_task3.ipynb`.

---

## 3. Hướng Dẫn Tích Hợp Bot Nhóm Khác Vào Task 2 (`external_agents/`)

Đặt file `.py` chứa thuật toán của nhóm bạn vào thư mục `task2/agents/external_agents/`, sau đó nhấn nút **`Reload external_agents/*.py`** trên giao diện PyGame của Task 2. Hệ thống hỗ trợ 2 cách viết:

1. **Cách 1 (Kế thừa lớp OOP `BaseTankAgent`)**: Xem file mẫu `task2/agents/external_agents/sample_oop_bot.py`.
2. **Cách 2 (Viết hàm độc lập `get_action(obs: dict) -> str`)**: Xem file mẫu `task2/agents/external_agents/sample_dict_bot.py` — nhận vào một `dict` thuần chứa toàn bộ trạng thái bàn cờ và trả về 1 trong 6 hành động hợp lệ (`"MOVE_UP"`, `"MOVE_DOWN"`, `"MOVE_LEFT"`, `"MOVE_RIGHT"`, `"FIRE"`, `"STAY"`).
