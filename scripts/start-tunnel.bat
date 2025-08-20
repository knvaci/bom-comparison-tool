@echo off
echo 🚀 Starting ngrok tunnel for BOM Comparison Tool...
echo.

echo 🔑 Setting up authentication...
ngrok config add-authtoken 31THtlOvfItg5OSI2jIuH5dOsnF_2Rh8vohUmKuSmFx59JyyV

echo.
echo 🌐 Starting tunnel to localhost:80...
echo.
echo ⚠️  IMPORTANT: Keep this window open while employees are testing!
echo.
echo 📧 Copy the https://xxxxx.ngrok.app URL and share it with your employees
echo.

ngrok http 80