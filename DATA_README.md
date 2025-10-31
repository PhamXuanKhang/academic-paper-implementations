# Hướng dẫn Quản lý Dataset bằng DVC và Google Drive

## Vấn đề là gì?
Git (và GitHub) không được thiết kế để lưu các file dữ liệu lớn (datasets, model checkpoints...). Nếu bạn đẩy file vài trăm MB lên, repo sẽ bị phình to rất nhanh.

## Giải pháp: DVC (Data Version Control)
Chúng ta dùng DVC để quản lý data. Luồng hoạt động sẽ là:
* **Git:** Chỉ lưu code (`.py`) và các file "metadata" (file `.dvc` siêu nhẹ).
* **Google Drive:** Là nơi lưu trữ file data thật sự.
* **DVC:** Là công cụ kết nối Git và Google Drive.

---

## 1. Cài đặt (Làm 1 lần duy nhất)

Mỗi thành viên trong nhóm cần chạy lệnh này trên máy của mình:
```bash
pip install dvc dvc-gdrive
```

## 2. Dành cho NGƯỜI DÙNG (Tôi muốn TẢI data về để chạy code)
Đây là việc bạn sẽ làm thường xuyên nhất.

1.**Lấy code mới nhất:** (Đảm bảo bạn có file `.dvc` mới nhất)

```bash
git pull
```

2.**Lấy data về máy:**

```bash
dvc pull
```

**Xong!** DVC sẽ tự động đọc các file `.dvc`, tìm đến Google Drive và tải các file data còn thiếu về đúng thư mục `data/` trên máy của bạn.

## 3. Dành cho NGƯỜI ĐÓNG GÓP (Tôi muốn THÊM data mới)
Khi bạn là người đầu tiên thêm một dataset cho paper của mình:

1.**Copy data:** Copy file/thư mục dataset của bạn vào thư mục `data/` (ví dụ: `data/my-new-dataset.zip`).

2.**Theo dõi bằng DVC:**

```bash
# Thay 'data/my-new-dataset.zip' bằng tên file/thư mục của bạn
dvc add data/my-new-dataset.zip
```

Lệnh này tạo ra file `data/my-new-dataset.zip.dvc`. Đây chính là file metadata.

3. **Đẩy data lên Google Drive:**

```bash
dvc push
```

*Lưu ý: Lần đầu tiên chạy, DVC sẽ mở trình duyệt yêu cầu bạn đăng nhập và cấp quyền cho Google Drive. Hãy làm theo hướng dẫn.*

3. **Commit file metadata (Quan trọng!):** Bây giờ bạn cần commit file `.dvc` (file nhẹ) chứ **KHÔNG PHẢI** file data (file nặng).

```bash
# Git đã tự động bỏ qua 'data/my-new-dataset.zip' (nhờ file .gitignore)
# Chúng ta chỉ cần add file .dvc
git add data/my-new-dataset.zip.dvc

git commit -m "Data: Add my-new-dataset"
```

4. **Đẩy code:**

```bash
git push
```

Bây giờ, người khác chỉ cần `git pull` (để lấy file `.dvc` của bạn) và `dvc pull` (để lấy data về).

## 4. Cấu hình (Dành cho Quản trị viên - Chỉ làm 1 lần)
(Các thành viên bình thường không cần quan tâm mục này)

Nếu bạn là người tạo repo này, bạn cần kết nối DVC với Google Drive:

1. **Tạo thư mục Google Drive:** Tạo một thư mục chung trên Google Drive (ví dụ: AI_Paper_DVC_Storage).

2. **Lấy ID thư mục:** Truy cập thư mục đó, nhìn lên URL: https://drive.google.com/drive/folders/[ĐÂY LÀ ID THƯ MỤC]

3. **Khởi tạo DVC:** (Nếu chưa làm)

```bash
dvc init
```

4. **Kết nối Google Drive:** Chạy lệnh sau (thay ID của bạn vào):

```bash
dvc remote add -d mygdrive gdrive://[ID-THU-MUC-GOOGLE-DRIVE]
```

5. **Commit thay đổi cấu hình:**

```bash
git add .dvc/config .dvc/.gitignore
git commit -m "Config: Initialize DVC with Google Drive remote"
git push
```