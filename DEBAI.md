# ĐỀ BÀI ĐỒ ÁN CUỐI KỲ — NHẬP MÔN TRÍ TUỆ NHÂN TẠO (503043)

> Bản dịch đầy đủ và chính xác từ đề gốc [2627-HK1-AI-CK.pdf](file:///d:/3.1.%20AI/Final/2627-HK1-AI-CK.pdf) (7 trang).

- **Trường:** Đại học Tôn Đức Thắng (Ton Duc Thang University)
- **Khoa:** Khoa Công nghệ Thông tin (Faculty of Information Technology)
- **Học phần:** 503043 – Nhập môn Trí tuệ Nhân tạo (Introduction to Artificial Intelligence)
- **Giảng viên phụ trách:** `nguyenthanhan@tdtu.edu.vn`
- **Thời lượng thực hiện:** 06 tuần

---

## I. Hình thức tổ chức (Formation)

1. Đồ án được thực hiện theo nhóm sinh viên.
2. Các nhóm sinh viên thực hiện đầy đủ các nhiệm vụ yêu cầu và nộp bài theo hướng dẫn bên dưới.

---

## II. Các nhiệm vụ (Tasks)

### a) Nhiệm vụ 1 (3.0 điểm): Tìm kiếm cục bộ & Logic mệnh đề (Local Search & Propositional Logic)

#### Mô tả bài toán: Bài toán N Quân Hậu (N-Queen problem)
- Cho một bàn cờ vua kích thước $N \times N$, sinh viên cài đặt một bộ giải để tìm cấu hình đặt $N$ quân hậu lên bàn cờ sao cho không có cặp quân hậu nào tấn công lẫn nhau.
- Gán cho mỗi ô trên bàn cờ một biến logic mệnh đề, trong đó nếu biến mang giá trị `True` thì ô đó chứa một quân hậu, còn nếu biến mang giá trị `False` thì ô đó trống.

#### Các yêu cầu (Requirements):
1. **(1.0 điểm):** Mô hình hóa bài toán đã cho dưới dạng bài toán Logic mệnh đề (Propositional Logic) và trình bày các thành phần liên quan. Thảo luận về một thuật toán tìm ra các ràng buộc chi phối việc đặt các quân hậu trên bàn cờ, đồng thời giải thích quy trình chuyển đổi các ràng buộc này thành các mệnh đề ở Dạng chuẩn hội (Conjunctive Normal Form – CNF).
2. **(1.0 điểm):** Sử dụng bộ giải [Glucose3](https://pysathq.github.io/) từ thư viện `PySAT` để tìm lời giải cho bài toán và tiến hành thực nghiệm với các giá trị $N$ tăng dần, trong đó $N \ge 4$. Với mỗi giá trị $N$, báo cáo tổng số mệnh đề CNF và thời gian chạy mà bộ giải cần.
3. **(1.0 điểm):** Giải bài toán bằng thuật toán **Min-Conflicts** đã được giới thiệu trong Bài giảng 08 (Lecture 08) và đề xuất một hàm heuristic để chọn biến. Tiến hành thực nghiệm để đánh giá hiệu quả của heuristic đề xuất bằng cách so sánh hiệu năng của nó với phương pháp Min-Conflicts tiêu chuẩn.

#### Lưu ý (Notice):
- Trình soạn thảo khuyến nghị: Visual Studio Code.
- Dự án bắt buộc phải được thiết kế và cài đặt tuân theo các nguyên lý Lập trình hướng đối tượng (Object-Oriented Programming – OOP).
- Cấu hình môi trường chấm bài: **macOS 13.7.8 (Ventura)** với vi xử lý **Intel Core i5**.

---

### b) Nhiệm vụ 2 (3.0 điểm): Tìm kiếm đối kháng (Adversarial Search)

#### Mô tả bài toán: Trò chơi Đấu Tăng (Tank Battle Game)
- Trò chơi được thiết kế theo dạng theo lượt (turn-based). Trong mỗi chu kỳ trò chơi (game cycle), các người chơi thực hiện hành động và trạng thái trò chơi được cập nhật tương ứng.
- Mỗi xe tăng có thể di chuyển 1 ô mỗi lượt (`LÊN`, `XUỐNG`, `TRÁI`, `PHẢI`). Khi xe tăng bắn một viên đạn, viên đạn bay với tốc độ **3 ô mỗi chu kỳ trò chơi** theo hướng mà xe tăng đang quay mặt.
- Chuyển động của viên đạn được xử lý **từng ô một (cell by cell)**. Trong mỗi chu kỳ trò chơi, viên đạn di chuyển tối đa 3 ô và một phép kiểm tra va chạm được thực hiện ngay sau mỗi bước di chuyển 1 ô. Nếu viên đạn gặp tường (wall), xe tăng (tank) hoặc căn cứ (base), sự kiện va chạm tương ứng được kích hoạt ngay lập tức. Viên đạn dừng lại ngay sau khi trúng một thực thể.
- Mỗi thực thể trong trò chơi có lượng sinh lực (HP) định sẵn như trong bảng sau:

| Thực thể (Entity) | Sinh lực ban đầu (Initial HP) | Sát thương mỗi phát trúng (Damage per Hit) |
| :--- | :---: | :---: |
| Xe tăng (`Tank`) | 6 | 1 |
| Căn cứ (`Base`) | 9 | 1 |
| Tường (`Wall`) | 3 | 1 |

- Một thực thể xe tăng có **06 hành động**, bao gồm: `MOVE_UP`, `MOVE_DOWN`, `MOVE_LEFT`, `MOVE_RIGHT`, `FIRE`, `STAY`.
- Trò chơi kết thúc khi một căn cứ hoặc một xe tăng bị phá hủy. Người chơi có xe tăng và/hoặc căn cứ còn hoạt động được tuyên bố là người chiến thắng.
- Sinh viên được yêu cầu áp dụng các thuật toán tìm kiếm đối kháng đã giới thiệu trong Bài giảng 07 (Lecture 07), chẳng hạn như **Minimax Search**, **Alpha-Beta Pruning** và **Heuristic Minimax Search**, để điều khiển xe tăng.
- Hình minh họa tham khảo trong đề: *Tank Battalion / Battle City* (`https://www.hardcoregaming101.net/tank-battalion-battle-city/`).

#### Các yêu cầu (Requirements):
1. **(1.0 điểm):** Mô hình hóa bài toán đã cho dưới dạng Trò chơi Tổng bằng không (Zero-Sum Game) và trình bày các thành phần liên quan, bao gồm: trạng thái trò chơi (game state), người chơi (players), tập hành động (actions), hàm chuyển trạng thái (transition function), các trạng thái kết thúc (terminal states) và hàm tiện ích (utility function). Thảo luận cách áp dụng các thuật toán tìm kiếm đối kháng như Minimax Search, Alpha-Beta Pruning và Heuristic Minimax Search để điều khiển xe tăng.
2. **(1.5 điểm):** Cài đặt thuật toán điều khiển xe tăng trong trò chơi. Sinh viên có thể áp dụng nhiều kỹ thuật tối ưu khác nhau để đảm bảo xe tăng hoạt động hiệu quả và trò chơi chạy ở thời gian thực (real time). Thiết lập thực nghiệm để so sánh thời gian tính toán và hiệu năng tìm kiếm của **bốn cấu hình** sau:
   - Minimax Search
   - Alpha-Beta Search
   - Heuristic Minimax Search
   - Heuristic Minimax Search with Alpha-Beta Pruning
   
   Các thực nghiệm phải sử dụng cùng kịch bản trò chơi và cùng điều kiện tìm kiếm (khi có thể áp dụng) để đảm bảo so sánh công bằng. Các chỉ số đánh giá liên quan có thể bao gồm: thời gian thực thi, số trạng thái trò chơi đã duyệt, độ sâu tìm kiếm và các thước đo hiệu năng phù hợp khác.
3. **(0.5 điểm):** Xây dựng giao diện đồ họa người dùng (GUI) bằng thư viện **PyGame** để vận hành trò chơi. Hệ thống phải cung cấp một cơ chế cho phép **nhập (import) và tích hợp các thuật toán do các nhóm sinh viên khác phát triển**, giúp các bản cài đặt thuật toán khác nhau có thể thi đấu trực tiếp với nhau trên cùng một môi trường trò chơi.

#### Lưu ý (Notice):
- Trình soạn thảo khuyến nghị: Visual Studio Code.
- Dự án bắt buộc phải được thiết kế và cài đặt tuân theo các nguyên lý Lập trình hướng đối tượng (OOP).
- Cấu hình môi trường chấm bài: **macOS 13.7.8 (Ventura)** với vi xử lý **Intel Core i5**.

---

### c) Nhiệm vụ 3 (3.0 điểm): Bài toán Thỏa mãn Ràng buộc (Constraint Satisfaction Problems – CSP)

#### Mô tả bài toán: Trò chơi Kakuro
- Sinh viên cần tìm hiểu luật chơi và cách giải câu đố Kakuro thông qua bài viết về Kakuro trên Wikipedia (`https://en.wikipedia.org/wiki/Kakuro`).
- Cho bảng trò chơi Kakuro ví dụ dưới đây (trang 4 đề gốc — lưới $5 \times 5$, ký hiệu `D\A` là tổng cột dọc ở dưới-trái / tổng hàng ngang ở trên-phải, `■` là ô đen, `□` là ô trắng cần điền số $1..9$):

| | Cột 1 | Cột 2 | Cột 3 | Cột 4 | Cột 5 |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **Hàng 1** | ■ | ■ | `21\` | `14\` | ■ |
| **Hàng 2** | ■ | `14\12` | □ | □ | `11\` |
| **Hàng 3** | `\21` | □ | □ | □ | □ |
| **Hàng 4** | `\11` | □ | □ | □ | □ |
| **Hàng 5** | ■ | `\16` | □ | □ | ■ |

- Sinh viên cần mô hình hóa trò chơi dưới dạng một Bài toán Thỏa mãn Ràng buộc (CSP) bằng cách xác định tập biến, các miền giá trị tương ứng và các ràng buộc chi phối câu đố.
- Sau đó, sinh viên phát triển một bộ giải kết hợp các kỹ thuật **lan truyền ràng buộc (constraint propagation)** với **Tìm kiếm quay lui (Backtracking Search)** để tìm một lời giải hợp lệ. Bản cài đặt cần tích hợp các kỹ thuật heuristic phù hợp đã được giới thiệu trong Bài giảng 08 (Lecture 08) nhằm cải thiện hiệu quả của quá trình tìm kiếm.

#### Các yêu cầu (Requirements):
1. **(1.0 điểm):** Mô hình hóa chính xác bài toán dưới dạng Bài toán Thỏa mãn Ràng buộc (CSP), xác định và giải thích rõ các thành phần liên quan gồm: biến (variables), miền giá trị (domains) và ràng buộc (constraints). Mô tả và biện luận các thuật toán cũng như kỹ thuật được áp dụng trong dự án.
2. **(1.0 điểm):** Cài đặt bộ giải có khả năng tìm ra lời giải hợp lệ cho bài toán. Chứng minh và đánh giá **tính đúng đắn (correctness)**, **độ ổn định (stability)** và **tính hiệu quả (effectiveness)** của bộ giải bằng cách áp dụng lên bộ kiểm thử phức tạp hơn được cung cấp bên dưới (trang 5 đề gốc — lưới $9 \times 9$):

| | C1 | C2 | C3 | C4 | C5 | C6 | C7 | C8 | C9 |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **H1** | ■ | ■ | `44\` | `16\` | `9\` | ■ | `15\` | `44\` | ■ |
| **H2** | ■ | `\22` | □ | □ | □ | `11\3` | □ | □ | `14\` |
| **H3** | ■ | `17\28` | □ | □ | □ | □ | □ | □ | □ |
| **H4** | `\14` | □ | □ | ■ | `12\20` | □ | □ | □ | □ |
| **H5** | `\17` | □ | □ | `29\22` | □ | □ | □ | □ | `7\` |
| **H6** | ■ | `12\28` | □ | □ | □ | □ | `\12` | □ | □ |
| **H7** | `\14` | □ | □ | □ | □ | `7\` | `12\6` | □ | □ |
| **H8** | `\39` | □ | □ | □ | □ | □ | □ | □ | ■ |
| **H9** | ■ | `\16` | □ | □ | `\8` | □ | □ | □ | ■ |

3. **(1.0 điểm):** Xây dựng giao diện người dùng (UI) cho trò chơi có khả năng **trực quan hóa rõ ràng**:
   - Miền giá trị của các biến (domains of variables),
   - Quá trình lan truyền ràng buộc (constraint propagation process), và
   - Quá trình tìm kiếm quay lui (Backtracking Search process).

#### Lưu ý (Notice):
- Trình soạn thảo khuyến nghị: Visual Studio Code.
- Dự án bắt buộc phải được thiết kế và cài đặt tuân theo các nguyên lý Lập trình hướng đối tượng (OOP).
- Cấu hình môi trường chấm bài: **macOS 13.7.8 (Ventura)** với vi xử lý **Intel Core i5**.

---

### d) Nhiệm vụ 4 (1.0 điểm): Báo cáo và Phỏng vấn vấn đáp (Report and Interview)

- Các nhóm sinh viên soạn thảo báo cáo đồ án bằng **mẫu bài báo hội nghị IEEE** (IEEE conference proceeding template).
- Trình soạn thảo khuyến nghị: **Overleaf**.
- Các nội dung chọn lọc bắt buộc trong báo cáo:
  - **Title:** Tên đề tài đồ án.
  - **Authors:** Thông tin các thành viên nhóm, **giảng viên được thêm vào ở vị trí tác giả cuối cùng**.
  - **Abstract:** Tóm tắt các yêu cầu đồ án, phương pháp tiếp cận, kết quả thực nghiệm và mức độ hoàn thành.
  - **Các mục tiếp theo:** Mỗi mục trình bày một nhiệm vụ trong đồ án với tiêu đề rõ ràng, dễ đọc. Trình bày ngắn gọn cách tiếp cận giải quyết vấn đề và minh họa kết quả bằng các hình vẽ/bảng biểu liên quan.
  - **Mục "Contributions" (Đóng góp cá nhân):** Nhiệm vụ từng cá nhân, mức độ hoàn thành từng cá nhân (`0%–100%`).
  - **Mục "Self-evaluation" (Tự đánh giá):** Tự đánh giá mức độ hoàn thành các nhiệm vụ và ước lượng điểm số.
  - **Mục "Conclusion" (Kết luận):** Tóm tắt lại yêu cầu đồ án, phương pháp tiếp cận, kết quả thực nghiệm và mức độ hoàn thành.
- Tài liệu tham khảo (References) phải theo chuẩn **IEEE**.
- Độ dài tối đa là **05 trang** theo bố cục **2 cột**.
- Sinh viên **bắt buộc phải tham gia phỏng vấn vấn đáp** để bảo vệ phần việc của mình trong đồ án. Nếu không thể giải thích rõ ràng và chính xác ý tưởng cũng như phần cài đặt, sinh viên sẽ nhận **0.0 điểm** cho các nhiệm vụ liên quan.

---

## III. Quy định nộp bài (Submission)

- Tạo một thư mục đặt tên theo đúng định dạng:
  ```text
  AI_final_<Project Group ID>_<Student ID>
  ```
  Trong đó bao gồm:
  - `source`: thư mục chứa các file mã nguồn, mỗi nhiệm vụ đặt trong một thư mục con riêng.
    - Bắt buộc có file `README.md` *(đề gốc gõ nhầm là `REAME.md`)* và `requirement.txt` để hướng dẫn cài đặt dự án.
  - `report.pdf`: file báo cáo đồ án.
  - `demo.txt`: đường dẫn URL tới video demo.
- Sinh viên **phải giữ nguyên toàn bộ kết quả đầu ra (outputs) của tất cả các cell** trong các file `.ipynb`.
- Nén thư mục thành một file `.zip` và nộp trước thời hạn.
- **Mọi thành viên trong nhóm đều phải tự nộp đồ án cá nhân lên hệ thống.**

---

## IV. Quy chế (Policy)

- Nhóm sinh viên nộp bài trễ sẽ nhận **0.0 điểm** cho tất cả thành viên trong nhóm.
- Thiếu bất kỳ thành phần bắt buộc nào trong gói nộp bài sẽ bị **trừ tối thiểu 50% điểm trình bày/báo cáo**.
- Sao chép mã nguồn từ Internet hoặc từ sinh viên khác, chia sẻ bài làm với nhóm khác hoặc thực hiện các hành vi gian lận học thuật tương tự sẽ nhận **0.0 điểm cho tất cả các nhóm liên quan**.
- Nếu có bất kỳ dấu hiệu sao chép hoặc chia sẻ bài làm trái phép nào, các buổi phỏng vấn bổ sung có thể được tổ chức để xác minh tính xác thực bài làm của sinh viên.
- **Nghiêm cấm sử dụng công cụ AI trong đồ án này.** Nếu phát hiện bất kỳ ký tự đặc trưng do AI sinh ra hoặc nội dung nào khác có thể nhận diện là do AI tạo ra trong các file mã nguồn, nhóm sẽ nhận **0.0 điểm** cho nhiệm vụ tương ứng.

*(HẾT ĐỀ BÀI)*
