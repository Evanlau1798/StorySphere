import os
import httpx
import asyncio
import aiofiles
import zipfile
import logging
import base64
import subprocess
from datetime import datetime
from discord_webhook import DiscordWebhook
from tqdm.asyncio import tqdm_asyncio
import dotenv

dotenv.load_dotenv()

# --- 設定 ---
# 網站媒體檔案的根目錄
MEDIA_ROOT = "/var/www/novel_site/media/" 
# 備份檔案暫存目錄
BACKUP_TEMP_DIR = "/tmp/site_backups/" 
# Discord Webhook URL
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL") 
# PixelDrain API 金鑰
PIXELDRAN_API_KEY = os.getenv("PIXELDRAN_API_KEY") 
LOG_FILE = "/var/log/novel_site_backup.log"

# 資料庫設定
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")

# 設定 logging
logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")

def backup_and_zip_site(media_path, backup_dir):
    """
    傾印資料庫並將網站媒體檔案打包成 zip。
    """
    try:
        os.makedirs(backup_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        # 1. 傾印 PostgreSQL 資料庫
        db_dump_path = os.path.join(backup_dir, f"db_dump_{timestamp}.sql")
        logging.info(f"正在傾印資料庫至 {db_dump_path}...")
        
        # 設定環境變數以避免密碼提示
        env = os.environ.copy()
        env['PGPASSWORD'] = DB_PASSWORD
        
        dump_command = [
            'pg_dump',
            '-h', DB_HOST,
            '-U', DB_USER,
            '-d', DB_NAME,
            '-f', db_dump_path
        ]
        subprocess.run(dump_command, check=True, env=env, capture_output=True, text=True)
        logging.info("資料庫傾印完成。")

        # 2. 打包所有資源
        zip_filename = f"site_backup_{timestamp}.zip"
        zip_filepath = os.path.join(backup_dir, zip_filename)
        logging.info(f"正在打包網站資源至 {zip_filepath}...")
        
        with zipfile.ZipFile(zip_filepath, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # 添加資料庫備份檔
            zipf.write(db_dump_path, os.path.basename(db_dump_path))
            # 添加所有媒體檔案
            for root, _, files in os.walk(media_path):
                for file in files:
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, media_path)
                    zipf.write(full_path, os.path.join('media', rel_path)) # 在 zip 內也建立 media 目錄

        # 清理資料庫傾印檔案
        os.remove(db_dump_path)
        
        return zip_filepath
    except Exception as e:
        logging.error(f"備份與打包時發生錯誤: {e}")
        if isinstance(e, subprocess.CalledProcessError):
            logging.error(f"pg_dump Stderr: {e.stderr}")
        raise

async def upload_to_pixeldrain(file_path, api_key):
    try:
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        logging.info(f"開始上傳至 PixelDrain (檔案大小: {file_size/1024**2:.2f} MB, 檔名: {file_name})")
        headers = { "Authorization": "Basic " + base64.b64encode(bytes(":" + api_key, 'utf-8')).decode('utf-8') }
        
        async with aiofiles.open(file_path, 'rb') as f:
            data = await f.read()
            async with httpx.AsyncClient(timeout=None) as client:
                response = await client.put(f"https://pixeldrain.com/api/file/{file_name}", content=data, headers=headers)
        response.raise_for_status()
        result = response.json()
        file_id = result.get('id')
        logging.info(f"檔案上傳成功，ID：{file_id}")
        return file_id
    except Exception as e:
        logging.error(f"上傳至 PixelDrain 時發生錯誤: {e}")
        return None

def send_to_discord(file_id, webhook_url):
    # 此函數與您提供的版本相同，此處省略以保持簡潔
    # ... (複製您提供的 send_to_discord 函數)
    try:
        file_url = f"https://pixeldrain.com/u/{file_id}"
        message = f"✅ 網站每日備份成功！\n備份時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n下載連結: {file_url}"
        webhook = DiscordWebhook(url=webhook_url, content=message)
        response = webhook.execute()
        response.raise_for_status()
        logging.info("成功發送 Discord 通知")
    except Exception as e:
        logging.error(f"發送 Discord 通知時發生錯誤: {e}")

async def main():
    zip_file = None # 確保變數存在
    try:
        logging.info("--- 開始每日網站備份任務 ---")

        # 1. 備份與打包
        zip_file = backup_and_zip_site(MEDIA_ROOT, BACKUP_TEMP_DIR)
        
        # 2. 上傳至 PixelDrain
        file_id = await upload_to_pixeldrain(zip_file, PIXELDRAN_API_KEY)
        
        if file_id:
            # 3. 傳送到 Discord
            send_to_discord(file_id, DISCORD_WEBHOOK_URL)
        else:
            # 上傳失敗的通知
            webhook = DiscordWebhook(url=DISCORD_WEBHOOK_URL, content=f"❌ 網站備份上傳失敗！請檢查日誌: {LOG_FILE}")
            webhook.execute()
            
    except Exception as e:
        logging.exception(f"主程式發生嚴重錯誤: {e}")
        # 發生錯誤的通知
        webhook = DiscordWebhook(url=DISCORD_WEBHOOK_URL, content=f"❌ 網站備份腳本執行失敗！請檢查日誌: {LOG_FILE}\n錯誤訊息: {e}")
        webhook.execute()
    finally:
        # 4. 清理本地暫存檔
        if zip_file and os.path.exists(zip_file):
            os.remove(zip_file)
            logging.info(f"已刪除暫存備份檔：{zip_file}")
        logging.info("--- 備份任務結束 ---")

if __name__ == "__main__":
    asyncio.run(main())