#!/usr/bin/env python3
"""
Test Legacy Database Connection
Simple script to verify the current database connection and show table structure.
"""

import asyncio
import asyncpg
import os
import sys
from typing import List, Dict

async def test_legacy_connection():
    """Test connection to legacy database and show table structure"""
    
    # Database configuration - using docker-compose settings
    db_config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': int(os.getenv('DB_PORT', '5433')),  # Docker maps to 5433
        'database': os.getenv('DB_NAME', 'saas_factory'),  # Matches docker-compose
        'user': os.getenv('DB_USER', 'postgres'),  # Matches docker-compose
        'password': os.getenv('DB_PASSWORD', 'postgres')  # Matches docker-compose
    }
    
    print("🔍 Testing Legacy Database Connection...")
    print(f"Host: {db_config['host']}:{db_config['port']}")
    print(f"Database: {db_config['database']}")
    print(f"User: {db_config['user']}")
    print("-" * 50)
    
    try:
        # Connect to database
        conn = await asyncpg.connect(
            host=db_config['host'],
            port=db_config['port'],
            database=db_config['database'],
            user=db_config['user'],
            password=db_config['password']
        )
        
        print("✅ Successfully connected to database!")
        
        # Get table list
        tables_query = """
        SELECT table_name, table_type
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_type = 'BASE TABLE'
        ORDER BY table_name
        """
        
        tables = await conn.fetch(tables_query)
        
        print(f"\n📊 Found {len(tables)} tables:")
        print("-" * 50)
        
        for table in tables:
            table_name = table['table_name']
            
            # Get record count
            try:
                count_query = f"SELECT COUNT(*) FROM {table_name}"
                count = await conn.fetchval(count_query)
                print(f"  {table_name}: {count:,} records")
            except Exception as e:
                print(f"  {table_name}: Error getting count - {e}")
        
        # Get foreign key constraints
        fk_query = """
        SELECT 
            tc.table_name,
            kcu.column_name,
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name
        FROM information_schema.table_constraints AS tc
        JOIN information_schema.key_column_usage AS kcu
            ON tc.constraint_name = kcu.constraint_name
        JOIN information_schema.constraint_column_usage AS ccu
            ON ccu.constraint_name = tc.constraint_name
        WHERE tc.constraint_type = 'FOREIGN KEY'
        ORDER BY tc.table_name, kcu.column_name
        """
        
        fks = await conn.fetch(fk_query)
        
        print(f"\n🔗 Found {len(fks)} foreign key constraints:")
        print("-" * 50)
        
        for fk in fks:
            print(f"  {fk['table_name']}.{fk['column_name']} -> {fk['foreign_table_name']}.{fk['foreign_column_name']}")
        
        # Test some sample queries
        print(f"\n🧪 Testing Sample Queries:")
        print("-" * 50)
        
        sample_queries = [
            ("Users Count", "SELECT COUNT(*) FROM users"),
            ("Tenants Count", "SELECT COUNT(*) FROM tenants"),
            ("Ideas Count", "SELECT COUNT(*) FROM ideas"),
            ("Active Users", "SELECT COUNT(*) FROM users WHERE status = 'active'")
        ]
        
        for query_name, query in sample_queries:
            try:
                result = await conn.fetchval(query)
                print(f"  {query_name}: {result:,}")
            except Exception as e:
                print(f"  {query_name}: Error - {e}")
        
        await conn.close()
        print(f"\n✅ Database connection test completed successfully!")
        
    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")
        print("\n🔧 Troubleshooting tips:")
        print("  1. Check if the database is running")
        print("  2. Verify environment variables are set correctly")
        print("  3. Check database credentials")
        print("  4. Ensure database exists")
        sys.exit(1)

async def main():
    """Main function"""
    await test_legacy_connection()

if __name__ == "__main__":
    asyncio.run(main())
