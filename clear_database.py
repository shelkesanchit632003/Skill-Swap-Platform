#!/usr/bin/env python3
"""
Script to clear all data from the SQLite database while preserving table structure.
"""

import sqlite3
import os

def clear_database():
    """Clear all data from the database"""
    try:
        # Connect to database
        conn = sqlite3.connect('skillswap.db')
        cursor = conn.cursor()
        
        # Get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print('Tables found:', [table[0] for table in tables])
        
        # Disable foreign key constraints temporarily
        cursor.execute('PRAGMA foreign_keys = OFF')
        
        # Clear all tables
        cleared_tables = []
        for table in tables:
            table_name = table[0]
            if table_name != 'sqlite_sequence':  # Skip sqlite internal table
                cursor.execute(f'DELETE FROM {table_name}')
                cleared_tables.append(table_name)
                print(f'✓ Cleared table: {table_name}')
        
        # Reset auto-increment sequences
        cursor.execute('DELETE FROM sqlite_sequence')
        print('✓ Reset auto-increment sequences')
        
        # Re-enable foreign key constraints
        cursor.execute('PRAGMA foreign_keys = ON')
        
        # Commit changes
        conn.commit()
        conn.close()
        
        print('\n🎉 All data cleared successfully!')
        print(f'📊 Cleared {len(cleared_tables)} tables')
        print('🏗️  Database structure preserved')
        print('\nCleared tables:')
        for table in cleared_tables:
            print(f'  - {table}')
            
    except Exception as e:
        print(f'❌ Error clearing database: {e}')
        return False
    
    return True

if __name__ == '__main__':
    print('🧹 Clearing SQLite database...\n')
    success = clear_database()
    
    if success:
        print('\n✨ Database is now clean and ready for fresh data!')
    else:
        print('\n💥 Failed to clear database. Check the error above.')
