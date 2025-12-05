# Novel Website

## 專案簡介

這是一個基於 Vue.js 和 Django 建立的非營利小說平台。旨在提供一個現代化、注重使用者體驗的線上閱讀與創作環境。

## 主要功能

- **使用者認證**：完整的註冊、登入、登出功能。
- **作者儀表板**：
  - 小說與章節管理：作者可以新增、編輯、刪除自己的小說和章節。
  - 富文本編輯器：支援標題、段落、粗體、斜體、清單、水平分割線及圖片上傳。
  - 作者個人資料管理：編輯筆名、個人簡介、頭像等。
- **核心閱讀功能**：
  - 小說詳情頁：顯示小說簡介、章節列表等。
  - 閱讀器：支援黑暗/白色模式切換、閱讀進度追蹤、自動恢復閱讀位置。
  - 書架功能：使用者可以收藏喜歡的小說到書架。
- **社群與互動**：
  - 作者公開頁面：展示作者的個人資訊及其所有作品。
  - （未來規劃）評論系統、排行榜、Discord 更新通知等。

## 技術棧

### 後端 (Backend)

- **框架**：Django 4.x
- **API**：Django REST Framework (DRF)
- **資料庫**：PostgreSQL
- **認證**：Django REST Framework Simple JWT
- **圖片儲存**：Django 的 `default_storage` (通常配置為本地檔案系統或雲儲存)

### 前端 (Frontend)

- **框架**：Vue.js 3 (搭配 Vite)
- **狀態管理**：Pinia
- **路由**：Vue Router
- **樣式**：Tailwind CSS v3
- **富文本編輯器**：Tiptap
- **套件管理器**：pnpm

### 部署 (Deployment)

- **作業系統**：Rocky Linux (或其他基於 RHEL 的發行版)
- **Web 伺服器**：Nginx (作為反向代理)
- **應用程式伺服器**：Gunicorn
- **安全**：SELinux (自訂策略)

## 環境設定與運行

### 先決條件

- Python 3.9+ (建議使用 pyenv 或 miniconda 管理)
- Node.js (建議使用 nvm 管理，專案使用 `v22.17.0`)
- PostgreSQL 資料庫
- pnpm (前端套件管理器)

### 後端設定

1.  **複製專案**：
    ```bash
    git clone <您的 GitHub 倉庫地址>
    cd novel
    ```
2.  **建立並啟用 Python 虛擬環境**：
    ```bash
    python3.9 -m venv venv
    source venv/bin/activate
    ```
3.  **安裝 Python 依賴**：
    ```bash
    pip install -r requirements.txt
    ```
4.  **設定環境變數**：
    建立 `.env` 檔案在專案根目錄，並填寫必要的環境變數，例如：
    ```env
    SECRET_KEY=your_django_secret_key
    DEBUG=True
    DATABASE_URL=postgres://user:password@host:port/dbname
    # DISCORD_WEBHOOK_URL=your_discord_webhook_for_errors (選填)
    ```
5.  **執行資料庫遷移**：
    ```bash
    python manage.py migrate
    ```
6.  **建立超級使用者 (管理員帳號)**：
    ```bash
    python manage.py createsuperuser
    ```
7.  **運行後端開發伺服器**：
    ```bash
    python manage.py runserver
    ```
    後端將在 `http://127.0.0.1:8000/` 運行。

### 前端設定

1.  **進入前端目錄**：
    ```bash
    cd frontend
    ```
2.  **使用正確的 Node.js 版本** (如果使用 nvm)：
    ```bash
    nvm use
    ```
3.  **安裝前端依賴**：
    ```bash
    pnpm install
    ```
4.  **運行前端開發伺服器**：
    ```bash
    pnpm dev
    ```
    前端將在 `http://127.0.0.1:5173/` (預設) 運行。

## 部署

專案包含用於 Rocky Linux 環境的部署腳本和配置範例：

- `deploy.sh`：一個簡單的部署腳本，用於建置前端、重啟後端服務等。
- `mygunicorn.pp` / `mygunicorn.te`：SELinux 策略模組，用於允許 Gunicorn 在 `Enforcing` 模式下運行。
- Nginx 配置：通常位於 `/etc/nginx/conf.d/novel.conf`，用於反向代理。
- Gunicorn `systemd` 服務：通常位於 `/etc/systemd/system/gunicorn.service`，用於管理 Gunicorn 進程。

**重要提示**：部署涉及系統級配置，請務必仔細閱讀相關檔案並根據您的伺服器環境進行調整。

## 貢獻

歡迎任何形式的貢獻！如果您有任何建議、錯誤報告或功能請求，請隨時提交 Issue 或 Pull Request。

## 授權

本專案採用 MIT 授權。詳情請參閱 `LICENSE` 檔案。
