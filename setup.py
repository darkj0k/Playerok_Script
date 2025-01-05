import subprocess

subprocess.run(["pip","install", "-r", "requirements.txt"])
subprocess.run(["pyinstaller", "--onefile", "main.py"])
print("Successfully build script.")