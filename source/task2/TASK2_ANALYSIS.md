# Task 2 — Tank Battle: Phân tích đề bài và sản phẩm

## 1. Bài toán Tank Battle là gì?

Tank Battle là trò chơi đối kháng theo lượt giữa hai người chơi trên một bàn cờ ô vuông. Mỗi bên điều khiển một xe tăng và bảo vệ căn cứ của mình. Người chơi cần di chuyển, xoay hướng, bắn đạn và tận dụng tường để phá hủy xe tăng hoặc căn cứ đối phương trước khi đối thủ làm điều tương tự.

Đây là bài toán **tìm kiếm đối kháng trong trò chơi tổng bằng không (zero-sum game)**: lợi ích của MAX là bất lợi của MIN. Chương trình biểu diễn trạng thái bàn đấu, các hành động hợp lệ và luật chuyển trạng thái; sau đó các AI tìm nước đi tốt cho bên đang điều khiển.

## 2. Mô hình và luật chơi

### Trạng thái đầu vào

Một trạng thái trò chơi chứa:

- Kích thước bàn đấu và bản đồ vật cản.
- Vị trí, hướng quay và HP của hai xe tăng (MAX và MIN).
- Vị trí và HP của hai căn cứ.
- Tường gạch có thể bị phá, tường thép không thể bị phá (nếu bản đồ có).
- Đạn đang bay, người chơi tới lượt, số lượt đã đi và giới hạn lượt.

Trạng thái này là đầu vào cho engine khi áp dụng một hành động, và cho agent khi chọn nước đi. Với bot dạng hàm độc lập, hệ thống chuyển trạng thái thành một `obs_dict` mới để bot đọc.

### Hành động

Mỗi lượt, người chơi chọn một trong sáu hành động:

`MOVE_UP`, `MOVE_DOWN`, `MOVE_LEFT`, `MOVE_RIGHT`, `FIRE`, `STAY`.

Hành động di chuyển luôn đổi hướng xe tăng về hướng được chọn; xe chỉ tiến một ô nếu ô đó đi được. Mỗi xe có tối đa một viên đạn đang hoạt động. Đạn tồn tại qua lượt và di chuyển tối đa 3 ô trong chu kỳ; va chạm được kiểm tra từng ô, đạn dừng khi chạm tường, xe tăng hoặc căn cứ.

### HP, kết thúc và điểm kết quả

| Thực thể | HP ban đầu | Sát thương mỗi lần trúng |
|---|---:|---:|
| Xe tăng | 6 | 1 |
| Căn cứ | 9 | 1 |
| Tường gạch | 3 | 1 |
| Tường thép | Không áp dụng | Không thể phá |

Trận đấu kết thúc khi xe tăng hoặc căn cứ của một bên bị phá hủy, hoặc khi đạt giới hạn lượt. Theo góc nhìn của bên được đánh giá, MAX thắng được +1000, MIN thắng được -1000 và hòa được 0.

## 3. AI tìm kiếm đối kháng

Ở mỗi lượt, agent nhận trạng thái hiện tại và trả về một hành động hợp lệ. Bốn cấu hình được yêu cầu:

1. **Minimax:** xét cây hành động luân phiên của hai bên; MAX chọn kết quả lớn nhất và MIN chọn kết quả nhỏ nhất.
2. **Alpha-Beta:** cùng mục tiêu và kết quả minimax, nhưng dùng hai ngưỡng alpha/beta để ngừng xét các nhánh không thể làm thay đổi quyết định.
3. **Heuristic Minimax:** tìm tới độ sâu giới hạn `d`, sau đó dùng `EVAL(s)` để ước lượng trạng thái chưa kết thúc.
4. **Heuristic Alpha-Beta:** kết hợp đánh giá heuristic và cắt tỉa Alpha-Beta. Move Ordering đưa các nước có triển vọng lên xét trước; Transposition Table lưu kết quả trạng thái đã gặp để có thể tái sử dụng.

Hàm `EVAL(s)` trong dự án xem xét chênh lệch HP xe tăng/căn cứ, khoảng cách tiếp cận căn cứ và xe đối phương, đường bắn, tiến độ phá tường và mối đe dọa từ đạn. Đây là ước lượng chiến thuật cho trạng thái chưa kết thúc, không phải kết quả thắng/thua chắc chắn.

