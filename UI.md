# QUY ƯỚC THIẾT KẾ GIAO DIỆN — PHONG CÁCH TỐI GIẢN (MINIMALISM)

Tài liệu này là bộ tiêu chuẩn ràng buộc thiết kế giao diện đồ họa (**PyGame**) cho toàn bộ **3 Nhiệm vụ** (`task1/`, `task2/`, `task3/`) của Đồ án cuối kỳ **503043 – Nhập môn Trí tuệ Nhân tạo**, đảm bảo đồng bộ thẩm mỹ, dễ thao tác khi demo/vấn đáp và chạy ổn định trên môi trường chấm bài **macOS 13.7.8 (Intel Core i5)** cũng như **Windows**.

---

## 1. Triết Lý Thiết Kế: Tối Giản (Minimalism)

Lấy cảm hứng từ các ứng dụng năng suất và đọc nội dung hiện đại (*Notion*, *Medium*), giao diện tuân thủ 4 nguyên tắc cốt lõi:

1. **Khoảng trắng rộng rãi (Negative Space):** Ưu tiên không gian thở quanh bàn cờ, lưới câu đố và các khối điều khiển (`padding >= 24px`, khoảng cách giữa các phần tử `12–16px`). Không nhồi nhét thông tin dày đặc.
2. **Bảng màu tiết chế (Tối đa 3 tông chủ đạo):** Hơn 85% diện tích sử dụng tông trung tính (giấy trắng – xám nhạt – mực đen); chỉ dùng 2 tông nhấn có ngữ nghĩa rõ ràng (tích cực/hợp lệ và cảnh báo/xung đột).
3. **Typography làm điểm tựa phân cấp:** Phân biệt thông tin bằng kích thước, độ đậm và khoảng cách dòng rõ ràng, thay vì lạm dụng khung viền, màu nền sặc sỡ hay biểu tượng trang trí.
4. **Loại bỏ hoàn toàn chi tiết thừa:** Không dùng đổ bóng nặng, không dùng dải màu chuyển sắc (gradient), không dùng viền dày nhiều lớp, không chèn hoạt họa trang trí không phục vụ trực quan hóa thuật toán.

---

## 2. Hệ Thống Màu Sắc (Giới Hạn 3 Tông Chủ Đạo)

Mọi giao diện PyGame chỉ được sử dụng các mã màu chuẩn dưới đây:

### Tông 1 — Trung Tính (Giấy & Mực — ~85% diện tích)
| Tên hằng số | Mã HEX | Giá trị RGB | Vai trò sử dụng |
| :--- | :---: | :---: | :--- |
| `BG_CANVAS` | `#FAFAFA` | `(250, 250, 250)` | Nền chính cửa sổ (trắng ngà dịu mắt) |
| `SURFACE` | `#FFFFFF` | `(255, 255, 255)` | Bề mặt bàn cờ, ô sáng, thẻ/nút phụ |
| `SURFACE_SUBTLE` | `#F3F4F6` | `(243, 244, 246)` | Ô cờ tối nhẹ, ô gợi ý Kakuro, nền hover |
| `SURFACE_ACTIVE` | `#E5E7EB` | `(229, 231, 235)` | Nền nhấn khi chọn / di chuột vào nút phụ |
| `BORDER` | `#E5E7EB` | `(229, 231, 235)` | Đường kẻ phân cách mảnh `1px`, viền ô/nút |
| `BORDER_STRONG` | `#9CA3AF` | `(156, 163, 175)` | Viền ngoài khung bàn cờ / ô đang focus |
| `TEXT_PRIMARY` | `#111827` | `(17, 24, 39)` | Tiêu đề, chữ chính, con số đã xác nhận, quân cờ |
| `TEXT_SECONDARY` | `#6B7280` | `(107, 114, 128)` | Nhãn phụ, chú thích, ứng viên miền giá trị |

