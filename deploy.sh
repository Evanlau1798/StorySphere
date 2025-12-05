#!/bin/bash

# 當任何指令失敗時立即停止腳本
set -e

# --- 腳本說明 ---
echo "🚀 Starting deployment script..."

# --- 導航到專案根目錄 ---
echo "📂 Navigating to project root..."
cd /opt/novel || exit

# --- 後端準備 (如果需要) ---
echo "🐍 Activating Python virtual environment..."
source venv/bin/activate
# echo "🔄 Installing/updating Python dependencies..."
# pip install -r requirements.txt
echo "Applying database migrations..."
python manage.py migrate

# --- 前端建置 ---
echo "

🎨 Building frontend application..."
echo "   (Navigating to frontend directory)"
cd frontend

# 為了在腳本中使用 nvm，需要先 source 它
#echo "   (Sourcing nvm)"
#. ~/.nvm/nvm.sh

#echo "   (Using correct Node.js version via nvm)"
#nvm use

echo "   (Installing/updating npm packages with pnpm)"
pnpm install

echo "   (Building static files with pnpm)"
pnpm build

# --- 返回專案根目錄 ---
echo "

📂 Returning to project root..."
cd ..

# --- 重啟服務 ---
echo "

🔄 Restarting services..."

echo "   (Restarting Gunicorn backend service)"
sudo systemctl restart gunicorn

echo "   (Restarting Nginx frontend service)"
sudo systemctl restart nginx

# --- 完成 ---
echo "

✅ Deployment finished successfully!
"