## 4. Thực nghiệm cần có

Benchmark được chia thành hai tầng để đánh giá cả độ chính xác tìm kiếm lẫn chi phí tính toán:

- **Tầng 1 — endgame 7×7:** ba thế cờ HP thấp (`Endgame Center Duel`, `Endgame Base Race`, `Endgame Corner Ambush`). So sánh cả bốn cấu hình trên cùng trạng thái, ghi nhận hành động, số trạng thái đã xét, độ sâu, số cutoff, TT hits và thời gian.
- **Tầng 2 — bản đồ đầy đủ 9×9 và 11×11:** so sánh Heuristic Minimax và Heuristic Alpha-Beta ở độ sâu 2, 3, 4. Ghi nhận hành động, states, cutoffs, TT hits và thời gian; notebook có bảng và biểu đồ so sánh.

Các thời gian chạy phụ thuộc máy và lần thực thi; khi trích số liệu vào báo cáo, dùng output notebook được chạy với phiên bản code hiện tại.

## 5. Sản phẩm đầu ra của Task 2

### Mã nguồn

- `config.py`: hằng số người chơi, hành động, HP, sát thương, tốc độ đạn và utility.
- `engine/entities.py`, `engine/game_state.py`, `engine/game_engine.py`, `engine/maps.py`: thực thể, trạng thái, luật chuyển trạng thái và các bản đồ/kịch bản.
- `agents/minimax_agent.py`, `agents/alphabeta_agent.py`, `agents/heuristic_minimax.py`, `agents/heuristic_ab.py`: bốn cấu hình tìm kiếm.
- `agents/evaluation.py`: hàm lượng giá, truy vết mục tiêu và sắp xếp nước đi.
- `agents/base_agent.py`: giao diện agent, metrics và nạp bot ngoài.
- `agents/external_agents/`: hai bot mẫu, một theo OOP và một theo `get_action(obs_dict)`.
- `ui/pygame_arena.py`: giao diện PyGame để chọn bản đồ/controller, chạy hoặc bước từng lượt, xem HP và telemetry.
- `ui/assets/`: 9 sprite dùng trong giao diện; `CREDITS.txt` ghi nguồn Kenney và CC0 1.0.
- `main_task2.py`: khởi chạy giao diện, chạy CLI benchmark hoặc tạo ảnh headless.
- `benchmark_task2.ipynb`: bảng số liệu và biểu đồ thực nghiệm hai tầng.

### Quan sát được khi chạy

- **GUI:** bàn đấu và bảng điều khiển; có thể chọn map, điều khiển MAX/MIN bằng người hoặc AI, chạy tự động/từng bước, reset trận, đổi tốc độ và nạp lại bot ngoài.
- **CLI (`--cli`):** in kết quả so sánh bốn agent trên các endgame, phát hiện bot ngoài và chạy một trận mẫu giới hạn lượt.
- **Notebook:** lưu các bảng benchmark và hình so sánh để dùng trong báo cáo.
- **Ảnh headless:** lưu ảnh giao diện ra đường dẫn được truyền cho tùy chọn `--headless-screenshot`.

## 6. Cách chạy

Chạy từ thư mục gốc repository:

```powershell
# Mở PyGame Arena
python source\task2\main_task2.py

# Chạy benchmark/kiểm tra CLI
python source\task2\main_task2.py --cli

# Tạo ảnh giao diện không mở cửa sổ
python source\task2\main_task2.py --headless-screenshot report\figures\task2_arena_ui.png

# Mở notebook benchmark
jupyter notebook source\task2\benchmark_task2.ipynb
```

### Nạp bot ngoài

Đặt file Python của bot trong `source/task2/agents/external_agents/`, sau đó bấm `Reload bots` trên giao diện. Có thể dùng một trong hai giao diện:

- Bot OOP kế thừa `BaseTankAgent` và triển khai `choose_action(state)`.
- Bot hàm độc lập khai báo `get_action(obs_dict)` và trả về một trong sáu hành động hợp lệ.

Tham khảo `agents/external_agents/sample_oop_bot.py` và `agents/external_agents/sample_dict_bot.py`.
