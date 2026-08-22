#!/bin/bash
echo "Setting up Home Agent..."

# Install requirements
echo "Installing Python dependencies..."
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create .env if not exists
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env file. Please edit it to add your API keys."
fi

# Configure Skills
echo "Configuring skills with your local paths..."
PYTHON_BIN=$(pwd)"/venv/bin/python"
FAST_CLI_PATH=$(pwd)"/fast_cli.py"

mkdir -p skills
for file in skills_template/*.md; do
    filename=$(basename "$file")
    sed "s|{{PYTHON_BIN}}|$PYTHON_BIN|g" "$file" | sed "s|{{FAST_CLI_PATH}}|$FAST_CLI_PATH|g" > "skills/$filename"
done

echo "Setup complete! Now you need to:"
echo "1. Put your Firebase credentials in 'firebase-credentials.json'"
echo "2. Edit '.env' with your Gemini API key"
echo "3. Copy the 'skills/' folder to your Hermes Agent skills directory (e.g., ~/.hermes/skills/home-agent/)"
echo "4. Run 'python fast_daemon.py' in the background to start the socket server"
