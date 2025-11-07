#!/bin/bash

# Nimbus Installation Script
# Automated installation for Nimbus backup solution

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored message
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

print_header() {
    echo ""
    print_message "$BLUE" "═══════════════════════════════════════════════"
    print_message "$BLUE" "  🌥️  Nimbus Installation Script"
    print_message "$BLUE" "  Enterprise Backup & Cloud Sync Solution"
    print_message "$BLUE" "═══════════════════════════════════════════════"
    echo ""
}

check_requirements() {
    print_message "$YELLOW" "🔍 Checking requirements..."

    # Check Python version
    if ! command -v python3 &> /dev/null; then
        print_message "$RED" "❌ Python 3 is not installed!"
        print_message "$YELLOW" "Please install Python 3.8 or higher"
        exit 1
    fi

    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    print_message "$GREEN" "✓ Python $PYTHON_VERSION found"

    # Check pip
    if ! command -v pip3 &> /dev/null; then
        print_message "$RED" "❌ pip is not installed!"
        print_message "$YELLOW" "Installing pip..."
        python3 -m ensurepip --upgrade
    fi
    print_message "$GREEN" "✓ pip found"

    # Check git
    if ! command -v git &> /dev/null; then
        print_message "$YELLOW" "⚠️  git is not installed (optional)"
    else
        print_message "$GREEN" "✓ git found"
    fi
}

create_venv() {
    print_message "$YELLOW" "📦 Creating virtual environment..."

    if [ -d "venv" ]; then
        print_message "$YELLOW" "Virtual environment already exists, skipping..."
    else
        python3 -m venv venv
        print_message "$GREEN" "✓ Virtual environment created"
    fi
}

activate_venv() {
    print_message "$YELLOW" "🔄 Activating virtual environment..."

    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        print_message "$GREEN" "✓ Virtual environment activated"
    else
        print_message "$RED" "❌ Failed to activate virtual environment"
        exit 1
    fi
}

install_dependencies() {
    print_message "$YELLOW" "📥 Installing dependencies..."

    # Upgrade pip
    pip install --upgrade pip setuptools wheel

    # Install requirements
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        print_message "$GREEN" "✓ Dependencies installed"
    else
        print_message "$RED" "❌ requirements.txt not found"
        exit 1
    fi
}

install_package() {
    print_message "$YELLOW" "📦 Installing Nimbus package..."

    # Install in development mode
    pip install -e .
    print_message "$GREEN" "✓ Nimbus package installed"
}

create_config() {
    print_message "$YELLOW" "⚙️  Creating configuration directory..."

    CONFIG_DIR="$HOME/.config/nimbus"

    if [ ! -d "$CONFIG_DIR" ]; then
        mkdir -p "$CONFIG_DIR/logs"
        mkdir -p "$CONFIG_DIR/keys"
        mkdir -p "$CONFIG_DIR/backups"
        print_message "$GREEN" "✓ Configuration directory created at $CONFIG_DIR"
    else
        print_message "$YELLOW" "Configuration directory already exists"
    fi

    # Copy default config if not exists
    if [ -f "config/settings.yaml" ] && [ ! -f "$CONFIG_DIR/config.yaml" ]; then
        cp config/settings.yaml "$CONFIG_DIR/config.yaml"
        print_message "$GREEN" "✓ Default configuration copied"
    fi
}

run_tests() {
    print_message "$YELLOW" "🧪 Running tests..."

    if command -v pytest &> /dev/null; then
        pytest tests/ -v --tb=short || print_message "$YELLOW" "⚠️  Some tests failed (this is OK for initial setup)"
        print_message "$GREEN" "✓ Tests completed"
    else
        print_message "$YELLOW" "⚠️  pytest not found, skipping tests"
    fi
}

verify_installation() {
    print_message "$YELLOW" "✅ Verifying installation..."

    # Check if nimbus command works
    if python -m app.cli.main --version &> /dev/null; then
        VERSION=$(python -m app.cli.main --version 2>&1 | grep -oP 'version \K[0-9.]+' || echo "unknown")
        print_message "$GREEN" "✓ Nimbus v$VERSION installed successfully!"
    else
        print_message "$RED" "❌ Installation verification failed"
        exit 1
    fi
}

print_next_steps() {
    echo ""
    print_message "$GREEN" "═══════════════════════════════════════════════"
    print_message "$GREEN" "  ✅ Installation Complete!"
    print_message "$GREEN" "═══════════════════════════════════════════════"
    echo ""
    print_message "$BLUE" "📝 Next Steps:"
    echo ""
    echo "  1. Activate the virtual environment:"
    echo "     $ source venv/bin/activate"
    echo ""
    echo "  2. Test the installation:"
    echo "     $ nimbus --version"
    echo "     $ nimbus --help"
    echo ""
    echo "  3. Perform your first backup:"
    echo "     $ nimbus backup /path/to/source -d /path/to/backup"
    echo ""
    echo "  4. View configuration:"
    echo "     $ nimbus config show"
    echo ""
    echo "  5. Read the documentation:"
    echo "     $ cat README.md"
    echo ""
    print_message "$YELLOW" "⭐ If you find Nimbus useful, please give it a star on GitHub!"
    print_message "$BLUE" "   https://github.com/ysntns/nimbus"
    echo ""
}

# Main installation flow
main() {
    print_header
    check_requirements
    create_venv
    activate_venv
    install_dependencies
    install_package
    create_config
    run_tests
    verify_installation
    print_next_steps
}

# Run installation
main
