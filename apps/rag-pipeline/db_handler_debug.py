import os
print(f"[DB] SUPABASE_URL: {os.getenv('SUPABASE_URL', 'NOT SET')[:50]}")
print(f"[DB] SUPABASE_SERVICE_KEY: {os.getenv('SUPABASE_SERVICE_KEY', 'NOT SET')[:50]}")