### Tông 2 — Xanh Ngọc Trầm (Hành Động Chính / Hợp Lệ / Phe MAX — ~10% diện tích)
| Tên hằng số | Mã HEX | Giá trị RGB | Vai trò sử dụng |
| :--- | :---: | :---: | :--- |
| `ACCENT_PRIMARY` | `#0F766E` | `(15, 118, 110)` | Nút chính (Primary CTA), nghiệm hợp lệ, ô đã giải, phe `MAX` |
| `ACCENT_PRIMARY_HOVER` | `#115E59` | `(17, 94, 89)` | Trạng thái di chuột của nút chính |
| `ACCENT_PRIMARY_SOFT` | `#E6F4F1` | `(230, 244, 241)` | Nền nhạt đánh dấu ô hợp lệ / vùng hoàn thành |

### Tông 3 — Đỏ Gạch Trầm (Xung Đột / Cắt Tỉa / Quay Lui / Phe MIN — ~5% diện tích)
| Tên hằng số | Mã HEX | Giá trị RGB | Vai trò sử dụng |
| :--- | :---: | :---: | :--- |
| `ACCENT_ALERT` | `#C83E37` | `(200, 62, 55)` | Quân hậu xung đột, tia tấn công, số bị loại/quay lui, phe `MIN` |
| `ACCENT_ALERT_SOFT` | `#FCEBEA` | `(252, 235, 234)` | Nền cảnh báo nhẹ (ô xung đột / ô miền rỗng khi quay lui) |

> **Quy tắc nhấn trạng thái đang xét (Active Focus):** Để giữ nghiêm giới hạn 3 tông màu, ô hoặc quân cờ đang được thuật toán chọn xử lý (cột `Min-Conflicts` vừa chọn, ô `MRV` đang gán ở Kakuro) sử dụng **viền đậm `2px` màu `TEXT_PRIMARY` (`#111827`)** kết hợp nền `SURFACE_SUBTLE` (`#F3F4F6`) hoặc viền `ACCENT_PRIMARY` (`#0F766E`), không thêm tông màu thứ 4.

---

## 3. Hệ Thống Kiểu Chữ (Typography) & Ngôn Ngữ

### 3.1. Font chữ đa nền tảng (macOS 13.7.8 & Windows)
Sử dụng `pygame.font.SysFont` theo danh sách ưu tiên (tự động chọn font có sẵn hỗ trợ đầy đủ tiếng Việt có dấu, không cần đóng gói file `.ttf` rời):
- **Chữ giao diện (Sans-serif):** `["SF Pro Display", "Helvetica Neue", "Segoe UI", "Arial", "DejaVu Sans"]`
- **Số liệu & bảng thông số (Monospace):** `["SF Mono", "Menlo", "Consolas", "Courier New", "DejaVu Sans Mono"]`

### 3.2. Phân cấp kích thước (Type Scale)
| Cấp độ | Cỡ chữ | Độ đậm | Màu mặc định | Ứng dụng |
| :--- | :---: | :---: | :---: | :--- |
| `H1` (Tiêu đề cửa sổ) | `20px` | Bold | `TEXT_PRIMARY` | Tên bài toán trên thanh đầu trang |
| `H2` (Tiêu đề nhóm) | `12px` | Bold | `TEXT_SECONDARY` | Nhãn phân khu bên sidebar (`CẤU HÌNH`, `ĐIỀU KHIỂN`, `THÔNG SỐ`) |
| `Body` (Nội dung / Nút) | `14px` | Regular / Medium | `TEXT_PRIMARY` | Nhãn nút bấm, tên thuật toán, trạng thái |
| `Mono` (Số liệu) | `13px` | Regular / Bold | `TEXT_PRIMARY` | Giá trị đo thời gian, số bước, số mệnh đề, HP |
| `Caption` (Chú thích) | `12px` | Regular | `TEXT_SECONDARY` | Mô tả ngắn, chú giải màu, số ứng viên miền |

