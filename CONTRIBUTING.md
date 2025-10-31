# Hướng dẫn Đóng góp (cho người mới)

Cảm ơn bạn đã quan tâm đến việc đóng góp cho repo! Đây là hướng dẫn chi tiết từng bước, được thiết kế cho cả những người lần đầu sử dụng Git. Đừng lo lắng nếu bạn là người mới!

## Quy trình Chung (Tóm tắt)

Luồng làm việc chuẩn sẽ như sau:
1.  **Issue:** Tạo một "Issue" (vấn đề) để đề xuất paper bạn muốn làm.
2.  **Branch:** Tạo một "nhánh" (branch) mới cho riêng mình.
3.  **Code:** Viết code, tạo notebook trong thư mục paper của bạn.
4.  **Pull Request (PR):** Gửi "Yêu cầu Kéo" (Pull Request) để nhóm review.
5.  **Review & Merge:** Nhóm góp ý, bạn sửa code (nếu cần), và code được gộp vào dự án chung.

---

## Hướng dẫn Chi tiết Từng Bước

### Bước 0: Cài đặt (Chỉ làm 1 lần)

1.  **Cài đặt Git:** Tải và cài đặt Git từ [git-scm.com](https://git-scm.com/).
2.  **Cấu hình Git:** Mở terminal (Command Prompt/PowerShell trên Windows, Terminal trên Mac/Linux) và gõ 2 lệnh sau (thay bằng tên và email GitHub của bạn):
    ```bash
    git config --global user.name "Ten Cua Ban"
    git config --global user.email "emailcuaban@example.com"
    ```

### Bước 1: Lấy code từ repo về máy (Clone)

Bạn chỉ làm việc này 1 lần duy nhất cho repo này.

1.  Vào trang chính của repo trên GitHub.
2.  Nhấn nút "Code" (màu xanh lá).
3.  Copy đường dẫn HTTPS (ví dụ: `https://github.com/TenNhom/ten-repo.git`).
4.  Mở terminal, `cd` đến thư mục bạn muốn lưu code (ví dụ: `cd Documents/Projects`).
5.  Gõ lệnh:
    ```bash
    git clone [đường-dẫn-bạn-vừa-copy]
    ```
6.  `cd` vào thư mục repo vừa được tạo: `cd ten-repo`

### Bước 2: Bắt đầu làm (Mỗi lần làm paper mới)

Mỗi khi bạn bắt đầu làm một paper mới, bạn phải làm các bước sau.

1.  **Cập nhật code mới nhất:** Luôn đảm bảo bạn đang ở nhánh `main` (nhánh chính) và có code mới nhất từ "trung tâm" (GitHub).
    ```bash
    git checkout main
    git pull origin main
    ```
2.  **Tạo nhánh mới:** Tạo một "nhánh" (branch) riêng cho paper của bạn. Việc này giúp code của bạn không ảnh hưởng đến code chung khi chưa hoàn thiện.
    ```bash
    # Ví dụ tên nhánh: feature/implement-paper-abc
    git checkout -b feature/[ten-paper-ngan-gon-cua-ban]
    ```
    Lệnh này sẽ tạo ra một nhánh mới và tự động chuyển bạn sang nhánh đó.

### Bước 3: Code và Lưu thay đổi (Add & Commit)

1.  **Tạo thư mục:** Vào thư mục `papers/`, tạo một thư mục mới cho paper của bạn (ví dụ: `papers/fast-rcnn`).
2.  **Tạo file README:** Copy-paste **Template README con** (ở dưới) vào thư mục paper của bạn và đặt tên là `README.md`. Hãy điền thông tin vào đó.
3.  **Bắt đầu code:** Thêm code, notebook, file `requirements.txt` (nếu cần) vào thư mục của bạn.
4.  **Lưu thay đổi:** Sau khi code xong một phần, bạn cần "lưu" lại các thay đổi.
    ```bash
    # Đánh dấu tất cả các file bạn đã thay đổi trong thư mục paper của bạn
    git add papers/[ten-thu-muc-paper-cua-ban]/
    
    # Ghi chú (Commit) cho lần lưu này
    git commit -m "Feat: Implement [ten paper] - phan 1"
    ```
    (Bạn có thể `add` và `commit` nhiều lần trong quá trình code).

### Bước 4: Đẩy code lên GitHub (Push)

Khi bạn đã sẵn sàng chia sẻ code (hoặc muốn backup lên GitHub), bạn "đẩy" (push) nhánh của mình lên.

```bash
# Lần đầu tiên push nhánh này, dùng lệnh này (thay đúng tên nhánh):
git push -u origin feature/[ten-paper-ngan-gon-cua-ban]

# Từ lần thứ 2 trở đi, bạn chỉ cần gõ:
git push
```

### Bước 5: Tạo Pull Request (PR)
Đây là bước "yêu cầu" gộp code của bạn vào code chung (nhánh `main`).

1. Truy cập trang repo trên GitHub.

2. Bạn sẽ thấy một thanh màu vàng hiện lên với tên nhánh của bạn. Nhấn vào nút "**Compare & pull request**".

3. Viết tiêu đề và mô tả:

- Tiêu đề: Ghi rõ bạn làm gì (ví dụ: `Implement [Tên Paper]`).
- Mô tả: Ghi "Closes #[số Issue]" (nếu bạn có tạo Issue ở Bước 0).

4. Reviewers: Ở thanh bên phải, tìm mục "Reviewers" và tag (gắn thẻ) 1-2 thành viên trong nhóm.

5. Nhấn nút "**Create pull request**".

### Bước 6: Thảo luận và Hợp nhất (Merge)
- Nhóm của bạn sẽ vào review code. Họ có thể để lại "comment" (bình luận) yêu cầu bạn sửa.
- Nếu cần sửa, bạn chỉ cần **code tiếp trên máy, sau đó `add`, `commit`, và `push`** như Bước 3 & 4. PR sẽ tự động cập nhật.
- Khi code của bạn được "Approve" (chấp thuận), một người sẽ nhấn nút "Merge" để gộp code của bạn vào `main`.

**Chúc mừng! Bạn đã đóng góp thành công!**

---

🌟 **Template cho `README.md` (Con)**
(*Hãy copy nội dung này vào file README.md trong thư mục paper của bạn*)
```markdown
# Paper: [Tên đầy đủ của Paper]

* **Link Paper:** [dán link PDF vào đây]
* **Tác giả:** [Tên các tác giả paper]
* **Năm:** [Năm xuất bản]
* **Người thực hiện:** `@username-github-cua-ban`

## 1. Mô tả ngắn
(Paper này giải quyết vấn đề gì? Ý tưởng chính là gì? Chỉ cần 2-3 gạch đầu dòng)

* ...
* ...

## 2. Cách chạy
(Làm sao để người khác chạy được code / notebook của bạn?)

**Ví dụ:**

1.  (Nếu cần) Cài đặt thư viện: 
    ```bash
    pip install -r requirements.txt
    ```
2.  (Nếu cần) Tải data (Xem `DATA_README.md` ở thư mục gốc).
3.  Mở file `demo.ipynb` và chạy các cell từ trên xuống dưới.

## 3. Kết quả (Nếu có)
(Show một vài kết quả, hình ảnh, biểu đồ tái hiện được từ paper)
```