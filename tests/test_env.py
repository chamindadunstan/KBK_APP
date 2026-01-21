# test_env.py

import os
from pathlib import Path
from dotenv import load_dotenv

# -------------------------
# Load .env file
# -------------------------
ENV_PATH = Path(__file__).resolve().parents[1] / ".env"

if not ENV_PATH.exists():
    print("[ERROR] .env file not found at:", ENV_PATH)
    exit(1)

load_dotenv(ENV_PATH)

# -------------------------
# Required environment variables
# -------------------------
REQUIRED_VARS = [
    "APP_NAME",
    "APP_ENV",
    "DEBUG",
    "DEFAULT_THEME",
    "DEFAULT_LANGUAGE",
    "DEFAULT_FONT_SIZE",
    "DEFAULT_COLOR_MODE",
    "PROJECT_ROOT",
    "TEST_PROJECT",
    "VSCODE_PATH",
    "PYTHON_PATH"
]

# -------------------------
# Test logic
# -------------------------
missing = []
empty = []

for var in REQUIRED_VARS:
    value = os.getenv(var)

    if value is None:
        missing.append(var)
    elif value.strip() == "":
        empty.append(var)

# -------------------------
# Output results
# -------------------------
print("\n=== ENVIRONMENT VARIABLE TEST ===")

if missing:
    print("\n[FAILED] Missing variables:")
    for var in missing:
        print(f"  - {var}")

if empty:
    print("\n[WARNING] Variables defined but empty:")
    for var in empty:
        print(f"  - {var}")

if not missing and not empty:
    print("\n[SUCCESS] All environment variables are present and valid.")

print("\nTest completed.\n")
