#!/bin/bash
# MKV Manager Installation Script for Linux
# This script installs MKV Manager system-wide like other applications

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_NAME="mkv-manager"
INSTALL_DIR="/opt/$APP_NAME"
BIN_LINK="/usr/local/bin/$APP_NAME"
DESKTOP_FILE="/usr/share/applications/$APP_NAME.desktop"
ICON_DIR="/usr/share/icons/hicolor/256x256/apps"
ICON_FILE="$ICON_DIR/$APP_NAME.png"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}✅${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠️${NC} $1"
}

print_error() {
    echo -e "${RED}❌${NC} $1"
}

check_root() {
    if [[ $EUID -eq 0 ]]; then
        print_error "This script should not be run as root. Use sudo when prompted."
        exit 1
    fi
}

check_appimage() {
    APPIMAGE_PATH="$SCRIPT_DIR/dist/$APP_NAME-linux.AppImage"
    if [[ ! -f "$APPIMAGE_PATH" ]]; then
        print_error "AppImage not found at: $APPIMAGE_PATH"
        echo "Please build the application first:"
        echo "  cd $SCRIPT_DIR"
        echo "  python3 packaging/build_linux.py"
        exit 1
    fi
    echo "$APPIMAGE_PATH"
}

install_system_wide() {
    local appimage_path="$1"
    
    echo "Installing MKV Manager system-wide..."
    
    # Create installation directory
    sudo mkdir -p "$INSTALL_DIR"
    
    # Copy AppImage to installation directory
    sudo cp "$appimage_path" "$INSTALL_DIR/$APP_NAME"
    sudo chmod +x "$INSTALL_DIR/$APP_NAME"
    print_status "Copied executable to $INSTALL_DIR"
    
    # Create symbolic link in PATH
    sudo ln -sf "$INSTALL_DIR/$APP_NAME" "$BIN_LINK"
    print_status "Created symbolic link in $BIN_LINK"
    
    # Install icon
    if [[ -f "$SCRIPT_DIR/assets/icon.png" ]]; then
        sudo mkdir -p "$ICON_DIR"
        sudo cp "$SCRIPT_DIR/assets/icon.png" "$ICON_FILE"
        print_status "Installed icon"
    else
        print_warning "Icon not found, using generic icon"
    fi
    
    # Create desktop entry
    sudo tee "$DESKTOP_FILE" > /dev/null << EOF
[Desktop Entry]
Name=MKV Manager
Comment=Professional MKV file processing tool
Exec=$APP_NAME
Icon=$APP_NAME
Terminal=false
Type=Application
Categories=AudioVideo;Video;
StartupNotify=true
Keywords=mkv;video;subtitle;processing;
EOF
    
    print_status "Created desktop entry"
    
    # Update desktop database
    if command -v update-desktop-database >/dev/null 2>&1; then
        sudo update-desktop-database /usr/share/applications/
        print_status "Updated desktop database"
    fi
    
    # Update icon cache
    if command -v gtk-update-icon-cache >/dev/null 2>&1; then
        sudo gtk-update-icon-cache -f -t /usr/share/icons/hicolor/
        print_status "Updated icon cache"
    fi
}

install_user_local() {
    local appimage_path="$1"
    local user_bin="$HOME/.local/bin"
    local user_desktop="$HOME/.local/share/applications"
    local user_icon="$HOME/.local/share/icons/hicolor/256x256/apps"
    
    echo "Installing MKV Manager for current user..."
    
    # Create directories
    mkdir -p "$user_bin" "$user_desktop" "$user_icon"
    
    # Copy AppImage
    cp "$appimage_path" "$user_bin/$APP_NAME"
    chmod +x "$user_bin/$APP_NAME"
    print_status "Copied executable to $user_bin"
    
    # Install icon
    if [[ -f "$SCRIPT_DIR/assets/icon.png" ]]; then
        cp "$SCRIPT_DIR/assets/icon.png" "$user_icon/$APP_NAME.png"
        print_status "Installed icon"
    fi
    
    # Create desktop entry
    cat > "$user_desktop/$APP_NAME.desktop" << EOF
[Desktop Entry]
Name=MKV Manager
Comment=Professional MKV file processing tool
Exec=$user_bin/$APP_NAME
Icon=$APP_NAME
Terminal=false
Type=Application
Categories=AudioVideo;Video;
StartupNotify=true
Keywords=mkv;video;subtitle;processing;
EOF
    
    print_status "Created desktop entry"
    
    # Update desktop database
    if command -v update-desktop-database >/dev/null 2>&1; then
        update-desktop-database "$user_desktop"
        print_status "Updated desktop database"
    fi
    
    # Check if ~/.local/bin is in PATH
    if [[ ":$PATH:" != *":$user_bin:"* ]]; then
        print_warning "~/.local/bin is not in your PATH"
        echo "Add this to your ~/.bashrc or ~/.profile:"
        echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
    fi
}

