#!/usr/bin/env python3
"""
Setup script to install Git hooks for automatic sanitization.
This script installs pre-commit and post-commit hooks that automatically
sanitize files before committing and restore them after committing.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path


def check_git_repo():
    """Check if we're in a Git repository."""
    try:
        result = subprocess.run(['git', 'rev-parse', '--git-dir'],
                                capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False


def get_hooks_dir():
    """Get the Git hooks directory."""
    try:
        result = subprocess.run(['git', 'rev-parse', '--git-dir'],
                                capture_output=True, text=True)
        if result.returncode == 0:
            git_dir = Path(result.stdout.strip())
            return git_dir / 'hooks'
    except FileNotFoundError:
        pass
    return None


def create_hook_script(hook_name, python_script_path, hooks_dir):
    """Create a Git hook script that calls our Python script."""
    hook_path = hooks_dir / \
        hook_name
    python_exe = sys.executable

    hook_content = f'''#!/bin/sh
# Auto-generated Git hook for MKV Manager
"{python_exe}" "{python_script_path}"
'''
    with open(hook_path, 'w', newline='\n', encoding='utf-8') as f:
        f.write(hook_content)

    try:
        # This will be greyed out on Windows (expected behavior)
        if os.name != 'nt':
            os.chmod(hook_path, 0o755)
    except (OSError, AttributeError):
        pass

    return hook_path


def install_hooks():
    """Install the Git hooks."""
    if not check_git_repo():
        print("❌ Error: Not in a Git repository!")
        print("💡 Make sure you're in your project directory and it's a Git repo")
        return False

    hooks_dir = get_hooks_dir()
    if not hooks_dir:
        print("❌ Error: Could not find Git hooks directory!")
        return False

    print(f"📁 Git hooks directory: {hooks_dir}")

    hooks_dir.mkdir(exist_ok=True)

    project_root = Path.cwd()

    hooks_to_install = [
        ('pre-commit', 'pre-commit-hook.py'),
        ('post-commit', 'post-commit-hook.py'),
    ]

    installed_hooks = []

    for hook_name, python_script in hooks_to_install:
        python_script_path = project_root / python_script

        if not python_script_path.exists():
            print(f"❌ Error: {python_script} not found!")
            continue

        hook_path = hooks_dir / hook_name
        if hook_path.exists():
            backup_path = hook_path.with_suffix('.backup')
            shutil.copy2(hook_path, backup_path)
            print(f"📦 Backed up existing {hook_name} hook to {backup_path}")

        try:
            created_hook = create_hook_script(
                hook_name, python_script_path, hooks_dir)
            print(f"✅ Installed {hook_name} hook: {created_hook}")
            installed_hooks.append(hook_name)
        except Exception as e:
            print(f"❌ Error installing {hook_name} hook: {str(e)}")

    if installed_hooks:
        print(f"\n🎉 Successfully installed {len(installed_hooks)} Git hooks!")
        print("\n💡 How it works:")
        print("   • Before each commit: Files are automatically sanitized")
        print("   • After each commit: Original files are restored")
        print("   • Your GitHub repo will never contain personal information")
        print("   • Your working directory keeps your personal settings")

        print(f"\n📋 Installed hooks: {', '.join(installed_hooks)}")
        return True
    else:
        print("❌ No hooks were installed!")
        return False


def uninstall_hooks():
    """Uninstall the Git hooks."""
    hooks_dir = get_hooks_dir()
    if not hooks_dir:
        print("❌ Error: Could not find Git hooks directory!")
        return False

    hooks_to_remove = ['pre-commit', 'post-commit']
    removed_hooks = []

    for hook_name in hooks_to_remove:
        hook_path = hooks_dir / hook_name
        if hook_path.exists():
            try:
                content = None
                for encoding in ['utf-8', 'cp1252', 'latin-1']:
                    try:
                        with open(hook_path, 'r', encoding=encoding) as f:
                            content = f.read()
                        break
                    except UnicodeDecodeError:
                        continue

                if content and 'MKV Manager' in content:
                    hook_path.unlink()
                    print(f"🗑️ Removed {hook_name} hook")
                    removed_hooks.append(hook_name)

                    backup_path = hook_path.with_suffix('.backup')
                    if backup_path.exists():
                        shutil.move(backup_path, hook_path)
                        print(f"📦 Restored backup for {hook_name} hook")
                elif content:
                    print(
                        f"⚠️ {hook_name} hook exists but is not ours, skipping")
                else:
                    print(f"⚠️ Could not read {hook_name} hook file")
            except Exception as e:
                print(f"❌ Error removing {hook_name} hook: {str(e)}")

    if removed_hooks:
        print(f"\n✅ Successfully removed {len(removed_hooks)} Git hooks!")
    else:
        print("ℹ️ No MKV Manager hooks found to remove")

    return True


def test_hooks():
    """Test if the hooks are working properly."""
    project_root = Path.cwd()

    required_files = [
        'sanitize_for_github.py',
        'pre-commit-hook.py',
        'post-commit-hook.py'
    ]

    missing_files = []
    for file_name in required_files:
        if not (project_root / file_name).exists():
            missing_files.append(file_name)

    if missing_files:
        print(f"❌ Missing required files: {', '.join(missing_files)}")
        return False

    try:
        sys.path.insert(0, str(project_root))
        from sanitize_for_github import get_replacements, sanitize_content

        replacements = get_replacements()
        if not replacements:
            print("❌ No replacement patterns found")
            return False

        test_content = str(project_root)
        sanitized = sanitize_content(test_content)

        if sanitized != test_content:
            print("✅ Sanitization function is working")
            print(f"   Test: {test_content} → {sanitized}")
        else:
            print("⚠️ Sanitization function may not be working properly")

        return True

    except Exception as e:
        print(f"❌ Error testing sanitization: {str(e)}")
        return False


def main():
    """Main function with user interaction."""
    print("🎬 MKV Manager - Git Hooks Setup")
    print("=" * 40)

    while True:
        print("\nOptions:")
        print("1. 🔧 Install Git hooks")
        print("2. 🗑️ Uninstall Git hooks")
        print("3. 🧪 Test hooks")
        print("4. ℹ️ Show status")
        print("5. ❌ Exit")

        choice = input("\nEnter your choice (1-5): ").strip()

        if choice == '1':
            install_hooks()

        elif choice == '2':
            uninstall_hooks()

        elif choice == '3':
            if test_hooks():
                print("✅ All tests passed!")
            else:
                print("❌ Some tests failed!")

        elif choice == '4':
            print("\n📊 Status:")
            if check_git_repo():
                print("✅ Git repository detected")
                hooks_dir = get_hooks_dir()
                if hooks_dir:
                    print(f"📁 Hooks directory: {hooks_dir}")

                    hooks_to_check = ['pre-commit', 'post-commit']
                    for hook_name in hooks_to_check:
                        hook_path = hooks_dir / hook_name
                        if hook_path.exists():
                            print(f"✅ {hook_name} hook installed")
                        else:
                            print(f"❌ {hook_name} hook not found")
                else:
                    print("❌ Could not find hooks directory")
            else:
                print("❌ Not in a Git repository")

        elif choice == '5':
            print("👋 Goodbye!")
            break

        else:
            print("❌ Invalid choice. Please enter 1-5.")


if __name__ == "__main__":
    main()
