#!/bin/bash
set -e

echo "=== Setting up Home Agent Template ==="

# 1. Python Environment
echo "Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Environment Configuration
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ Created .env from template. Please configure your API keys."
fi

# 3. Web Dashboard
if [ -d "web" ]; then
    echo "Installing web dashboard dependencies..."
    cd web
    npm install
    if [ ! -f .env.local ]; then
        cp .env.example .env.local
    fi
    cd ..
fi

# 4. Configure Skills Template
if [ -d "skills_template" ]; then
    echo "Configuring local skills..."
    PYTHON_BIN="$(pwd)/venv/bin/python"
    FAST_CLI_PATH="$(pwd)/fast_cli.py"
    mkdir -p skills
    for file in skills_template/*.md; do
        if [ -f "$file" ]; then
            filename=$(basename "$file")
            sed "s|{{PYTHON_BIN}}|$PYTHON_BIN|g" "$file" | sed "s|{{FAST_CLI_PATH}}|$FAST_CLI_PATH|g" > "skills/$filename"
        fi
    done
fi

echo ""
echo "=== Setup Complete! ==="
echo "Next Steps:"
echo "1. Place your Google Cloud service account JSON at 'firebase-credentials.json'"
echo "2. Edit '.env' with your GEMINI_API_KEY / NINEROUTER_URL"
echo "3. Run 'python fast_daemon.py' to launch the background socket server"
echo "4. In another terminal, run 'cd web && npm run dev' to access the dashboard"
