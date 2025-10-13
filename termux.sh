#!/bin/bash
# ==========================================
#  Auto Start Script for Telegram AI Bot (TERMUX)
#  by BoysChell | t.me/boyschell
# ==========================================

BOT_NAME="AutoChatBot"
PYTHON_VERSION="python"
REQUIREMENTS="requirements.txt"
MAIN_FILE="main.py"

echo "====================================="
echo "🚀 Starting $BOT_NAME (TERMUX MODE)"
echo "====================================="

if ! command -v $PYTHON_VERSION &> /dev/null; then
    echo "❌ Python belum terpasang!"
    pkg update -y && pkg install python -y
fi

if ! command -v git &> /dev/null; then
    echo "🧰 Menginstal git..."
    pkg install git -y
fi


echo "📦 Memperbarui pip..."
$PYTHON_VERSION -m pip install -U pip wheel setuptools >/dev/null 2>&1

if [ -f "$REQUIREMENTS" ]; then
    echo "📦 Menginstal dependencies..."
    pip install -r $REQUIREMENTS
else
    echo "⚠️ File requirements.txt tidak ditemukan!"
fi

if [ -f ".env" ]; then
    EXTRA_REPO=$(grep "^EXTRA_REPO=" .env | cut -d '=' -f2)
    if [ ! -z "$EXTRA_REPO" ]; then
        echo "🔁 Mengecek repository plugin tambahan..."
        if [ -d "extra_plugins/.git" ]; then
            cd extra_plugins
            git pull
            cd ..
        else
            git clone "$EXTRA_REPO" extra_plugins
        fi
    fi
fi

echo "🧠 Menjalankan bot..."
python $MAIN_FILE

echo "✅ Bot selesai berjalan!"
echo "====================================="