uninstall() {
    echo "Uninstalling MKV Manager..."
    
    # Remove system-wide installation
    if [[ -f "$INSTALL_DIR/$APP_NAME" ]]; then
        sudo rm -f "$INSTALL_DIR/$APP_NAME"
        sudo rmdir "$INSTALL_DIR" 2>/dev/null || true
        print_status "Removed system installation"
    fi
    
    if [[ -L "$BIN_LINK" ]]; then
        sudo rm -f "$BIN_LINK"
        print_status "Removed symbolic link"
    fi
    
    if [[ -f "$DESKTOP_FILE" ]]; then
        sudo rm -f "$DESKTOP_FILE"
        print_status "Removed system desktop entry"
    fi
    
    if [[ -f "$ICON_FILE" ]]; then
        sudo rm -f "$ICON_FILE"
        print_status "Removed system icon"
    fi
    
    # Remove user installation
    local user_bin="$HOME/.local/bin/$APP_NAME"
    local user_desktop="$HOME/.local/share/applications/$APP_NAME.desktop"
    local user_icon="$HOME/.local/share/icons/hicolor/256x256/apps/$APP_NAME.png"
    
    [[ -f "$user_bin" ]] && rm -f "$user_bin" && print_status "Removed user executable"
    [[ -f "$user_desktop" ]] && rm -f "$user_desktop" && print_status "Removed user desktop entry"
    [[ -f "$user_icon" ]] && rm -f "$user_icon" && print_status "Removed user icon"
    
    # Update caches
    if command -v update-desktop-database >/dev/null 2>&1; then
        sudo update-desktop-database /usr/share/applications/ 2>/dev/null || true
        update-desktop-database "$HOME/.local/share/applications" 2>/dev/null || true
    fi
    
    if command -v gtk-update-icon-cache >/dev/null 2>&1; then
        sudo gtk-update-icon-cache -f -t /usr/share/icons/hicolor/ 2>/dev/null || true
    fi
    
    echo "MKV Manager has been uninstalled."
}

show_usage() {
    echo "MKV Manager Installation Script"
    echo
    echo "Usage: $0 [OPTION]"
    echo
    echo "Options:"
    echo "  --system     Install system-wide (requires sudo)"
    echo "  --user       Install for current user only"
    echo "  --uninstall  Remove installation"
    echo "  --help       Show this help message"
    echo
    echo "If no option is provided, you will be prompted to choose."
}

main() {
    check_root
    
    case "${1:-}" in
        --system)
            appimage_path=$(check_appimage)
            install_system_wide "$appimage_path"
            ;;
        --user)
            appimage_path=$(check_appimage)
            install_user_local "$appimage_path"
            ;;
        --uninstall)
            uninstall
            ;;
        --help)
            show_usage
            ;;
        "")
            appimage_path=$(check_appimage)
            echo "MKV Manager Installation"
            echo "========================"
            echo
            echo "Choose installation type:"
            echo "1) System-wide (all users, requires sudo)"
            echo "2) User-only (current user, no sudo required)"
            echo "3) Cancel"
            echo
            read -p "Enter choice [1-3]: " choice
            
            case $choice in
                1)
                    install_system_wide "$appimage_path"
                    ;;
                2)
                    install_user_local "$appimage_path"
                    ;;
                3)
                    echo "Installation cancelled."
                    exit 0
                    ;;
                *)
                    print_error "Invalid choice"
                    exit 1
                    ;;
            esac
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
    
    echo
    print_status "Installation completed!"
    echo "You can now:"
    echo "  • Find 'MKV Manager' in your application menu"
    echo "  • Run 'mkv-manager' from the command line"
    echo "  • The application is independent of this source directory"
}

main "$@"
