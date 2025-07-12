import sqlite3
from werkzeug.security import check_password_hash

# Connect to database
conn = sqlite3.connect('skillswap.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Check all users
print("=== ALL USERS ===")
users = cursor.execute('SELECT * FROM users').fetchall()
for user in users:
    print(f"ID: {user['id']}, Username: {user['username']}, Email: {user['email']}")
    print(f"  Name: {user['name']}, Admin: {user['is_admin']}, Banned: {user['is_banned']}")
    print(f"  Password Hash: {user['password_hash'][:50]}...")
    print()

# Test password verification for admin
print("=== TESTING ADMIN LOGIN ===")
admin_user = cursor.execute('SELECT * FROM users WHERE username = ?', ('admin',)).fetchone()
if admin_user:
    test_password = 'admin123'
    is_valid = check_password_hash(admin_user['password_hash'], test_password)
    print(f"Admin password verification for '{test_password}': {is_valid}")

# Test password verification for any other users
print("\n=== TESTING OTHER USER LOGINS ===")
other_users = cursor.execute('SELECT * FROM users WHERE username != ?', ('admin',)).fetchall()
for user in other_users:
    # Try some common passwords that might have been used during testing
    test_passwords = ['password', '123456', 'test', user['username'], 'password123']
    print(f"\nTesting user: {user['username']}")
    for pwd in test_passwords:
        is_valid = check_password_hash(user['password_hash'], pwd)
        if is_valid:
            print(f"  ✓ Password '{pwd}' works!")
            break
    else:
        print(f"  ✗ None of the test passwords work")
        print(f"  Hash: {user['password_hash']}")

conn.close()
