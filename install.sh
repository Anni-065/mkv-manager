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

check_existing_installation() {
    local has_system=false
    local has_user=false
    
    if [[ -f "$INSTALL_DIR/$APP_NAME" ]] || [[ -L "$BIN_LINK" ]] || [[ -f "$DESKTOP_FILE" ]]; then
        has_system=true
    fi
    
    local user_bin="$HOME/.local/bin/$APP_NAME"
    local user_desktop="$HOME/.local/share/applications/$APP_NAME.desktop"
    if [[ -f "$user_bin" ]] || [[ -f "$user_desktop" ]]; then
        has_user=true
    fi
    
    if [[ "$has_system" == true ]] || [[ "$has_user" == true ]]; then
        print_warning "Existing MKV Manager installation detected:"
        [[ "$has_system" == true ]] && echo "  • System-wide installation"
        [[ "$has_user" == true ]] && echo "  • User installation"
        echo
        
        local response
        read -p "Remove existing installation before proceeding? [Y/n]: " response
        response=${response:-y}
        
        if [[ "$response" =~ ^[Yy] ]]; then
            echo "Removing existing installation..."
            uninstall_quiet
            print_status "Existing installation removed"
            echo
        else
            print_warning "Continuing with existing installation present"
            echo "This may cause conflicts or leave old files behind"
            echo
        fi
    fi
}

uninstall_quiet() {
    if [[ -f "$INSTALL_DIR/$APP_NAME" ]]; then
        sudo rm -f "$INSTALL_DIR/$APP_NAME" 2>/dev/null || true
        sudo rmdir "$INSTALL_DIR" 2>/dev/null || true
    fi
    
    if [[ -L "$BIN_LINK" ]]; then
        sudo rm -f "$BIN_LINK" 2>/dev/null || true
    fi
    
    if [[ -f "$DESKTOP_FILE" ]]; then
        sudo rm -f "$DESKTOP_FILE" 2>/dev/null || true
    fi
    
    if [[ -f "$ICON_FILE" ]]; then
        sudo rm -f "$ICON_FILE" 2>/dev/null || true
    fi
    
    local user_bin="$HOME/.local/bin/$APP_NAME"
    local user_desktop="$HOME/.local/share/applications/$APP_NAME.desktop"
    local user_icon="$HOME/.local/share/icons/hicolor/256x256/apps/$APP_NAME.png"
    
    [[ -f "$user_bin" ]] && rm -f "$user_bin" 2>/dev/null || true
    [[ -f "$user_desktop" ]] && rm -f "$user_desktop" 2>/dev/null || true
    [[ -f "$user_icon" ]] && rm -f "$user_icon" 2>/dev/null || true
    
    if command -v update-desktop-database >/dev/null 2>&1; then
        sudo update-desktop-database /usr/share/applications/ 2>/dev/null || true
        update-desktop-database "$HOME/.local/share/applications" 2>/dev/null || true
    fi
    
    if command -v gtk-update-icon-cache >/dev/null 2>&1; then
        sudo gtk-update-icon-cache -f -t /usr/share/icons/hicolor/ 2>/dev/null || true
    fi
}

check_appimage() {
    local standalone_path="$SCRIPT_DIR/dist/mkv-manager-linux"
    local appimage_path="$SCRIPT_DIR/dist/mkv-manager-linux.AppImage"
    
    if [[ -f "$standalone_path" ]]; then
        print_status "Found standalone executable" >&2
        echo "$standalone_path"
    elif [[ -f "$appimage_path" ]]; then
        print_warning "Using AppImage (may require FUSE)" >&2
        echo "$appimage_path"
    else
        print_error "Neither standalone executable nor AppImage found"
        echo "Expected locations:"
        echo "  $standalone_path"
        echo "  $appimage_path"
        echo "Please build the application first:"
        echo "  cd $SCRIPT_DIR"
        echo "  python3 packaging/build_linux.py"
        exit 1
    fi
}

install_system_wide() {
    local executable_path="$1"
    
    echo "Installing MKV Manager system-wide..."
    
    sudo mkdir -p "$INSTALL_DIR"
    sudo cp "$executable_path" "$INSTALL_DIR/$APP_NAME"
    sudo chmod +x "$INSTALL_DIR/$APP_NAME"
    print_status "Copied executable to $INSTALL_DIR"
    
    sudo ln -sf "$INSTALL_DIR/$APP_NAME" "$BIN_LINK"
    print_status "Created symbolic link in $BIN_LINK"
    
    if [[ -f "$SCRIPT_DIR/assets/icon.png" ]]; then
        sudo mkdir -p "$ICON_DIR"
        sudo cp "$SCRIPT_DIR/assets/icon.png" "$ICON_FILE"
        print_status "Installed icon"
    else
        print_warning "Icon not found, using generic icon"
    fi
    
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
    
    if command -v update-desktop-database >/dev/null 2>&1; then
        sudo update-desktop-database /usr/share/applications/
        print_status "Updated desktop database"
    fi
    
    if command -v gtk-update-icon-cache >/dev/null 2>&1; then
        sudo gtk-update-icon-cache -f -t /usr/share/icons/hicolor/
        print_status "Updated icon cache"
    fi
}

