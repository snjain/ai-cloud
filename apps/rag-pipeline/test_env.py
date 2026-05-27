import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path.cwd()
while env_path.name != "ai-cloud" and env_path.parent != env_path:
    env_path = env_path.parent

print(f"CWD: {Path.cwd()}")
print(f"env_path: {env_path}")
print(f".env exists: {(env_path / '.env').exists()}")

load_dotenv(env_path / ".env")

print(f"SUPABASE_URL after load: {os.getenv('SUPABASE_URL', 'NOT SET')[:50]}")
print(f"SUPABASE_SERVICE_KEY after load: {os.getenv('SUPABASE_SERVICE_KEY', 'NOT SET')[:50]}")
