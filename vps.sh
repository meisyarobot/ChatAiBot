#!/bin/bash
# ==========================================
#  Auto Start Script for Telegram AI Bot (VPS)
#  by BoysChell | t.me/boyschell
# ==========================================

BOT_NAME="AutoChatBot"
PYTHON_VERSION="python3"
VENV_DIR="venv"
REQUIREMENTS="requirements.txt"
MAIN_FILE="Chell.py"
SCREEN_NAME="AiBot"
VENV_ACTIVATE="$VENV_DIR/bin/activate"

echo "====================================="
echo "🚀 Starting $BOT_NAME (VPS MODE)"
echo "====================================="

echo "✅ Memeriksa prasyarat sistem..."
sudo apt update -y >/dev/null 2>&1
sudo apt install ffmpeg -y

if ! command -v $PYTHON_VERSION &> /dev/null; then
    echo "❌ Python3 belum terpasang. Menginstal..."
    sudo apt install python3 python3-pip -y
fi

if ! command -v screen &> /dev/null; then
    echo "🧰 Menginstal screen..."
    sudo apt install screen -y
fi

if ! command -v git &> /dev/null; then
    echo "🧰 Menginstal git..."
    sudo apt install git -y
fi

echo "📦 Memperbarui pip..."
$PYTHON_VERSION -m pip install -U pip wheel setuptools >/dev/null 2>&1

if [ ! -d "$VENV_DIR" ]; then
    echo "🪄 Membuat virtual environment..."
    $PYTHON_VERSION -m venv $VENV_DIR
fi

source $VENV_ACTIVATE

if [ -f "$REQUIREMENTS" ]; then
    echo "📦 Menginstal/memperbarui dependencies..."
    pip install -r $REQUIREMENTS
else
    echo "⚠️ File requirements.txt tidak ditemukan!"
fi

if [ -f ".env" ]; then
    EXTRA_REPO=$(awk -F'=' '/^EXTRA_REPO/ {print $2}' .env | tr -d '"' | tr -d "'")
    if [ ! -z "$EXTRA_REPO" ]; then
        echo "🔁 Mengecek repository plugin tambahan: $EXTRA_REPO"
        if [ -d "extra_plugins/.git" ]; then
            cd extra_plugins
            echo "↪️ Melakukan git pull..."
            git pull
            cd ..
        else
            echo "📥 Melakukan git clone..."
            git clone "$EXTRA_REPO" extra_plugins
        fi
    fi
fi

if screen -list | grep -q "$SCREEN_NAME"; then
    echo "🧹 Menutup screen lama ($SCREEN_NAME)..."
    screen -S "$SCREEN_NAME" -X quit || screen -X -S "$SCREEN_NAME" quit
fi

echo "🖥️ Menjalankan bot di screen: $SCREEN_NAME"

screen -dmS "$SCREEN_NAME" bash -c "
    source $VENV_ACTIVATE
    exec $PYTHON_VERSION $MAIN_FILE
"

echo "✅ Bot telah berjalan di background!"
echo "💬 Untuk melihat log, gunakan:"
echo "    screen -r $SCREEN_NAME"
echo "====================================="
