# Hướng dẫn Quản lý Dataset bằng DVC và Azure Blob Storage

## Vấn đề là gì?
Git (và GitHub) không được thiết kế để lưu các file dữ liệu lớn (datasets, model checkpoints...). Nếu bạn đẩy file vài trăm MB lên, repo sẽ bị phình to rất nhanh.

## Giải pháp: DVC (Data Version Control)
Chúng ta dùng DVC để quản lý data. Luồng hoạt động sẽ là:
* **Git:** Chỉ lưu code (`.py`) và các file "metadata" (file `.dvc` siêu nhẹ).
* **Azure Blob Storage:** Là nơi lưu trữ file data thật sự.
* **DVC:** Là công cụ kết nối Git và Azure Blob Storage.

---

## 1. Cài đặt (Làm 1 lần duy nhất)

Mỗi thành viên trong nhóm cần chạy lệnh này trên máy của mình để cài DVC và các thư viện hỗ trợ Azure:
```bash
# Điều này là bắt buộc!
# 'dvc[azure]' cài đặt các thư viện Python (Azure SDK)
# để DVC "nói chuyện" được với Azure.
pip install dvc[azure]
```

## 2. Dành cho NGƯỜI DÙNG (Tôi muốn TẢI data về để chạy code)
Đây là việc bạn sẽ làm thường xuyên nhất.

1.  **Lấy code mới nhất:** (Đảm bảo bạn có file `.dvc` mới nhất)
    ```bash
    git pull
    ```

2.  **Lấy data về máy:**
    ```bash
    dvc pull
    ```

**Xong!** DVC sẽ tự động đọc các file `.dvc`, tìm đến **Azure Blob Storage** và tải các file data còn thiếu về đúng thư mục `data/` trên máy của bạn.

## 3. Dành cho NGƯỜI ĐÓNG GÓP (Tôi muốn THÊM data mới)
Khi bạn là người đầu tiên thêm một dataset cho paper của mình:

1.  **Copy data:** Copy file/thư mục dataset của bạn vào thư mục `data/` (ví dụ: `data/my-new-dataset.zip`).

2.  **Theo dõi bằng DVC:**
    ```bash
    # Thay 'data/my-new-dataset.zip' bằng tên file/thư mục của bạn
    dvc add data/my-new-dataset.zip
    ```
    Lệnh này tạo ra file `data/my-new-dataset.zip.dvc`. Đây chính là file metadata.

3.  **Đẩy data lên Azure:**
    ```bash
    dvc push
    ```
    *Lưu ý: Đảm bảo bạn đã cấu hình xác thực (xem Mục 4). Nếu bạn đã cấu hình đúng (ví dụ: dùng `connection_string`), DVC sẽ tự động kết nối và đẩy file lên.*

4.  **Commit file metadata (Quan trọng!):** Bây giờ bạn cần commit file `.dvc` (file nhẹ) chứ **KHÔNG PHẢI** file data (file nặng).
    ```bash
    # Git đã tự động bỏ qua 'data/my-new-dataset.zip' (nhờ file .gitignore)
    # Chúng ta chỉ cần add file .dvc
    git add data/my-new-dataset.zip.dvc

    git commit -m "Data: Add my-new-dataset"
    ```

5.  **Đẩy code:**
    ```bash
    git push
    ```

Bây giờ, người khác chỉ cần `git pull` (để lấy file `.dvc` của bạn) và `dvc pull` (để lấy data về).

## 4. Cấu hình (Dành cho Quản trị viên - Chỉ làm 1 lần)
(Các thành viên bình thường không cần quan tâm mục này)

Nếu bạn là người tạo repo này, bạn cần kết nối DVC với Azure Blob Storage:

1.  **Chuẩn bị trên Azure:**
    * Tạo một **Tài khoản lưu trữ (Storage Account)** trên Azure.
    * Trong tài khoản đó, tạo một **Bộ chứa Blob (Blob Container)** (ví dụ: `dvc-paper-storage`).

2.  **Khởi tạo DVC:** (Nếu chưa làm)
    ```bash
    # Phải chạy lệnh này ở thư mục gốc của dự án!
    dvc init
    ```

3.  **Kết nối Azure Remote:**
    Chạy lệnh sau để DVC biết kho lưu trữ của bạn ở đâu.
    ```bash
    # 'azure-remote' là tên bạn đặt, 'dvc-paper-storage' là tên container của bạn
    dvc remote add -d azure-remote azure://dvc-paper-storage
    ```

4.  **Cấu hình xác thực (Khuyến nghị):**
    Chúng ta sẽ dùng **Connection String** (Chuỗi kết nối) vì nó an toàn và không yêu cầu thành viên nào cũng phải cài Azure CLI.
    * Lấy Chuỗi kết nối từ Storage Account của bạn trên Azure Portal.
    * Chạy lệnh sau. **Cờ `--local`** sẽ lưu bí mật này vào file `.dvc/config.local` (file này *không* bị đẩy lên Git), giữ an toàn cho tài khoản của bạn.
    ```bash
    dvc remote modify --local azure-remote connection_string 'PASTE_CHUOI_KET_NOI_CUA_BAN_VAO_DAY'
    ```

5.  **Commit thay đổi cấu hình:**
    ```bash
    # Lệnh này chỉ add file .dvc/config (chứa URL)
    # File .dvc/config.local (chứa bí mật) đã tự động được .gitignore bỏ qua
    git add .dvc/config .dvc/.gitignore
    
    git commit -m "Config: Initialize DVC with Azure Blob remote"
    git push
    ```