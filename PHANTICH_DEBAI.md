# PHÂN TÍCH CHI TIẾT ĐỀ BÀI ĐỒ ÁN CUỐI KỲ AI (503043)

Tài liệu này phân tích sâu toàn bộ yêu cầu từ đề gốc [2627-HK1-AI-CK.pdf](file:///d:/3.1.%20AI/Final/2627-HK1-AI-CK.pdf) (bản dịch tiếng Việt xem tại [DEBAI.md](file:///d:/3.1.%20AI/Final/DEBAI.md)), chỉ rõ **bản chất thuật toán, các điểm bẫy dễ mất điểm, thiết kế thực nghiệm chuẩn xác, ràng buộc môi trường chấm bài và trọng tâm câu hỏi vấn đáp**.

---

## 1. Tổng Quan Cấu Trúc Điểm & Ràng Buộc Xuyên Suốt

### 1.1. Phân bổ thang điểm `10.0`

| Nhiệm vụ | Chủ đề AI cổ điển | Trọng số | Phân rã chi tiết |
| :--- | :--- | :---: | :--- |
| **Task 1** | Local Search & Propositional Logic (*N-Queen*) | **3.0đ** | 1.1 Mô hình Logic & CNF (`1.0đ`) · 1.2 `Glucose3` & thực nghiệm (`1.0đ`) · 1.3 `Min-Conflicts` + Heuristic đề xuất (`1.0đ`) |
| **Task 2** | Adversarial Search (*Tank Battle*) | **3.0đ** | 2.1 Mô hình Zero-Sum Game (`1.0đ`) · 2.2 Cài đặt & so sánh 4 cấu hình (`1.5đ`) · 2.3 PyGame GUI + nạp bot nhóm khác (`0.5đ`) |
| **Task 3** | Constraint Satisfaction Problems (*Kakuro*) | **3.0đ** | 3.1 Mô hình CSP & biện luận (`1.0đ`) · 3.2 Bộ giải & kiểm thử bảng `9×9` (`1.0đ`) · 3.3 UI trực quan hóa miền/lan truyền/quay lui (`1.0đ`) |
| **Task 4** | Report & Interview | **1.0đ** | Báo cáo IEEE 2 cột ≤ 5 trang + Video Demo + Vấn đáp bảo vệ |

### 1.2. Bốn ràng buộc kỹ thuật bắt buộc cho cả 3 Task
1. **Lập trình hướng đối tượng (OOP)**: Mọi Task đều ghi rõ *"must be designed and implemented following Object-Oriented Programming principles"*. Không viết code dạng hàm rời rạc thuần thủ tục; cần tách rõ các lớp: mô hình trạng thái (`Board`, `GameState`, `KakuroCSP`), bộ mã hóa/lan truyền (`CNFEncoder`, `ExtendedAC3Propagator`), bộ giải/tác tử (`Solver`, `BaseTankAgent`) và giao diện (`UI`).
2. **Tương thích môi trường chấm bài macOS 13.7.8 (Ventura) – Intel Core i5**:
   - Không dùng đường dẫn cứng kiểu Windows (`C:\...`, `D:\...`), bắt buộc dùng `pathlib.Path`.
   - Không dùng thư viện yêu cầu GPU CUDA hay chỉ chạy trên Windows.
   - Đảm bảo `from __future__ import annotations` để tránh lỗi cú pháp type hint trên Python 3.9–3.12 và dùng font chữ đa nền tảng cho PyGame/Tkinter.
3. **Giữ nguyên cell outputs trong `.ipynb`**: Mục III quy định bắt buộc giữ nguyên kết quả chạy (bảng số liệu + biểu đồ) của **tất cả các cell** trong file Jupyter Notebook.
4. **Học thuật & Vấn đáp**: Mỗi thành viên đều phải tự hiểu và giải thích được thuật toán + mã nguồn; không để sót dấu vết nháp hay ký tự lạ trong thư mục `source/`.

---

## 2. Phân Tích Chuyên Sâu Từng Nhiệm Vụ

### 2.1. Phân tích Task 1 (3.0 điểm) — N-Queen: Logic Mệnh Đề & Min-Conflicts

#### A. Bản chất yêu cầu 1.1 (Mô hình Logic mệnh đề & Chuyển đổi CNF – 1.0đ)
- **Tập biến**: Bàn cờ $N \times N$ có đúng $N^2$ ô, gán biến $P_{r,c}$ với $r, c \in \{0, \dots, N-1\}$. Để đưa vào `PySAT` (`Glucose3`), mỗi biến phải là số nguyên dương từ $1$ đến $N^2$:
  $$\text{id}(r, c) = r \cdot N + c + 1$$
- **Thuật toán phát hiện ràng buộc**:
  1. *Tồn tại (At-Least-One)*: Mỗi hàng $r$ có ít nhất 1 hậu ($\bigvee_{c=0}^{N-1} P_{r,c}$). Bổ sung thêm cho mỗi cột $c$ ($\bigvee_{r=0}^{N-1} P_{r,c}$) giúp bộ giải lan truyền đơn vị (Unit Propagation) mạnh hơn mà không làm thay đổi tập nghiệm.
  2. *Không tấn công (Pairwise At-Most-One)*: Duyệt mọi cặp ô phân biệt cùng hàng ($r_1 = r_2$), cùng cột ($c_1 = c_2$), cùng đường chéo chính ($r_1 - c_1 = r_2 - c_2$), hoặc cùng đường chéo phụ ($r_1 + c_1 = r_2 + c_2$). Mỗi cặp sinh ra phép kéo theo:
     $$P_{r_1,c_1} \Rightarrow \neg P_{r_2,c_2}$$
- **Quy trình chuyển đổi sang CNF (4 bước chuẩn Lecture 09)**:
  1. Khử tương đương $\alpha \Leftrightarrow \beta$ (không phát sinh ở đây).
  2. Khử kéo theo $\alpha \Rightarrow \beta \equiv \neg\alpha \vee \beta$: thu ngay mệnh đề nhị nguyên $(\neg P_{r_1,c_1} \vee \neg P_{r_2,c_2})$.
  3. Đẩy dấu phủ định vào sát biến nguyên tử (luật De Morgan & phủ định kép).
  4. Áp dụng luật phân phối $\vee$ qua $\wedge$ để thu được hội của các mệnh đề tuyển.
- **Công thức kiểm chứng tổng số mệnh đề CNF**:
  $$|C_{\text{CNF}}(N)| = 2N + N^2(N - 1) + \frac{N(N - 1)(2N - 1)}{3}$$
  *(Ví dụ: $N=4 \Rightarrow 84$ mệnh đề; $N=8 \Rightarrow 744$ mệnh đề; $N=50 \Rightarrow 203.450$ mệnh đề — tăng theo bậc ba $\mathcal{O}(N^3)$).*

#### B. Bản chất yêu cầu 1.2 (Thực nghiệm `Glucose3` – 1.0đ)
- Phải đo trên dải $N \ge 4$ tăng dần (ví dụ $N = 4, 8, 12, 16, 20, 25, 30, 35, 40, 50, 60$).
- Nên tách rõ 2 mốc thời gian: **thời gian sinh mệnh đề CNF (Python)** và **thời gian giải của `Glucose3` (C++ CDCL)** để giải thích hợp lý vì sao đồ thị thời gian tăng nhanh khi $N \ge 40$.

#### C. Bản chất yêu cầu 1.3 (Min-Conflicts & Đề xuất Heuristic chọn biến – 1.0đ)
- **Biểu diễn trạng thái**: Khác với SAT (dùng $N^2$ biến), Min-Conflicts chuẩn (Lecture 08) biểu diễn **trạng thái đầy đủ (Complete-state)** gồm 1 quân hậu trên mỗi cột `queens[c] = r`. Dùng 3 bảng đếm tần suất (hàng, chéo chính, chéo phụ) để tính số xung đột của bất kỳ vị trí nào trong thời gian $\mathcal{O}(1)$.
- **Điểm bẫy khi đề xuất Heuristic chọn biến**:
  - Min-Conflicts chuẩn chọn *ngẫu nhiên đều* một cột đang xung đột $\to$ tránh kẹt nhưng tốn nhiều bước dư thừa.
  - Nếu đề xuất ngây thơ *"luôn chọn cột nhiều xung đột nhất"* (*Pure Max-Conflict*) $\to$ sẽ **lặp vô hạn giữa 2 cột** trên vùng bình nguyên (plateau) và thất bại!
  - **Giải pháp tối ưu**: **Max-Conflict + Danh sách cấm ngắn hạn (Tabu List)** (cấm chọn lại cột vừa dời trong $k$ bước) + **Điều kiện ân xá (Aspiration)** (nếu cột bị cấm có thể triệt tiêu toàn bộ xung đột bàn cờ trong 1 bước thì cho phép chọn ngay) + **phá vỡ đình trệ** sau $16$ bước không cải thiện.
- **Nguyên tắc thực nghiệm công bằng**: Cả hai thuật toán bắt buộc phải chạy trên **cùng tập bàn cờ khởi tạo ngẫu nhiên** (cố định `seed`), cùng giới hạn `max_steps`, lặp nhiều lần (ví dụ 30 lần/mức $N$) rồi so sánh tỷ lệ thành công, số bước trung bình và thời gian chạy.

---

### 2.2. Phân tích Task 2 (3.0 điểm) — Tank Battle: Tìm Kiếm Đối Kháng

#### A. Mô hình hóa 6 thành phần Zero-Sum Game (Yêu cầu 2.1 – 1.0đ)
1. **Trạng thái khởi đầu $S_0$**: Kích thước lưới, tọa độ + hướng + HP của 2 xe tăng (`6 HP`), 2 căn cứ (`9 HP`), tường gạch (`3 HP`), tường thép (nếu có), danh sách đạn đang bay, lượt hiện tại `MAX`.
2. **Người chơi $\text{PLAYER}(s) \in \{\text{MAX}, \text{MIN}\}$**: Luân phiên 2 phe.
3. **Tập hành động $\text{ACTIONS}(s)$**: Gồm 6 hành động `{MOVE_UP, MOVE_DOWN, MOVE_LEFT, MOVE_RIGHT, FIRE, STAY}` (có thể lọc bỏ hành động dư thừa như bắn khi đã có đạn đang bay hoặc đâm vào tường khi đang quay sẵn hướng đó).
4. **Hàm chuyển trạng thái $\text{RESULT}(s, a)$**:
   - *Di chuyển & xoay hướng*: Vì đề bài không có lệnh xoay riêng, `MOVE_DIR` vừa cập nhật hướng quay mặt sang `DIR`, vừa tiến 1 ô nếu ô đích trống (cho phép xoay nòng bắn tường sát cạnh).
   - *Vật lý đạn bay 3 ô/chu kỳ*: Mỗi chu kỳ đạn di chuyển **tuần tự từng ô một**, tối đa 3 ô; sau mỗi bước 1 ô kiểm tra va chạm ngay với biên, đạn đối phương, tường thép, tường gạch (`-1 HP`), căn cứ (`-1 HP`) và xe tăng (`-1 HP`). Đạn trúng bất kỳ thực thể nào sẽ biến mất ngay lập tức; nếu đi hết 3 ô chưa chạm gì thì tồn tại tiếp sang lượt sau (*Persistent Bullet*).
5. **Trạng thái kết thúc $\text{TERMINAL-TEST}(s)$**: Khi `HP <= 0` đối với bất kỳ Xe tăng hoặc Căn cứ nào (hoặc chạm ngưỡng lượt hòa tối đa).
6. **Hàm tiện ích $\text{UTILITY}(s, p)$**: Tổng bằng 0: `+1000` nếu $p$ thắng, `-1000` nếu $p$ thua, `0` nếu hòa.

#### B. "Bẫy toán học" ở Yêu cầu 2.2 (So sánh 4 cấu hình – 1.5đ)
- **Vấn đề cốt lõi**: Xe tăng có `6 HP`, căn cứ có `9 HP`, sát thương `1/phát`. Để đi từ đầu ván đầy máu tới lúc có bên nổ tung cần ít nhất `12–20` nửa lượt (`ply`), không gian cây trò chơi lên tới $6^{15} \approx 4,7 \times 10^{11}$ trạng thái. Do đó, **Minimax thuần** và **Alpha-Beta thuần** (không có hàm lượng giá cắt độ sâu) **không thể chạy xong** trên ván đầy máu từ đầu!
- **Thiết kế thực nghiệm 2 tầng để đảm bảo công bằng tuyệt đối**:
  - *Tầng 1 (Endgame Micro-Scenarios – lưới $7\times 7$, còn 1–2 HP, giới hạn 6 ply)*: Cả 4 cấu hình (`Minimax`, `Alpha-Beta`, `Heuristic Minimax`, `Heuristic Alpha-Beta`) đều chạy hoàn chỉnh trên **đúng cùng một thế cờ**, chứng minh Alpha-Beta cho cùng nước đi tối ưu như Minimax nhưng giảm hàng chục lần số nút, còn Heuristic Alpha-Beta giảm tới gần `900` lần!
  - *Tầng 2 (Full Arenas – lưới $9\times 9$ và $11\times 11$ đầy đủ máu 6/9/3 HP)*: So sánh hiệu năng thời gian thực giữa `Heuristic Minimax` và `Heuristic Alpha-Beta` (+ `Move Ordering` + `Transposition Table`) ở các độ sâu $d = 2, 3, 4$.

#### C. Phân tích Yêu cầu 2.3 (PyGame GUI & Nạp thuật toán nhóm khác – 0.5đ)
- Điểm ăn tiền của yêu cầu này là **cơ chế plugin động (`importlib`)** + **cách ly trạng thái (State Isolation)**:
  - Sử dụng trạng thái bất biến (`frozen=True` / `MappingProxyType`) hoặc truyền bản sao sâu (`clone()`) để bot của nhóm khác không thể gian lận hay vô tình làm hỏng trạng thái trận đấu gốc.
  - Hỗ trợ cả 2 chuẩn giao tiếp (kế thừa `BaseTankAgent` hoặc hàm thuần `get_action(obs_dict)`) giúp nhóm khác cắm thuật toán vào đấu chỉ trong vài dòng code.

---

### 2.3. Phân tích Task 3 (3.0 điểm) — Kakuro: Bài Toán Thỏa Mãn Ràng Buộc (CSP)

#### A. Kiểm chứng chính xác 2 bảng câu đố trong đề gốc
Bằng kiểm tra bất biến toán học (*Tổng mọi gợi ý hàng ngang phải bằng tổng mọi gợi ý cột dọc*):
- **Bảng mẫu $5 \times 5$ (trang 4 đề gốc)**:
  - Tổng ngang: $12 + 21 + 11 + 16 = 60$.
  - Tổng dọc: $14 + 21 + 14 + 11 = 60$.
  - Số biến ô trắng chính xác: **12 biến** (`8` dãy ràng buộc: 4 ngang, 4 dọc).
- **Bảng kiểm thử phức tạp $9 \times 9$ (trang 5 đề gốc)**:
  - Tổng ngang: $(22+3) + 28 + (14+20) + (17+22) + (28+12) + (14+6) + 39 + (16+8) = 249$.
  - Tổng dọc: $(17+12) + 44 + (16+29) + (9+12) + (11+7) + (15+12) + 44 + (14+7) = 249$.
  - Số biến ô trắng chính xác: **48 biến** (`28` dãy ràng buộc: 14 ngang, 14 dọc).

#### B. Mô hình CSP $\langle X, D, C \rangle$ & Chiến lược giải (Yêu cầu 3.1 & 3.2 – 2.0đ)
- **Tập biến $X$**: Toàn bộ các ô trắng $(r, c)$.
- **Miền giá trị $D$**: Khởi tạo $\{1..9\}$, sau đó thu hẹp ngay từ bước tiền xử lý bằng **tổ hợp tổng (Sum Partitions)** — ví dụ dãy 2 ô có tổng $3$ chỉ nhận $\{1, 2\}$, dãy 2 ô tổng $17$ chỉ nhận $\{8, 9\}$; giao miền ngang và miền dọc của từng ô giúp loại bỏ ngay phần lớn giá trị vô lý.
- **Tập ràng buộc $C$**: Mỗi dãy (run) mang đồng thời 2 ràng buộc bậc cao:
  1. $\text{AllDifferent}$: các chữ số trong cùng một dãy phải đôi một khác nhau.
  2. $\text{Exact Sum}$: tổng các chữ số trong dãy bằng đúng con số gợi ý.
- **Lan truyền ràng buộc & Heuristics Lecture 08**:
  - *Forward Checking*: Sau khi gán $X_i = v$, loại $v$ và các chữ số không nằm trong tập phân hoạch tổng phần dư của các ô chưa gán cùng dãy.
  - *Extended AC-3 (hướng GAC)*: Duy trì hàng đợi các dãy bị ảnh hưởng; loại bỏ mọi giá trị $v \in D_i$ nếu không tồn tại tổ hợp giá trị khác nhau nào từ miền hiện tại của các ô còn lại trong dãy cộng lại bằng tổng mục tiêu (có kiểm tra nhanh cận tổng min/max chặt).
  - *MRV (Minimum Remaining Values)*: Chọn ô còn ít ứng viên nhất để phát hiện ngõ cụt sớm nhất (*fail-first*).
  - *Degree Heuristic*: Khi nhiều ô cùng có miền nhỏ nhất bằng nhau, ưu tiên ô liên kết với nhiều ô chưa gán nhất.
  - *LCV (Least Constraining Value)*: Thử trước giá trị làm mất ít lựa chọn nhất của các ô hàng xóm (ước lượng 1 bước bằng Forward Checking để giữ chi phí thấp).

#### C. Yêu cầu trực quan hóa UI (Yêu cầu 3.3 – 1.0đ)
- Đề bài chấm riêng `1.0 điểm` cho UI — tức là UI **không chỉ hiện đáp án cuối cùng** mà bắt buộc phải cho người chấm nhìn thấy rõ **3 tiến trình sống**:
  1. Miền giá trị hiện tại của từng ô (lưới ứng viên $3 \times 3$ các chữ số `1..9`).
  2. Quá trình lan truyền ràng buộc (highlight chữ số vừa bị gạch/loại khỏi miền).
  3. Quá trình tìm kiếm quay lui (ô đang được MRV chọn, giá trị thử gán, ngõ cụt miền rỗng và bước hoàn tác quay lui).

---

### 2.4. Phân tích Task 4 (1.0 điểm) & Chuẩn Bị Phỏng Vấn Vấn Đáp

#### A. Checklist Báo cáo IEEE & Gói nộp bài (Tránh bị trừ 50% điểm)
- [ ] Báo cáo biên dịch từ mẫu hội nghị **IEEE 2 cột**, tối đa **05 trang** (`report.pdf`).
- [ ] Danh sách tác giả có đủ 4 thành viên và **giảng viên hướng dẫn đứng ở vị trí tác giả cuối cùng**.
- [ ] Đủ các mục bắt buộc: `Title`, `Authors`, `Abstract`, 3 phần cho 3 Task kèm hình/bảng, `Contributions (0%–100%)`, `Self-evaluation`, `Conclusion`, `References` chuẩn IEEE.
- [ ] Cấu trúc nén cá nhân đúng tên `AI_final_<Project Group ID>_<Student ID>.zip` gồm: `source/` (có `task1/`, `task2/`, `task3/`, `README.md`, `requirement.txt`, 3 file `.ipynb` còn nguyên cell outputs), `report.pdf`, `demo.txt`.
- [ ] Mọi thành viên trong nhóm đều tự nộp bài cá nhân trước thời hạn.

#### B. Trọng tâm câu hỏi phỏng vấn vấn đáp (Cả 4 thành viên cần nắm chắc)
1. **Task 1**:
   - Tại sao bài toán N-Queen cần $N^2$ biến trong SAT nhưng chỉ cần mảng độ dài $N$ trong Min-Conflicts?
   - Giải thích cách chuyển $P(r_1, c_1) \Rightarrow \neg P(r_2, c_2)$ thành mệnh đề CNF và cách chứng minh công thức tổng số mệnh đề $\mathcal{O}(N^3)$.
   - Tại sao chọn cột nhiều xung đột nhất đơn thuần lại hay bị kẹt, và cơ chế Tabu + Aspiration khắc phục điều đó như thế nào?
2. **Task 2**:
   - Hàm `RESULT(s, a)` xử lý đạn bay 3 ô từng bước như thế nào nếu ô thứ 2 có tường gạch?
   - Tại sao phải dùng kịch bản Endgame ít máu để so sánh Minimax thuần với Alpha-Beta thuần? Ý nghĩa của từng trọng số trong hàm `EVAL(s)`?
   - Cơ chế nạp động bot của nhóm khác hoạt động ra sao và làm sao ngăn bot ngoài sửa trái phép `GameState`?
3. **Task 3**:
   - Một ô trắng trong Kakuro chịu tác động của những ràng buộc nào? Khác biệt giữa `Forward Checking` và `Extended AC-3` là gì?
   - Giải thích phối hợp giữa `MRV`, `Degree` và `LCV`: tại sao chọn biến dùng chiến lược *fail-first* (khó nhất trước) nhưng chọn giá trị lại dùng *fail-last* (ít ràng buộc nhất trước)?
   - Tại sao trên bảng `9×9` (48 biến), chế độ `AC-3 mở rộng + Heuristic` giải xong với **0 lần quay lui** trong khi quay lui cơ bản tốn gần 1.000 lần quay lui?

---

## 3. Thông Tin Nhóm & Phân Công Công Việc (4 Thành Viên)

- **Giảng viên hướng dẫn:** Tiến sĩ Trịnh Hùng Cường (`trinhhungcuong@tdtu.edu.vn`) *(đứng ở vị trí tác giả cuối cùng trong báo cáo khoa học IEEE theo quy định Task 4)*.
- **Nguyên tắc phối hợp:** 3 thành viên phụ trách trọn vẹn 3 bài toán độc lập trên các nhánh Git riêng biệt; Nhóm trưởng xây dựng khung kiến trúc OOP chung, rà soát/hợp nhất mã nguồn (`merge`), đồng bộ ngôn ngữ & kiểm thử tích hợp đa nền tảng, biên tập báo cáo IEEE và điều phối video demo. Mọi thành viên đều phải đọc hiểu toàn bộ 3 Task để sẵn sàng phỏng vấn vấn đáp.

### 3.1. Bảng phân công chi tiết từng thành viên

| STT | Họ và tên | MSSV | Email sinh viên | Vai trò & Phụ trách chính | Nhiệm vụ chi tiết & Sản phẩm bàn giao | Mức độ hoàn thành |
| :-: | :--- | :---: | :--- | :--- | :--- | :---: |
| 1 | **Nguyễn Văn Duy** | `52400010` | `52400010@student.tdtu.edu.vn` | **Nhóm trưởng** *(Kiến trúc, Tích hợp, Kiểm thử & Task 4)* | Thiết kế cấu trúc dự án chuẩn OOP; quản lý kho lưu trữ GitHub, review & hợp nhất (merge) code 3 nhánh; rà soát lỗi tích hợp, chuẩn hóa tương thích macOS 13.7.8 & Việt hóa đồng bộ toàn bộ sản phẩm; biên tập báo cáo khoa học IEEE (`report/main.tex`, `report.pdf`), `README.md`, `requirement.txt`, `DEBAI.md`, `PHANTICH_DEBAI.md` và tổng hợp video demo (`demo.txt`). | 100% |
| 2 | **Lê Văn Quý** | `52400153` | `52400153@student.tdtu.edu.vn` | **Thành viên — Phụ trách Task 1** *(N-Queen: Logic Mệnh Đề & Local Search)* | Mô hình hóa Logic mệnh đề và chuyển đổi CNF; cài đặt trọn bộ `source/task1/` (`board.py`, `cnf_encoder.py`, `sat_solver.py`, `min_conflicts.py`, `main_task1.py`); phát triển giao diện bàn cờ `gui.py`; chạy thực nghiệm `Glucose3` ($N \ge 4$) và đối sánh `Min-Conflicts` chuẩn với Heuristic `Max-Conflict + Tabu` trong `experiments_task1.ipynb` kèm biểu đồ & nội dung báo cáo Task 1. | 100% |
| 3 | **Huỳnh Thiên Đức** | `5240110` | `5240110@student.tdtu.edu.vn` | **Thành viên — Phụ trách Task 2** *(Tank Battle: Tìm Kiếm Đối Kháng & PyGame)* | Mô hình hóa trò chơi Tổng bằng không (Zero-Sum Game); thiết kế engine trạng thái bất biến (`entities.py`, `game_state.py`, `game_engine.py`, `maps.py`) với vật lý đạn bay 3 ô/chu kỳ từng ô một; cài đặt 4 cấu hình thuật toán (`Minimax`, `Alpha-Beta`, `Heuristic Minimax`, `Heuristic Alpha-Beta`), hàm lượng giá `EVAL(s)`, giao diện PyGame Arena (`pygame_arena.py`, bộ sprite Kenney CC0), cơ chế nạp động bot nhóm ngoài (`external_agents/`) và thực nghiệm 2 tầng trong `benchmark_task2.ipynb`. | 100% |
| 4 | **Lê Tiến Đạt** | `52400105` | `52400105@student.tdtu.edu.vn` | **Thành viên — Phụ trách Task 3** *(Kakuro: Bài Toán Thỏa Mãn Ràng Buộc CSP)* | Mô hình hóa Kakuro CSP $\langle X, D, C \rangle$ và số hóa 4 bản đồ JSON (`5×5`, `6×6`, `8×8`, `9×9`); cài đặt tiền xử lý `Sum Partitions`, `Forward Checking`, `Extended AC-3` và bộ giải kết hợp `MRV/Degree/LCV` (`csp_model.py`, `propagation.py`, `solver.py`); phát triển giao diện trực quan hóa PyGame đa luồng (`visualizer_ui.py`) kèm trình soạn thảo bảng (`board_editor.py`); thực nghiệm thống kê 30 lần chạy và kiểm thử tự động trong `experiments_task3.ipynb`. | 100% |

### 3.2. Quy chuẩn đặt tên gói nộp bài cá nhân cho 4 thành viên
Mỗi thành viên tự nén bản hoàn chỉnh cuối cùng và nộp cá nhân lên hệ thống theo đúng cú pháp `AI_final_<Project Group ID>_<Student ID>.zip`:
- Nguyễn Văn Duy: `AI_final_<MaNhom>_52400010.zip`
- Lê Văn Quý: `AI_final_<MaNhom>_52400153.zip`
- Huỳnh Thiên Đức: `AI_final_<MaNhom>_5240110.zip`
- Lê Tiến Đạt: `AI_final_<MaNhom>_52400105.zip`
