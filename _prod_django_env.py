import os

print("Generating /etc/django.env with environment variables...   ", end="")
with open("/etc/django.env", "w") as env_file:
    env_file.write(f"DJANGO_SETTINGS_MODULE={os.getenv('DJANGO_SETTINGS_MODULE', 'django_project.settings')}\n")
    env_file.write(f"DEBUG={os.getenv('DEBUG', '0')}\n")
    env_file.write(f"ALLOWED_HOSTS={os.getenv('ALLOWED_HOSTS', '*')}\n")
    env_file.write(f"MEDIA_ROOT={os.getenv('MEDIA_ROOT', '/var/www/grow/media')}\n")
    env_file.write(f"STATIC_ROOT={os.getenv('STATIC_ROOT', '/var/www/grow/static')}\n")
    env_file.write(f"GROW_DB={os.getenv('GROW_DB', 'sqlite:////data/db.sqlite3')}\n")

print("[DONE]")
