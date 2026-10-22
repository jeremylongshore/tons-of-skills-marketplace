#!/bin/bash

# Jeremy's AI Agent Development Plugins Installer
# Date: 2025-10-27
# Author: Jeremy Longshore

echo "=================================================="
echo "   Jeremy's AI Agent Development Plugins Suite   "
echo "=================================================="
echo ""

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to install a plugin
install_plugin() {
    local plugin_name=$1
    local plugin_repo=$2
    echo -e "${BLUE}Installing ${plugin_name}...${NC}"

    # Check if already installed
    if [ -d "$HOME/.claude/plugins/marketplaces/jeremy-plugins/${plugin_name}" ]; then
        echo -e "${YELLOW}${plugin_name} is already installed. Skipping...${NC}"
    else
        echo "/plugin install ${plugin_name}@${plugin_repo}"
        echo -e "${GREEN}✓ ${plugin_name} installation command ready${NC}"
    fi
    echo ""
}

# Display available plugins
echo -e "${BLUE}Available Plugins:${NC}"
echo "1. jeremy-google-adk     - Google Agent Development Kit (ADK) SDK"
echo "2. jeremy-vertex-ai      - Vertex AI & Gemini Integration"
echo "3. jeremy-genkit         - Firebase Genkit Multi-Model Framework"
echo "4. excel-analyst-pro     - Excel Financial Modeling Toolkit"
echo ""

# Ask user what to install
echo -e "${YELLOW}Which plugins would you like to install?${NC}"
echo "Enter numbers separated by space (e.g., 1 2 3 4) or 'all' for everything:"
read -r selection

# Generate installation commands
echo ""
echo -e "${BLUE}Installation Commands:${NC}"
echo "=================================================="

if [[ "$selection" == "all" || "$selection" == *"1"* ]]; then
    echo "/plugin install jeremy-google-adk@jeremylongshore"
fi

if [[ "$selection" == "all" || "$selection" == *"2"* ]]; then
    echo "/plugin install jeremy-vertex-ai@jeremylongshore"
fi

if [[ "$selection" == "all" || "$selection" == *"3"* ]]; then
    echo "/plugin install jeremy-genkit@jeremylongshore"
fi

if [[ "$selection" == "all" || "$selection" == *"4"* ]]; then
    echo "/plugin install excel-analyst-pro@jeremylongshore"
fi

echo "=================================================="
echo ""

# Test commands
echo -e "${BLUE}Test Commands After Installation:${NC}"
echo "=================================================="
echo ""

echo "# Test ADK Plugin:"
echo "adk-agent create --name test-agent --pattern react --model gemini-1.5-pro"
echo ""

echo "# Test Vertex AI Plugin:"
echo "vertex-agent create --name test-vertex --type rag-enhanced"
echo ""

echo "# Test Genkit Plugin:"
echo "genkit-app create --name test-app --language typescript"
echo ""

echo "# Test Excel Plugin:"
echo 'echo "Create a DCF model for Apple" | claude'
echo ""

# Python test script
echo -e "${BLUE}Creating test script...${NC}"
cat > test-jeremy-plugins.py << 'EOF'
#!/usr/bin/env python3
"""
Test script for Jeremy's AI plugins
"""

import os
import sys

def test_imports():
    """Test that plugin modules can be imported"""
    tests = []

    # Test jeremy-google-adk
    try:
        import jeremy_google_adk
        tests.append(("jeremy-google-adk", True))
    except ImportError:
        tests.append(("jeremy-google-adk", False))

    # Test jeremy-vertex-ai
    try:
        import jeremy_vertex_ai
        tests.append(("jeremy-vertex-ai", True))
    except ImportError:
        tests.append(("jeremy-vertex-ai", False))

    # Test jeremy-genkit
    try:
        import jeremy_genkit
        tests.append(("jeremy-genkit", True))
    except ImportError:
        tests.append(("jeremy-genkit", False))

    return tests

def main():
    print("Testing Jeremy's AI Plugins...")
    print("=" * 40)

    results = test_imports()

    for plugin, success in results:
        status = "✓" if success else "✗"
        color = "\033[92m" if success else "\033[91m"
        reset = "\033[0m"
        print(f"{color}{status}{reset} {plugin}")

    print("=" * 40)

    # Check environment variables
    print("\nEnvironment Variables:")
    print("-" * 40)

    env_vars = [
        "CLAUDE_API_KEY",
        "GOOGLE_PROJECT_ID",
        "VERTEX_AI_LOCATION",
        "FIREBASE_PROJECT_ID"
    ]

    for var in env_vars:
        value = os.getenv(var)
        if value:
            masked = value[:4] + "..." if len(value) > 4 else "***"
            print(f"✓ {var}: {masked}")
        else:
            print(f"✗ {var}: Not set")

    print("\nTest complete!")

if __name__ == "__main__":
    main()
EOF

chmod +x test-jeremy-plugins.py

echo -e "${GREEN}✓ Test script created: test-jeremy-plugins.py${NC}"
echo ""

# Display next steps
echo -e "${BLUE}Next Steps:${NC}"
echo "=================================================="
echo "1. Copy the installation commands above into Claude Code"
echo "2. Set required environment variables:"
echo "   export CLAUDE_API_KEY='your-key'"
echo "   export GOOGLE_PROJECT_ID='your-project'"
echo "   export VERTEX_AI_LOCATION='us-central1'"
echo "3. Run the test script: ./test-jeremy-plugins.py"
echo "4. Try creating your first agent!"
echo ""

echo -e "${GREEN}Installation guide complete!${NC}"
echo ""

# Optional: Create requirements file
echo -e "${BLUE}Creating requirements.txt...${NC}"
cat > requirements-jeremy-plugins.txt << 'EOF'
# Jeremy's AI Agent Development Plugins - Python Requirements
# Generated: 2025-10-27

# Google Cloud & Vertex AI
google-cloud-aiplatform>=1.38.0
vertexai>=1.46.0
google-generativeai>=0.3.2
google-cloud-bigquery>=3.13.0
google-cloud-storage>=2.10.0
google-cloud-secret-manager>=2.16.0

# Firebase & Genkit
firebase-admin>=6.1.0

# Anthropic (Claude)
anthropic>=0.18.0

# OpenAI (Optional)
openai>=1.10.0

# Agent Development
pydantic>=2.6.0
tenacity>=8.2.0
httpx>=0.26.0

# Testing
pytest>=7.4.4
pytest-asyncio>=0.23.3
pytest-cov>=4.1.0

# Monitoring
prometheus-client>=0.19.0
structlog>=24.1.0

# Development
python-dotenv>=1.0.0
click>=8.1.0
jinja2>=3.1.0
EOF

echo -e "${GREEN}✓ Requirements file created: requirements-jeremy-plugins.txt${NC}"
echo ""
echo "Install Python dependencies with:"
echo "  pip install -r requirements-jeremy-plugins.txt"
echo ""

echo "=================================================="
echo -e "${GREEN}Setup complete! Happy agent building! 🚀${NC}"
echo "=================================================="