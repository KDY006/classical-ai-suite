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
# Mở giao diện bàn cờ trực quan (Tkinter)
python task1/gui.py

# Chạy thực nghiệm dòng lệnh (Glucose3 N=4..50 & đối sánh Min-Conflicts N=8..100)
python task1/main_task1.py
```
- Notebook thực nghiệm (đã lưu đủ output tất cả các cell): `task1/experiments_task1.ipynb`.

### Task 2: Trò chơi Tank Battle (Tìm kiếm đối kháng & Giao diện PyGame Arena)
```bash
# Mở giao diện đồ họa PyGame Arena (AI vs AI, Người vs AI, nạp bot nhóm ngoài)
python task2/main_task2.py

# Chạy thực nghiệm đối sánh 4 cấu hình thuật toán trên dòng lệnh (CLI)
python task2/main_task2.py --cli
```
- Các điều khiển trên giao diện: chọn bản đồ, chọn bộ điều khiển `MAX` / `MIN`, `Play`/`Pause`, `Step`, `Reset`, `-`/`+` tốc độ, và `Reload bots`.
- Notebook thực nghiệm (đã lưu đủ output tất cả các cell): `task2/benchmark_task2.ipynb`.

### Task 3: Câu đố Kakuro (Bộ giải CSP, Visualizer & Board Editor trên PyGame)
```bash
# Mở giao diện đồ họa PyGame Kakuro Visualizer & Board Editor
python task3/main_task3.py

# Chạy kiểm thử toàn bộ 4 bảng Kakuro với 3 chế độ giải trên dòng lệnh (CLI)
python task3/main_task3.py --cli
```
- Các điều khiển trên giao diện: `Switch Preset`, đổi chế độ thuật toán (`Advanced: AC-3 + MRV/Degree/LCV`, `Backtracking + FC + MRV`, `Basic Backtracking`), `Auto Play`/`Pause`, `Previous Step`/`Next Step`, `Reset`, `Final State`, thanh kéo `Speed`, và `Edit Board` / `Stop & Edit` để mở trình soạn thảo bảng tùy chỉnh (`BoardEditor`).
- Notebook thực nghiệm (đã lưu đủ output tất cả các cell): `task3/experiments_task3.ipynb`.

---

## 3. Hướng Dẫn Tích Hợp Bot Nhóm Khác Vào Task 2 (`external_agents/`)

Đặt file `.py` chứa thuật toán của nhóm khác vào `task2/agents/external_agents/`, sau đó nhấn nút **`Reload bots`** trên giao diện PyGame của Task 2:
1. **Chuẩn OOP**: Kế thừa `task2.agents.base_agent.BaseTankAgent` và cài đặt `choose_action(self, state) -> str` (xem mẫu `sample_oop_bot.py`).
2. **Chuẩn Dictionary Adapter**: Khai báo `BOT_NAME` và hàm `def get_action(obs: dict) -> str` trả về 1 trong 6 hành động hợp lệ `"MOVE_UP"`, `"MOVE_DOWN"`, `"MOVE_LEFT"`, `"MOVE_RIGHT"`, `"FIRE"`, `"STAY"` (xem mẫu `sample_dict_bot.py`).