### 3.3. Quy ước ngôn ngữ xuyên suốt dự án
- **Giao diện PyGame, biểu đồ Matplotlib và Markdown trong Notebook:** **Tiếng Việt có dấu** ngắn gọn, tự nhiên, không viết tắt khó hiểu.
- **Đầu ra dòng lệnh (CLI terminal), thông báo ngoại lệ và comment/docstring trong mã nguồn `.py`:** **Tiếng Việt không dấu** (ASCII thuần) để tránh lỗi hiển thị font/encoding trên mọi terminal Windows & macOS.

---

## 4. Bố Cục Chuẩn & Thành Phần Tương Tác

### 4.1. Kích thước cửa sổ chuẩn: `1160 x 720` px
Kích thước này vừa khít hoàn toàn trên màn hình laptop **macOS 13.7.8** (`1280x800` / `1440x900` có thanh menu & Dock) cũng như màn hình Windows chuẩn, không bị tràn khung.

```text
+-------------------------------------------------------------------------+
|  [Header Bar - cao 56px]  Tên Nhiệm Vụ       [Nhãn trạng thái tối giản] |
+---------------------------------------------+---------------------------+
|                                             |  CẤU HÌNH                 |
|                                             |  (Chọn kích thước / map,  |
|             VÙNG HIỂN THỊ CHÍNH             |   chọn thuật toán)        |
|             (rộng ~780px, ~67%)             |  -----------------------  |
|                                             |  ĐIỀU KHIỂN               |
|         Bàn cờ / Đấu trường / Lưới          |  [ Nút chính (Teal) ]     |
|       căn giữa với khoảng trắng rộng        |  [ Phụ ] [ Phụ ] [ Phụ ]  |
|           (margin tối thiểu 28px)           |  Tốc độ:  ---o---------   |
|                                             |  -----------------------  |
|                                             |  THÔNG SỐ & CHÚ GIẢI      |
|                                             |  Nhãn           Giá trị   |
|                                             |  Nhãn           Giá trị   |
+---------------------------------------------+---------------------------+
                                               Sidebar (rộng ~380px, ~33%)
```

### 4.2. Quy chuẩn linh kiện UI tối giản
- **Đường phân cách:** Chỉ dùng 1 đường kẻ `1px` màu `BORDER` (`#E5E7EB`) giữa Header / Vùng chính / Sidebar và giữa các nhóm trong Sidebar. Không lồng nhiều khung hộp chồng chéo.
- **Nút bấm (Button):**
  - Bo góc nhẹ `border_radius = 6`, chiều cao chuẩn `34–38px`.
  - *Nút chính (chỉ tối đa 1 nút nổi bật trên màn hình, ví dụ `Giải` / `Phát`):* nền `ACCENT_PRIMARY`, chữ `SURFACE` (`#FFFFFF`), không viền.
  - *Nút phụ (`Từng bước`, `Đặt lại`, `Đổi chế độ`, ...):* nền `SURFACE`, viền `1px` màu `BORDER`, chữ `TEXT_PRIMARY`; hover chuyển nền `SURFACE_SUBTLE`.
  - *Nút đang chọn (Toggle / Segmented Option):* nền `ACCENT_PRIMARY_SOFT`, viền `1px` màu `ACCENT_PRIMARY`, chữ `ACCENT_PRIMARY` đậm.
- **Thanh trượt tốc độ (Slider):** Thanh ray mảnh cao `4px` màu `BORDER`, phần đã kéo màu `ACCENT_PRIMARY`, núm tròn bán kính `7px` màu `SURFACE` viền `2px` màu `ACCENT_PRIMARY`.
- **Bảng thông số (Telemetry):** Dạng 2 cột không kẻ lưới ô — nhãn căn trái (`TEXT_SECONDARY`), giá trị căn phải (`TEXT_PRIMARY`, font `Mono`), mỗi dòng cao `24–26px`.

---

## 5. Ràng Buộc Kiến Trúc Kỹ Thuật (Bắt Buộc)

