# AutoLDPlayer

AutoLDPlayer là một phần mềm hỗ trợ chạy Macro trên giả lập LDPlayer thông qua kết nối ADB (Android Debug Bridge), được xây dựng bằng Python và giao diện PySide6 hiện đại (chuẩn UI Premium Blue Studio).

## 🌟 Tính năng chính

- **Quản lý thiết bị linh hoạt:** Tự động quét và kết nối với các thiết bị giả lập LDPlayer đang chạy thông qua ADB.
- **Biên soạn kịch bản Macro (Actions):** 
  - Hỗ trợ các lệnh cơ bản: Chạm (Tap), Gõ phím (Key Event), Chờ (Delay).
  - Tự động nhận diện độ phân giải màn hình của giả lập.
- **Hệ thống tải & nhập Code thông minh:**
  - Tải danh sách code từ website thông qua API.
  - Nhập code hàng loạt từ văn bản copy/paste với khả năng nhận diện định dạng cực kỳ thông minh (như `1. code`, `1 code`, `1: code`...).
  - Quản lý hàng đợi code (Queue) tự động phân bổ cho macro.
- **Giao diện Modern UI:** Được thiết kế tỉ mỉ với tông màu xanh `#3399FF` dịu mắt, Dark Theme tích hợp giúp sử dụng trong thời gian dài không bị mỏi mắt.

## 🛠 Yêu cầu hệ thống

- Python 3.10+
- Giả lập LDPlayer đã bật tính năng "ADB Debugging" (Cài đặt -> Mạng -> Bật cầu nối ADB).
- Môi trường Windows.

## 📦 Cài đặt thư viện

Bạn cần cài đặt các thư viện Python sau trước khi chạy mã nguồn:

```bash
pip install -r requirements.txt
```

## 🚀 Hướng dẫn sử dụng (Mã nguồn)

1. Khởi động các instance của LDPlayer.
2. Chạy ứng dụng:
   ```bash
   python main.py
   ```
3. Trên giao diện ứng dụng:
   - Nhấn **Làm mới** để tìm thiết bị.
   - Chọn một thiết bị từ danh sách.
   - Sang thẻ **Code**, bạn có thể tải từ Web hoặc dán text để chuẩn bị code.
   - Xây dựng các bước Macro (thêm Tap, Key, Code...).
   - Nhấn **Chạy Macro** để bắt đầu.

## 🏗 Đóng gói thành file thực thi (.exe)

Dự án đã cấu hình sẵn PyInstaller qua file `AutoLDPlayer.spec`. Chỉ cần chạy:

```bash
pyinstaller AutoLDPlayer.spec -y
```

Kết quả sẽ nằm ở thư mục `dist/AutoLDPlayer`.
