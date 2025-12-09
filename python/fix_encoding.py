
import os

env_path = r'c:\Users\sid\台大\114-1\生物機電工程概論\期末專題程式碼\python\.env'

# Try reading with different encodings
content = ""
# utf-8-sig handles UTF-8 with BOM (PowerShell sometimes does this)
# utf-16-le is PowerShell 'Unicode' default
encodings = ['utf-8', 'utf-8-sig', 'utf-16-le', 'cp950', 'big5', 'latin1']

for encoding in encodings:
    try:
        print(f"Trying encoding: {encoding}...")
        with open(env_path, 'r', encoding=encoding) as f:
            content = f.read()
            print(f"Successfully read with {encoding}")
            break
    except Exception as e:
        print(f"Failed with {encoding}: {e}")
        continue

if content:
    # Remove any potential NULL bytes if read effectively from UTF-16 as bytes
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Successfully converted .env to UTF-8")
else:
    print("FATAL: Failed to read .env file with all checked encodings")