1. **Tách biệt tuyệt đối Logic và Giao diện (Model–View Decoupling):**
   - Toàn bộ file thuật toán lõi (`board.py`, `cnf_encoder.py`, `sat_solver.py`, `min_conflicts.py`, `game_engine.py`, `solver.py`, ...) **tuyệt đối không `import pygame`**.
   - Các thuật toán lặp cung cấp song song 2 chế độ:
     - `solve()`: chạy không giao diện ở tốc độ tối đa cho CLI và Notebook `.ipynb`.
     - `iter_solve()` / lưu vết từng bước: phục vụ PyGame trình diễn mượt `[Tự chạy]`, `[Từng bước]`, `[Tạm dừng]`, `[Đặt lại]` mà không treo sự kiện cửa sổ.
2. **Độc lập từng thư mục Task:**
   - Theo Mục III đề bài, mỗi nhiệm vụ nằm gọn trong thư mục con riêng (`source/task1/`, `source/task2/`, `source/task3/`).
   - Mỗi Task tự cài đặt file giao diện PyGame gọn nhẹ (~250–450 dòng, dễ đọc hiểu khi phỏng vấn vấn đáp), tuân thủ đúng các hằng số màu sắc, font và bố cục trong `UI.md` mà **không tạo thư mục `shared_ui/` phụ thuộc chéo**.
3. **Điểm khởi chạy thống nhất:**
   - Chạy trực tiếp `python source/taskX/main_taskX.py` -> mở giao diện PyGame tối giản.
   - Chạy kèm `--cli` -> thực thi thực nghiệm dòng lệnh (tiếng Việt không dấu).

---

## 6. Quy Ước Áp Dụng Cụ Thể Cho Từng Task

### 6.1. Nhiệm vụ 1 — Bài Toán N Quân Hậu (`source/task1/ui_nqueen.py`)
- **Bàn cờ (trái):** Lưới $N \times N$ xen kẽ `SURFACE` (`#FFFFFF`) và `SURFACE_SUBTLE` (`#F3F4F6`), viền ngoài `1px` `BORDER_STRONG`, nhãn chỉ số hàng/cột mảnh khi $N \le 20$.
- **Quân hậu (vector tối giản):** Biểu tượng vương miện vẽ bằng hình học sạch:
  - Khi bàn cờ đã là nghiệm hợp lệ (0 xung đột): màu `ACCENT_PRIMARY`.
  - Khi còn xung đột: hậu an toàn màu `TEXT_PRIMARY`, hậu đang xung đột màu `ACCENT_ALERT` trên nền `ACCENT_ALERT_SOFT`.
  - Khi $N \le 20$: vẽ đường nét đứt mảnh màu `ACCENT_ALERT` nối các cặp hậu đang tấn công nhau; đánh dấu cột vừa di chuyển bằng viền `2px` `TEXT_PRIMARY`.
- **Sidebar (phải):**
  - *Cấu hình:* Chọn nhanh kích thước `N` (`4, 8, 12, 16, 20, 32, 50` hoặc nút `-` / `+` từ `4` đến `100`), chọn thuật toán (`Glucose3 (SAT)`, `Min-Conflicts chuẩn`, `Max-Conflict thuần`, `Max-Conflict + Tabu thích nghi`).
  - *Điều khiển:* `Giải ngay` (nút chính), `Ngẫu nhiên`, `Từng bước`, `Phát / Tạm dừng`, `So sánh nhanh` (so chuẩn vs đề xuất trên cùng bàn cờ khởi tạo), thanh tốc độ.
  - *Thông số:* Kích thước $N$, tổng số mệnh đề CNF & phân rã (khi dùng `Glucose3`) hoặc số bước / số cặp xung đột / thời gian chạy (khi dùng `Min-Conflicts`).

