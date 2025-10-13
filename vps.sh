#!/bin/bash
# ==========================================
#  Auto Start Script for Telegram AI Bot (VPS)
#  by BoysChell | t.me/boyschell
# ==========================================

BOT_NAME="AutoChatBot"
PYTHON_VERSION="python3"
VENV_DIR="venv"
REQUIREMENTS="requirements.txt"
MAIN_FILE="main.py"
SCREEN_NAME="autochat"

echo "====================================="
echo "🚀 Starting $BOT_NAME (VPS MODE)"
echo "====================================="

if ! command -v $PYTHON_VERSION &> /dev/null; then
    echo "❌ Python3 belum terpasang!"
    apt update -y && apt install python3 python3-pip -y
fi

if ! command -v screen &> /dev/null; then
    echo "🧰 Menginstal screen..."
    apt install screen -y
fi

if ! command -v git &> /dev/null; then
    echo "🧰 Menginstal git..."
    apt install git -y
fi

echo "📦 Memperbarui pip..."
$PYTHON_VERSION -m pip install -U pip wheel setuptools >/dev/null 2>&1

if [ ! -d "$VENV_DIR" ]; then
    echo "🪄 Membuat virtual environment..."
    $PYTHON_VERSION -m venv $VENV_DIR
fi

source $VENV_DIR/bin/activate

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

if screen -list | grep -q "$SCREEN_NAME"; then
    echo "🧹 Menutup screen lama..."
    screen -S "$SCREEN_NAME" -X quit
fi

echo "🖥️ Menjalankan bot di screen: $SCREEN_NAME"
screen -dmS "$SCREEN_NAME" bash -c "
source $VENV_DIR/bin/activate
python3 $MAIN_FILE
"

echo "✅ Bot telah berjalan di background!"
echo "💬 Untuk melihat log, gunakan:"
echo "    screen -r $SCREEN_NAME"
echo "====================================="
