# TỔNG HỢP HOÀN THIỆN NHIỆM VỤ 2 — TRÒ CHƠI ĐẤU TĂNG ĐỐI KHÁNG (TANK BATTLE)

> Tài liệu tổng hợp toàn bộ cơ sở lý thuyết Trò chơi Tổng bằng không (Zero-Sum Game), kiến trúc Lập trình hướng đối tượng (OOP), 4 cấu hình tìm kiếm đối kháng, cơ chế nạp động bot nhóm ngoài, giao diện PyGame tối giản và kết quả thực nghiệm cho **Nhiệm vụ 2 (3.0 điểm)** — Học phần **503043: Nhập môn Trí tuệ Nhân tạo** (Đại học Tôn Đức Thắng).

---

## 1. Đối Chiếu Mức Độ Hoàn Thành Theo Đề Bài & Quy Ước Thiết Kế

| Hạng mục yêu cầu | Tiêu chuẩn tham chiếu | Mức độ hoàn thành & sản phẩm bàn giao |
| :--- | :--- | :--- |
| **Yêu cầu 2.1 (1.0đ):** Mô hình hóa Trò chơi Tổng bằng không (6 thành phần), thông số HP `6/9/3`, đạn bay `3` ô từng bước & thảo luận tìm kiếm đối kháng | [DEBAI.md](file:///d:/3.1.%20AI/Final/DEBAI.md) (II.b.1) | **100%** — Mô hình hóa trọn vẹn trên cấu trúc trạng thái bất biến (`entities.py`, `game_state.py`, `game_engine.py`, `config.py`), bảo toàn đúng thông số sinh lực (`Tank=6`, `Base=9`, `Wall=3`, sát thương `1`), tập `6` hành động và vật lý đạn bay `3` ô/chu kỳ xử lý va chạm từng ô một. |
| **Yêu cầu 2.2 (1.5đ):** Cài đặt thuật toán thời gian thực và đối sánh công bằng **4 cấu hình** trên cùng kịch bản | [DEBAI.md](file:///d:/3.1.%20AI/Final/DEBAI.md) (II.b.2) | **100%** — Cài đặt đủ 4 cấu hình (`MinimaxAgent`, `AlphaBetaAgent`, `HeuristicMinimaxAgent`, `HeuristicAlphaBetaAgent` tích hợp `Move Ordering`, `Transposition Table` và hàm lượng giá `EVAL(s)` có khoảng cách BFS né tường thép $\mathcal{O}(1)$). Thực nghiệm công bằng 2 tầng (trung vị 3 lần) kèm 2 biểu đồ [task2_four_algo_comparison.png](file:///d:/3.1.%20AI/Final/report/figures/task2_four_algo_comparison.png) và [task2_tier2_9x9_vs_11x11.png](file:///d:/3.1.%20AI/Final/report/figures/task2_tier2_9x9_vs_11x11.png). |
| **Yêu cầu 2.3 (0.5đ):** Giao diện **PyGame** & cơ chế nhập/tích hợp thuật toán nhóm khác thi đấu trực tiếp | [DEBAI.md](file:///d:/3.1.%20AI/Final/DEBAI.md) (II.b.3) & [UI.md](file:///d:/3.1.%20AI/Final/UI.md) | **100%** — Giao diện PyGame vector tối giản `1160 × 720` ([pygame_arena.py](file:///d:/3.1.%20AI/Final/source/task2/ui/pygame_arena.py)) đúng 3 tông màu `UI.md`, hỗ trợ AI vs AI, Người chơi vs AI, nạp nóng bot nhóm ngoài qua 2 chuẩn (`OOP` & `Dict Adapter`) trong `external_agents/` và cách ly bất biến an toàn. |
| **Nguyên lý OOP, macOS 13.7.8 & quy ước ngôn ngữ** | [DEBAI.md](file:///d:/3.1.%20AI/Final/DEBAI.md) & Quy ước dự án | **100%** — Tách rời tuyệt đối Engine/Agents khỏi PyGame (`0` lệnh `import pygame` trong lõi); không dùng API riêng của Windows; tiếng Việt có dấu trên PyGame UI, Matplotlib, Notebook & `TASK2.md`; tiếng Việt không dấu (ASCII thuần) trên CLI (`0` ký tự ngoài ASCII) và toàn bộ comment/docstring; giữ nguyên 100% outputs trên [benchmark_task2.ipynb](file:///d:/3.1.%20AI/Final/source/task2/benchmark_task2.ipynb). |

---

## 2. Kiến Trúc OOP & Tổ Chức Mã Nguồn (`source/task2/`)

Toàn bộ Nhiệm vụ 2 được tổ chức độc lập thành 3 tầng rõ ràng (Engine – Agents – UI):

| Tệp / Thư mục | Tầng kiến trúc | Vai trò & Lớp OOP chính |
| :--- | :--- | :--- |
| [config.py](file:///d:/3.1.%20AI/Final/source/task2/config.py) | Cấu hình chung | Hằng số luật chơi (`TANK_INITIAL_HP=6`, `BASE_INITIAL_HP=9`, `WALL_INITIAL_HP=3`, `DAMAGE_PER_HIT=1`, `BULLET_SPEED_PER_CYCLE=3`, 6 hành động `ALL_ACTIONS`, nhãn hành động có/không dấu). |
| [engine/entities.py](file:///d:/3.1.%20AI/Final/source/task2/engine/entities.py) | Engine (Thực thể) | Lớp cơ sở `Entity` và 5 thực thể bất biến (`@dataclass(frozen=True, slots=True)`): `Tank`, `Base`, `BrickWall`, `SteelWall`, `Bullet`. |
| [engine/game_state.py](file:///d:/3.1.%20AI/Final/source/task2/engine/game_state.py) | Engine (Trạng thái) | Lớp `GameState` bất biến dùng `MappingProxyType` và `frozenset`; cài đặt `legal_actions()`, `winner()`, `is_terminal()`, `utility()`, `state_key()`, `to_observation_dict()`. |
| [engine/game_engine.py](file:///d:/3.1.%20AI/Final/source/task2/engine/game_engine.py) | Engine (Chuyển trạng thái) | `TankBattleEngine`, `StepEvent`, `MatchStepSnapshot`: xử lý `RESULT(s, a)`, vật lý đạn bay 3 ô từng bước dừng ngay tại chướng ngại vật đầu tiên, và generator `iter_match()` thuần Python. |
| [engine/maps.py](file:///d:/3.1.%20AI/Final/source/task2/engine/maps.py) | Engine (Bản đồ) | 6 kịch bản 2 tầng: Tầng 1 (`7×7` tàn cuộc) và Tầng 2 (`9×9` & `11×11` đầy đủ máu). |
| [agents/base_agent.py](file:///d:/3.1.%20AI/Final/source/task2/agents/base_agent.py) | Tác tử (Cơ sở & Plugin) | `BaseTankAgent(ABC)`, `SearchMetrics`, `DictAdapterTankAgent`, trình quét nạp động `discover_external_agents()` và cơ chế phòng thủ `safe_choose_action()`. |
| [agents/evaluation.py](file:///d:/3.1.%20AI/Final/source/task2/agents/evaluation.py) | Tác tử (Lượng giá) | `TacticalEvaluator`: hàm lượng giá phản đối xứng `evaluate(state, perspective)` dùng khoảng cách BFS né tường thép có cache $\mathcal{O}(1)$ và `order_actions()` ưu tiên nước đi bảng băm TT. |
| [agents/minimax_agent.py](file:///d:/3.1.%20AI/Final/source/task2/agents/minimax_agent.py) | Tác tử (Cấu hình 1) | `MinimaxAgent`: Minimax thuần túy. |
| [agents/alphabeta_agent.py](file:///d:/3.1.%20AI/Final/source/task2/agents/alphabeta_agent.py) | Tác tử (Cấu hình 2) | `AlphaBetaAgent`: Alpha-Beta thuần túy (bảo toàn chính xác giá trị & nước đi của Minimax). |
| [agents/heuristic_minimax.py](file:///d:/3.1.%20AI/Final/source/task2/agents/heuristic_minimax.py) | Tác tử (Cấu hình 3) | `HeuristicMinimaxAgent`: Heuristic Minimax cắt tại độ sâu $d$. |
| [agents/heuristic_ab.py](file:///d:/3.1.%20AI/Final/source/task2/agents/heuristic_ab.py) | Tác tử (Cấu hình 4) | `HeuristicAlphaBetaAgent`: Heuristic Alpha-Beta tích hợp `Move Ordering` + `Transposition Table` (`EXACT`/`LOWER`/`UPPER`). |
| [agents/external_agents/](file:///d:/3.1.%20AI/Final/source/task2/agents/external_agents/sample_oop_bot.py) | Bot nhóm ngoài | 2 bot mẫu kiểm chứng: `sample_oop_bot.py` (kế thừa `BaseTankAgent`) và `sample_dict_bot.py` (hàm `get_action(obs)` có BFS né tường thép). |
| [ui/pygame_arena.py](file:///d:/3.1.%20AI/Final/source/task2/ui/pygame_arena.py) | Giao diện (View) | `TankBattleArenaUI` & `HumanController` bằng đồ họa vector PyGame tối giản `1160 × 720` tuân thủ [UI.md](file:///d:/3.1.%20AI/Final/UI.md). |
| [main_task2.py](file:///d:/3.1.%20AI/Final/source/task2/main_task2.py) | Điều phối & CLI | `Task2ExperimentRunner` quản lý khởi chạy PyGame mặc định, `--cli`, `--explain-model`, `--verify` và `--headless-screenshot`. |
| [benchmark_task2.ipynb](file:///d:/3.1.%20AI/Final/source/task2/benchmark_task2.ipynb) | Sổ tay thực nghiệm | Thực nghiệm đầy đủ 4 phần đã chạy sẵn lưu 100% outputs và biểu đồ. |

---

## 3. Yêu Cầu 2.1 — Mô Hình Hóa Trò Chơi Tổng Bằng Không (Zero-Sum Game)

Trò chơi Đấu Tăng được hình thức hóa thành bộ 6 thành phần $\mathcal{G} = \langle S_0, \text{PLAYER}, \text{ACTIONS}, \text{RESULT}, \text{TERMINAL}, \text{UTILITY} \rangle$:

1. **Trạng thái khởi đầu $S_0$ (`GameState`):** Lưới kích thước $R \times C$, hai xe tăng (tọa độ, hướng quay mặt, `HP = 6`), hai căn cứ (`HP = 9`), tập tường gạch (`HP = 3`), tập tường thép bất tử, danh sách đạn đang bay (tối đa 1 viên/phe), phe đi trước `MAX` và bộ đếm nửa lượt `ply`.
2. **Người chơi $\text{PLAYER}(s) \in \{\text{MAX} (1), \text{MIN} (2)\}$:** Hai phe luân phiên đi từng lượt.
3. **Tập hành động $\text{ACTIONS}(s)$:** Gồm đúng **6 hành động**: `MOVE_UP`, `MOVE_DOWN`, `MOVE_LEFT`, `MOVE_RIGHT`, `FIRE`, `STAY`. Hàm `legal_actions()` tự động loại bỏ các nước đi vô nghĩa (ví dụ `FIRE` khi phe hiện tại đã có đạn đang bay, hoặc đâm vào ô bị chặn khi nòng đã quay sẵn về hướng đó) để giảm hệ số nhánh trung bình mà không làm mất hành động chiến thuật nào.
4. **Hàm chuyển trạng thái $\text{RESULT}(s, a)$ (`TankBattleEngine.apply_action`):**
   - *Hành động xe tăng:* `MOVE_DIR` luôn xoay hướng nòng về `DIR` và tiến `1` ô nếu ô đích trống (nếu đi trúng viên đạn địch đang nằm ở ô đích sẽ chịu `-1 HP` và viên đạn bị hủy); `FIRE` tạo viên đạn tại vị trí xe theo hướng nòng hiện tại; `STAY` giữ nguyên vị trí.
   - *Vật lý đạn bay 3 ô/chu kỳ xử lý từng ô một:* Viên đạn di chuyển tuần tự tối đa `3` bước `1` ô; ngay sau **mỗi bước 1 ô** kiểm tra va chạm tức thời theo thứ tự: (1) ra biên $\to$ biến mất, (2) đụng đạn đối phương $\to$ triệt tiêu cả hai, (3) chạm tường thép $\to$ dừng lại, (4) trúng tường gạch $\to$ `-1 HP` & dừng, (5) trúng căn cứ $\to$ `-1 HP` & dừng, (6) trúng xe tăng $\to$ `-1 HP` & dừng. Nếu đi hết `3` ô chưa trúng gì, đạn tồn tại tiếp sang lượt sau.
5. **Kiểm tra kết thúc $\text{TERMINAL}(s)$:** Kết thúc ngay khi `Tank.hp <= 0` hoặc `Base.hp <= 0` của ít nhất một phe, hoặc khi `ply >= max_plies`.
6. **Hàm tiện ích $\text{UTILITY}(s, p)$:** Tổng bằng không chặt chẽ ($\text{UTILITY}(s, \text{MAX}) + \text{UTILITY}(s, \text{MIN}) = 0$): `+1000` nếu phe $p$ thắng, `-1000` nếu phe $p$ thua và `0` nếu hòa. Ở nút kết thúc trong cây tìm kiếm, áp dụng chiết khấu cực nhỏ `±0.01 × depth` để ưu tiên thắng sớm hơn và kéo dài trận đấu nếu buộc phải thua.

---

## 4. Yêu Cầu 2.2 — Hàm Lượng Giá Chiến Thuật, Tối Ưu Hóa & Thực Nghiệm 2 Tầng

### 4.1. Hàm lượng giá phản đối xứng `EVAL(s)` và các kỹ thuật tối ưu
Để vừa đảm bảo xe tăng chủ động bọc sườn né tường thép `#`, công phá tường gạch bảo vệ căn cứ và giao tranh quyết liệt (khắc phục hoàn toàn lỗi hòa lặp `6/9 vs 6/9`), vừa đảm bảo tính đối xứng chuẩn Zero-Sum (`EVAL(s, MAX) + EVAL(s, MIN) = 0`), `TacticalEvaluator.evaluate(s, p)` kết hợp 5 nhóm đặc trưng:

$$\text{EVAL}(s, p) = 130\,\Delta\text{HP}_{\text{tank}} + 165\,\Delta\text{HP}_{\text{base}} + 7{,}5\,\Delta\text{HP}_{\text{shield}} + 6\,\Delta d_{\text{BFS-base}} + \Delta\text{Offense}(s) + 70\,\Delta\text{BulletThreat}(s)$$

Trong đó:
- **Khoảng cách BFS né tường thép có cache $\mathcal{O}(1)$ (`steel_aware_distance`):** Tính BFS ngắn nhất trên lưới tránh các ô tường thép tĩnh `#` và lưu vào cache theo `(rows, cols, steel_walls, target)` — giúp xe tăng chủ động rẽ vòng quanh trụ thép trung tâm mà không tốn chi phí duyệt lại.
- **Điểm lá chắn căn cứ (`_base_shield_hp`):** Tổng HP các tường gạch trong bán kính Manhattan $\le 2$ quanh mỗi căn cứ, tạo phần thưởng bền vững ngay khi xe tăng làm sứt mẻ tường bảo vệ của địch.
- **Tuyến bắn & trục tấn công (`_positional_offense_score`):** Thưởng tuyến bắn thẳng vào xe/căn cứ địch, thưởng chiếm trục ngang/dọc thông thoáng không bị thép chắn, phạt nhẹ `-5.0` khi quay sát mặt vào tường thép bất tử.
- **Tối ưu Alpha-Beta (`HeuristicAlphaBetaAgent`):** Kết hợp **Move Ordering** (ưu tiên nước đi tốt nhất `tt_best_action` từ bảng băm, kế đến bắn trúng mục tiêu, né đạn, rút ngắn khoảng cách BFS) và **Transposition Table** (`EXACT`, `LOWER`, `UPPER` có kiểm tra độ sâu an toàn đối với điểm chiết khấu kết thúc), đảm bảo giá trị lượng giá khớp tuyệt đối với `HeuristicMinimaxAgent` cùng độ sâu.

### 4.2. Thực nghiệm Tầng 1: Đối sánh công bằng 4 cấu hình trên Tàn cuộc `7×7` (trung vị 3 lần)

| Kịch bản (`7×7`) | Cấu hình thuật toán | Nước đi | Số trạng thái | Độ sâu | Cắt tỉa | Trúng TT | Thời gian (ms) |
| :--- | :--- | :-: | :-: | :-: | :-: | :-: | :-: |
| **Tàn cuộc Đối đầu** | Minimax thuần | BẮN | 30.278 | 6 | 0 | 0 | 1.355,27 |
| **Tàn cuộc Đối đầu** | Alpha-Beta thuần | BẮN | 2.213 | 6 | 539 | 0 | 104,71 |
| **Tàn cuộc Đối đầu** | Heuristic Minimax (`d=4`) | BẮN | 1.004 | 4 | 0 | 0 | 96,45 |
| **Tàn cuộc Đối đầu** | **Heuristic Alpha-Beta (`d=4`)** | **BẮN** | **34** | **4** | **17** | **2** | **3,84** |
| **Tàn cuộc Đua phá căn cứ** | Minimax thuần | TRÁI | 35.824 | 6 | 0 | 0 | 1.561,37 |
| **Tàn cuộc Đua phá căn cứ** | Alpha-Beta thuần | TRÁI | 975 | 6 | 395 | 0 | 61,40 |
| **Tàn cuộc Đua phá căn cứ** | Heuristic Minimax (`d=4`) | TRÁI | 1.369 | 4 | 0 | 0 | 133,64 |
| **Tàn cuộc Đua phá căn cứ** | **Heuristic Alpha-Beta (`d=4`)** | **TRÁI** | **220** | **4** | **51** | **14** | **22,74** |
| **Tàn cuộc Phục kích góc** | Minimax thuần | TRÁI | 39.326 | 6 | 0 | 0 | 1.821,64 |
| **Tàn cuộc Phục kích góc** | Alpha-Beta thuần | TRÁI | 1.418 | 6 | 402 | 0 | 70,64 |
| **Tàn cuộc Phục kích góc** | Heuristic Minimax (`d=4`) | PHẢI | 1.266 | 4 | 0 | 0 | 155,06 |
| **Tàn cuộc Phục kích góc** | **Heuristic Alpha-Beta (`d=4`)** | **PHẢI** | **126** | **4** | **23** | **1** | **20,81** |

- **Biểu đồ đối sánh Tầng 1:** [task2_four_algo_comparison.png](file:///d:/3.1.%20AI/Final/report/figures/task2_four_algo_comparison.png).
- **Nhận xét:** Trên cả 3 thế cờ Tầng 1, `Alpha-Beta thuần` cho ra **đúng cùng giá trị và nước đi tối ưu** như `Minimax thuần` nhưng giảm `13,7–36,7` lần số trạng thái duyệt. Khi kết hợp thêm `EVAL(s)`, Move Ordering và Transposition Table, `Heuristic Alpha-Beta (d=4)` chỉ duyệt **`34` trạng thái** trên kịch bản Đối đầu — giảm tới **890 lần** số trạng thái và nhanh hơn **353 lần** (`3,84 ms` so với `1.355,27 ms`).

### 4.3. Thực nghiệm Tầng 2: Đấu trường đầy đủ máu `9×9` & `11×11` (độ sâu $d \in \{2, 3, 4\}$)

| Bản đồ đầy đủ máu (`6/9/3 HP`) | $d$ | Thuật toán | Nước đi | Số trạng thái | Cắt tỉa | Trúng TT | Thời gian (ms) |
| :--- | :-: | :--- | :-: | :-: | :-: | :-: | :-: |
| **Đấu trường Cổ điển (`9×9`)** | 2 | Heuristic Minimax | BẮN | 31 | 0 | 0 | 3,36 |
| **Đấu trường Cổ điển (`9×9`)** | 2 | **Heuristic Alpha-Beta** | **BẮN** | **15** | **4** | **0** | **2,30** |
| **Đấu trường Cổ điển (`9×9`)** | 3 | Heuristic Minimax | BẮN | 166 | 0 | 0 | 15,78 |
| **Đấu trường Cổ điển (`9×9`)** | 3 | **Heuristic Alpha-Beta** | **BẮN** | **46** | **8** | **0** | **5,78** |
| **Đấu trường Cổ điển (`9×9`)** | 4 | Heuristic Minimax | BẮN | 895 | 0 | 0 | 90,65 |
| **Đấu trường Cổ điển (`9×9`)** | 4 | **Heuristic Alpha-Beta** | **BẮN** | **94** | **34** | **5** | **12,89** |
| **Công thành Pháo đài (`11×11`)** | 2 | Heuristic Minimax | LÊN | 43 | 0 | 0 | 5,01 |
| **Công thành Pháo đài (`11×11`)** | 2 | **Heuristic Alpha-Beta** | **LÊN** | **23** | **4** | **0** | **2,86** |
| **Công thành Pháo đài (`11×11`)** | 3 | Heuristic Minimax | TRÁI | 253 | 0 | 0 | 33,89 |
| **Công thành Pháo đài (`11×11`)** | 3 | **Heuristic Alpha-Beta** | **TRÁI** | **93** | **16** | **1** | **15,37** |
| **Công thành Pháo đài (`11×11`)** | 4 | Heuristic Minimax | TRÁI | 1.478 | 0 | 0 | 271,46 |
| **Công thành Pháo đài (`11×11`)** | 4 | **Heuristic Alpha-Beta** | **TRÁI** | **328** | **84** | **22** | **68,07** |

- **Biểu đồ đối sánh Tầng 2:** [task2_tier2_9x9_vs_11x11.png](file:///d:/3.1.%20AI/Final/report/figures/task2_tier2_9x9_vs_11x11.png).
- **Nhận xét:** Tại $d = 4$, `Heuristic Alpha-Beta` giảm **89,5%** số trạng thái trên bản đồ `9×9` (`94` vs `895`, chỉ `12,89 ms/lượt`) và giảm **77,8%** trên bản đồ `11×11` (`328` vs `1.478`, `68,07 ms/lượt`), đảm bảo vận hành mượt thời gian thực trên cấu hình chấm bài macOS 13.7.8 Intel Core i5.

---

## 5. Yêu Cầu 2.3 — Giao Diện PyGame Tối Giản & Cơ Chế Nạp Bot Nhóm Ngoài

### 5.1. Giao diện PyGame vector tối giản (`pygame_arena.py`)
Thiết kế tuân thủ tuyệt đối [UI.md](file:///d:/3.1.%20AI/Final/UI.md):
- **Cửa sổ chuẩn `1160 × 720`**, bảng màu 3 tông (Giấy/Mực trung tính, Xanh ngọc trầm `#0F766E` cho phe `MAX` và nút chính, Đỏ gạch trầm `#C83E37` cho phe `MIN` và va chạm).
- **Đồ họa vector hoàn toàn độc lập** (không phụ thuộc file PNG rời hay API Windows): tường thép tối giản kẻ chéo, tường gạch có 3 nấc HP (`3 -> 2 -> 1`) rõ ràng, căn cứ pháo đài hình thoi kèm thanh HP, xe tăng xoay nòng 4 hướng kèm viền `2px` đánh dấu phe đang tới lượt, vệt đạn bay nét đứt theo từng ô và vòng tròn va chạm khi trúng mục tiêu.
- **Sidebar 3 nhóm gọn gàng:** chuyển 6 kịch bản bản đồ, chọn bộ điều khiển `MAX`/`MIN` (4 thuật toán + `Người chơi` + các bot ngoài), nút `Nạp lại Bot nhóm ngoài`, điều khiển `Tự chạy`/`Tạm dừng`, `Từng bước`, `Đặt lại`, thanh trượt tốc độ, thanh sinh lực 2 phe và bảng thông số tìm kiếm (`nước đi`, `độ sâu`, `số nút`, `cắt tỉa`, `TT`, `ms`).
- **Ảnh chụp minh họa:** [task2_arena_ui.png](file:///d:/3.1.%20AI/Final/report/figures/task2_arena_ui.png).

### 5.2. Cơ chế nạp động bot nhóm khác & Kết quả giải đấu đối kháng
Chỉ cần chép file `.py` của nhóm khác vào `source/task2/agents/external_agents/` và bấm **`Nạp lại Bot nhóm ngoài`**, `discover_external_agents()` tự động phát hiện cả 2 chuẩn:
1. **Chuẩn 1 (OOP):** Kế thừa `BaseTankAgent` và cài đặt `choose_action(self, state: GameState) -> str` (mẫu: [sample_oop_bot.py](file:///d:/3.1.%20AI/Final/source/task2/agents/external_agents/sample_oop_bot.py)).
2. **Chuẩn 2 (Dict Adapter):** Khai báo `BOT_NAME` và hàm thuần `get_action(obs: dict) -> str` không cần import lớp nội bộ (mẫu: [sample_dict_bot.py](file:///d:/3.1.%20AI/Final/source/task2/agents/external_agents/sample_dict_bot.py)).

Kết quả giải đấu đầy đủ máu (`Tank=6`, `Base=9`, `Wall=3`) trên bản đồ **Giao lộ Hỏa lực (`9×9`)**:

| Phe MAX (Người chơi 1) | Phe MIN (Người chơi 2) | Số lượt | Máu cuối (`MAX Xe/CC vs MIN Xe/CC`) | TG TB MAX (ms) | Kết quả chung cuộc |
| :--- | :--- | :-: | :-: | :-: | :--- |
| **Heuristic Alpha-Beta (sâu 4)** | Heuristic Minimax (sâu 2) | 119 | `6/9` vs `6/0` | 22,01 | **Heuristic Alpha-Beta (sâu 4) thắng** *(phá căn cứ)* |
| **Heuristic Alpha-Beta (sâu 4)** | Bot ngoài: Săn căn cứ (Dict) | 15 | `1/9` vs `0/9` | 14,12 | **Heuristic Alpha-Beta (sâu 4) thắng** *(hạ xe tăng)* |
| **Heuristic Alpha-Beta (sâu 4)** | Bot ngoài: Xung kích (OOP) | 15 | `1/9` vs `0/9` | 11,56 | **Heuristic Alpha-Beta (sâu 4) thắng** *(hạ xe tăng)* |

---

## 6. Hướng Dẫn Chạy & Kiểm Chứng Tự Động

Đứng tại thư mục gốc dự án (thay `python` bằng `& "F:\Python311\python.exe"` nếu chạy trực tiếp trên máy Windows hiện tại):

```bash
# 1. Mo giao dien PyGame Dau Tang toi gian (mac dinh)
python source/task2/main_task2.py

# 2. Chay bo kiem chung tu dong 6 nhom (vat ly, bat bien, 4 thuat toan, bot ngoai, tran dau)
python source/task2/main_task2.py --verify

# 3. Chay tron bo thuc nghiem CLI 2 tang & giai dau (tieng Viet khong dau)
python source/task2/main_task2.py --cli

# 4. In tom tat mo hinh 6 thanh phan Zero-Sum Game & minh hoa vat ly dan 3 o
python source/task2/main_task2.py --explain-model

# 5. Xuat anh chup giao dien PyGame che do khong cua so
python source/task2/main_task2.py --headless-screenshot task2_preview.png --map crossfire_9x9 --turns 9
```

---

## 7. Trọng Tâm Chuẩn Bị Phỏng Vấn Vấn Đáp (Task 2)

1. **Hàm `RESULT(s, a)` xử lý đạn bay 3 ô/chu kỳ như thế nào nếu ô thứ 2 là tường gạch còn 3 HP và ô thứ 3 là xe tăng địch?**
   - Trong `_transition()`, vòng lặp `for _ in range(3)` gọi `_advance_bullet_one_cell()` tuần tự từng ô: ô thứ 1 trống nên đạn bay qua; tới ô thứ 2 gặp tường gạch nên trừ tường còn `2 HP`, đánh dấu `active=False` và kết thúc ngay (`return`) — viên đạn dừng lập tức, không bay tiếp sang ô thứ 3 và xe tăng phía sau hoàn toàn an toàn.
2. **Tại sao phải thiết kế thực nghiệm 2 tầng để so sánh 4 cấu hình thuật toán?**
   - Vì ván đầy máu (`Tank=6`, `Base=9`, sát thương `1`) cần tối thiểu `12–20` nửa lượt mới có bên bị phá hủy, cây trò chơi đạt $6^{15} \approx 4{,}7 \times 10^{11}$ trạng thái nên `Minimax thuần` và `Alpha-Beta thuần` không thể duyệt hết. Tầng 1 (Tàn cuộc `7×7` còn `1–2 HP`, giới hạn `6 ply`) cho phép cả 4 cấu hình chạy công bằng trên cùng một thế cờ; Tầng 2 (`9×9`, `11×11` đầy máu) đánh giá hiệu năng thời gian thực của 2 cấu hình có hàm lượng giá ở $d = 2, 3, 4$.
3. **Làm sao chứng minh `Alpha-Beta` và `Transposition Table` cài đặt đúng không làm sai lệch quyết định?**
   - Bộ kiểm chứng `--verify` (Nhóm 3 & 4) kiểm tra trực tiếp `AlphaBetaAgent` cho ra đúng cùng `best_value` và `action` với `MinimaxAgent` trên cả 3 bản đồ Tầng 1, đồng thời `HeuristicAlphaBetaAgent` cho ra đúng cùng `best_value` với `HeuristicMinimaxAgent` ở cùng độ sâu trên cả 3 bản đồ Tầng 2 (nhờ kiểm tra an toàn độ sâu TT với điểm chiết khấu kết thúc).
4. **Tại sao thêm khoảng cách BFS né tường thép và điểm lá chắn gạch vào `EVAL(s)`?**
   - Dùng khoảng cách Manhattan thuần khiến xe tăng bị hút vào cột giữa và kẹt lặp phía sau tường thép bất tử `#` (hòa thụ động `6/9 vs 6/9`). Khoảng cách BFS né tường thép tĩnh (cache $\mathcal{O}(1)$) định hướng xe tăng rẽ bọc sườn tự nhiên, còn điểm lá chắn căn cứ (`7,5 × ΔHP_shield`) thưởng trực tiếp cho mỗi phát bắn phá tường bảo vệ địch.
5. **Hệ thống bảo vệ `GameState` như thế nào khi nạp bot từ nhóm khác?**
   - `GameState` là `@dataclass(frozen=True)` bọc toàn bộ `dict` bằng `MappingProxyType` và các tập hợp bằng `frozenset`/`tuple`, nên mọi thao tác cố tình sửa trạng thái đều bị chặn ngay bằng `TypeError`. Bên cạnh đó `safe_choose_action()` chạy trong khối `try/except`, kiểm tra hành động trả về nằm trong `ALL_ACTIONS`, nếu lỗi hoặc sai chuẩn tự động chuyển an toàn về `STAY`.