### 6.2. Nhiệm vụ 2 — Trò Chơi Đấu Tăng (`source/task2/ui/pygame_arena.py`)
- **Đấu trường (trái):** Nền lưới sáng `SURFACE` với đường chia ô mảnh `BORDER`; xe tăng và căn cứ dùng hình học rõ nét (hoặc sprite sạch đặt trên nền thoáng) phân biệt trực tiếp bằng 2 tông: phe `MAX` dùng `ACCENT_PRIMARY`, phe `MIN` dùng `ACCENT_ALERT`; tường gạch dùng ô `SURFACE_SUBTLE` kèm vạch mức HP mảnh (`3 -> 2 -> 1`); đạn bay từng ô có vệt chấm mảnh theo hướng bay.
- **Sidebar (phải):**
  - *Cấu hình:* Chọn bản đồ, chọn bộ điều khiển `MAX` / `MIN` (đủ 4 cấu hình + bot nạp động từ `external_agents/` + chế độ Người chơi), nút `Nạp lại Bot`.
  - *Điều khiển:* `Tự chạy / Tạm dừng` (nút chính), `Từng bước`, `Đặt lại`, thanh tốc độ.
  - *Thông số:* Lượt hiện tại, thanh sinh lực mảnh (`HP Tank / HP Base`) của 2 phe, số trạng thái đã duyệt, độ sâu tìm kiếm và thời gian quyết định (`ms`).

### 6.3. Nhiệm vụ 3 — Câu Đố Kakuro CSP (`source/task3/visualizer_ui.py`)
- **Lưới Kakuro (trái):** Ô đen dùng `TEXT_PRIMARY` (`#111827`) hoặc xám đậm tối giản; ô gợi ý dùng `SURFACE_SUBTLE` chia đôi bằng 1 nét chéo mảnh `1px` (tổng ngang góc trên-phải, tổng dọc góc dưới-trái); ô trắng nền `SURFACE`:
  - Chưa gán: hiển thị lưới ứng viên `3x3` mảnh màu `TEXT_SECONDARY`.
  - Đang chọn (`MRV`): viền đậm `2px` `TEXT_PRIMARY` trên nền `SURFACE_SUBTLE`.
  - Lan truyền ràng buộc (`AC-3` / `Forward Checking`): gạch chéo màu `ACCENT_ALERT` lên chữ số bị loại.
  - Quay lui (`Backtrack`): nháy nền `ACCENT_ALERT_SOFT` và viền `ACCENT_ALERT`.
  - Đã gán hợp lệ: chữ số lớn sắc nét màu `ACCENT_PRIMARY`.
- **Sidebar (phải):**
  - *Cấu hình:* Đổi bảng mẫu (`5x5`, `6x6`, `8x8`, `9x9`), chọn chế độ giải (`Quay lui cơ bản`, `Kiểm tra tiến + MRV`, `AC-3 mở rộng + MRV/Bậc/LCV`), nút mở trình soạn thảo bảng (`Sửa bảng`).
  - *Điều khiển:* `Phát / Tạm dừng` (nút chính), `Bước trước`, `Bước tiếp`, `Bước cuối`, `Đặt lại`, thanh tốc độ.
  - *Thông số:* Tiến độ ô đã gán, số nút duyệt, số lần cắt tỉa, số lần quay lui và thời gian giải (`ms`).

---

## 7. Checklist Nghiệm Thu Giao Diện Cho Mỗi Task

Trước khi hoàn tất giao diện của từng Task, cần kiểm tra đạt đủ 7 tiêu chí:
- [ ] Cửa sổ đúng chuẩn `1160 x 720`, không tràn màn hình laptop macOS 13.7.8 và Windows.
- [ ] Chỉ sử dụng đúng 3 tông màu quy định trong Mục 2, khoảng trắng rộng và thoáng.
- [ ] 100% chữ trên giao diện là tiếng Việt có dấu rõ nét, không vỡ chữ, không tràn khung nút.
- [ ] Logic thuật toán tách rời hoàn toàn, không `import pygame` trong các module lõi.
- [ ] Có đầy đủ tương tác trực quan (`Chạy/Tạm dừng`, `Từng bước`, `Đặt lại`, chỉnh tốc độ).
- [ ] Hỗ trợ xuất ảnh chụp màn hình chế độ không cửa sổ (`--headless-screenshot`) phục vụ kiểm thử tự động và chèn vào báo cáo sau này.
- [ ] Mã nguồn giao diện ngắn gọn, cấu trúc OOP rõ ràng, dễ giải thích từng lớp khi phỏng vấn vấn đáp.
