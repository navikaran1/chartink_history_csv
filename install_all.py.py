import subprocess
import sys

def install_requirements():
    requirements = [
        "pandas",
        "openpyxl",
        "playwright",
        "requests"
    ]

    print("\n✅ Installing Python packages...\n")
    for package in requirements:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def install_playwright_browsers():
    print("\n✅ Installing Playwright browsers (Chromium, Firefox, WebKit)...\n")
    subprocess.check_call([sys.executable, "-m", "playwright", "install"])

if __name__ == "__main__":
    try:
        install_requirements()
        install_playwright_browsers()
        print("\n🎉 All packages and Playwright browsers installed successfully!")
    except Exception as e:
        print(f"\n❌ Error occurred: {e}")
