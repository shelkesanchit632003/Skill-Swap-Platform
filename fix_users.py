import sqlite3
from werkzeug.security import generate_password_hash

# Connect to database
conn = sqlite3.connect('skillswap.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Unban the user
cursor.execute('UPDATE users SET is_banned = 0 WHERE username = ?', ('Sanchit6303',))

# Create a test user with known password
test_password = 'testpass123'
test_password_hash = generate_password_hash(test_password)

cursor.execute('''
    INSERT INTO users (username, email, password_hash, name, is_public)
    VALUES (?, ?, ?, ?, ?)
''', ('testuser', 'test@example.com', test_password_hash, 'Test User', 1))

conn.commit()

print("✅ Fixed issues:")
print("1. Unbanned user 'Sanchit6303'")
print("2. Created test user:")
print("   Username: testuser")
print("   Password: testpass123")
print("   Email: test@example.com")

# Show all users now
print("\n=== UPDATED USER LIST ===")
users = cursor.execute('SELECT * FROM users').fetchall()
for user in users:
    banned_status = "BANNED" if user['is_banned'] else "ACTIVE"
    admin_status = "ADMIN" if user['is_admin'] else "USER"
    print(f"• {user['username']} ({user['name']}) - {admin_status} - {banned_status}")

conn.close()