install_user_local() {
    local executable_path="$1"
    local user_bin="$HOME/.local/bin"
    local user_desktop="$HOME/.local/share/applications"
    local user_icon="$HOME/.local/share/icons/hicolor/256x256/apps"
    
    echo "Installing MKV Manager for current user..."
    
    mkdir -p "$user_bin" "$user_desktop" "$user_icon"
    
    cp "$executable_path" "$user_bin/$APP_NAME"
    chmod +x "$user_bin/$APP_NAME"
    print_status "Copied executable to $user_bin"
    
    if [[ -f "$SCRIPT_DIR/assets/icon.png" ]]; then
        cp "$SCRIPT_DIR/assets/icon.png" "$user_icon/$APP_NAME.png"
        print_status "Installed icon"
    fi
    
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
    
    if command -v update-desktop-database >/dev/null 2>&1; then
        update-desktop-database "$user_desktop"
        print_status "Updated desktop database"
    fi
    
    if [[ ":$PATH:" != *":$user_bin:"* ]]; then
        print_warning "~/.local/bin is not in your PATH"
        echo "Add this to your ~/.bashrc or ~/.profile:"
        echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
    fi
}

uninstall() {
    echo "Uninstalling MKV Manager..."
    
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
    
    local user_bin="$HOME/.local/bin/$APP_NAME"
    local user_desktop="$HOME/.local/share/applications/$APP_NAME.desktop"
    local user_icon="$HOME/.local/share/icons/hicolor/256x256/apps/$APP_NAME.png"
    
    [[ -f "$user_bin" ]] && rm -f "$user_bin" && print_status "Removed user executable"
    [[ -f "$user_desktop" ]] && rm -f "$user_desktop" && print_status "Removed user desktop entry"
    [[ -f "$user_icon" ]] && rm -f "$user_icon" && print_status "Removed user icon"
    
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
    echo "  --force      Skip existing installation check"
    echo "  --help       Show this help message"
    echo
    echo "If no option is provided, you will be prompted to choose."
}

main() {
    check_root
    
    local force_install=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --system)
                executable_path=$(check_appimage)
                [[ "$force_install" == false ]] && check_existing_installation
                install_system_wide "$executable_path"
                return
                ;;
            --user)
                executable_path=$(check_appimage)
                [[ "$force_install" == false ]] && check_existing_installation
                install_user_local "$executable_path"
                return
                ;;
            --uninstall)
                uninstall
                return
                ;;
            --force)
                force_install=true
                shift
                continue
                ;;
            --help)
                show_usage
                return
                ;;
            *)
                print_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
        shift
    done
    
    executable_path=$(check_appimage)
    [[ "$force_install" == false ]] && check_existing_installation
    
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
            echo "Installing MKV Manager system-wide..."
            
            sudo mkdir -p "$INSTALL_DIR"
            
            sudo cp "$executable_path" "$INSTALL_DIR/$APP_NAME"
            sudo chmod +x "$INSTALL_DIR/$APP_NAME"
            print_status "Copied executable to $INSTALL_DIR"
                    sudo ln -sf "$INSTALL_DIR/$APP_NAME" "$BIN_LINK"
                    print_status "Created symbolic link in $BIN_LINK"
                    
                    if [[ -f "$SCRIPT_DIR/assets/icon.png" ]]; then
                        sudo mkdir -p "$ICON_DIR"
                        sudo cp "$SCRIPT_DIR/assets/icon.png" "$ICON_FILE"
                        print_status "Installed icon"
                    else
                        print_warning "Icon not found, using generic icon"
                    fi
                    
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
                    
                    if command -v update-desktop-database >/dev/null 2>&1; then
                        sudo update-desktop-database /usr/share/applications/
                        print_status "Updated desktop database"
                    fi
                    
                    if command -v gtk-update-icon-cache >/dev/null 2>&1; then
                        sudo gtk-update-icon-cache -f -t /usr/share/icons/hicolor/
                        print_status "Updated icon cache"
                    fi
                    ;;
                2)
                    local user_bin="$HOME/.local/bin"
                    local user_desktop="$HOME/.local/share/applications"
                    local user_icon="$HOME/.local/share/icons/hicolor/256x256/apps"
                    
                    echo "Installing MKV Manager for current user..."
                    mkdir -p "$user_bin" "$user_desktop" "$user_icon"
                    cp "$executable_path" "$user_bin/$APP_NAME"
                    chmod +x "$user_bin/$APP_NAME"
                    print_status "Copied executable to $user_bin"
                    
                    if [[ -f "$SCRIPT_DIR/assets/icon.png" ]]; then
                        cp "$SCRIPT_DIR/assets/icon.png" "$user_icon/$APP_NAME.png"
                        print_status "Installed icon"
                    fi
                    
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
                    
                    if command -v update-desktop-database >/dev/null 2>&1; then
                        update-desktop-database "$user_desktop"
                        print_status "Updated desktop database"
                    fi
                    
                    if [[ ":$PATH:" != *":$user_bin:"* ]]; then
                        print_warning "~/.local/bin is not in your PATH"
                        echo "Add this to your ~/.bashrc or ~/.profile:"
                        echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
                    fi
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
    
    echo
    print_status "Installation completed!"
}

main "$@"
