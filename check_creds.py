import os

# 取得 GOOGLE_APPLICATION_CREDENTIALS 環境變數的值
credentials_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')

if credentials_path:
    print(f"環境變數 GOOGLE_APPLICATION_CREDENTIALS 設置為: {credentials_path}")
    # 檢查該路徑下的檔案是否存在
    if os.path.exists(credentials_path):
        print("檔案已找到！")
    else:
        print("錯誤：根據環境變數，檔案路徑無效。檔案不存在。")
else:
    print("錯誤：環境變數 GOOGLE_APPLICATION_CREDENTIALS 未設置。")