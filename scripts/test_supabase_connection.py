#!/usr/bin/env python3
"""
Test Supabase Connection
This script tests the Supabase connection to verify configuration is correct.
"""

import os
import sys
import asyncio
import asyncpg
from typing import Dict, Optional

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  python-dotenv not installed. Install with: pip install python-dotenv")
    print("   Or ensure environment variables are set manually.")

async def test_supabase_connection():
    """Test connection to Supabase database"""
    
    # Get Supabase configuration from environment
    supabase_config = {
        'host': os.getenv('SUPABASE_DB_HOST'),
        'port': int(os.getenv('SUPABASE_DB_PORT', '5432')),
        'database': os.getenv('SUPABASE_DB_NAME', 'postgres'),
        'user': os.getenv('SUPABASE_DB_USER', 'postgres'),
        'password': os.getenv('SUPABASE_DB_PASSWORD')
    }
    
    print("🔍 Testing Supabase Connection...")
    print(f"Host: {supabase_config['host']}:{supabase_config['port']}")
    print(f"Database: {supabase_config['database']}")
    print(f"User: {supabase_config['user']}")
    print("-" * 50)
    
    # Check if required configuration is present
    missing_vars = []
    for key, value in supabase_config.items():
        if not value:
            missing_vars.append(key.upper())
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("\n🔧 Please run: python scripts/setup_supabase_config.py")
        return False
    
    try:
        # Test connection to Supabase
        conn = await asyncpg.connect(
            host=supabase_config['host'],
            port=supabase_config['port'],
            database=supabase_config['database'],
            user=supabase_config['user'],
            password=supabase_config['password']
        )
        
        print("✅ Successfully connected to Supabase!")
        
        # Test basic database operations
        print("\n🧪 Testing Basic Database Operations:")
        print("-" * 50)
        
        # Get version
        version = await conn.fetchval("SELECT version()")
        print(f"PostgreSQL Version: {version.split()[1]}")
        
        # Get current user
        current_user = await conn.fetchval("SELECT current_user")
        print(f"Current User: {current_user}")
        
        # Get database name
        db_name = await conn.fetchval("SELECT current_database()")
        print(f"Database: {db_name}")
        
        # Get table list
        tables_query = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_type = 'BASE TABLE'
        ORDER BY table_name
        """
        
        tables = await conn.fetch(tables_query)
        print(f"\n📊 Found {len(tables)} tables in Supabase:")
        
        for table in tables[:10]:  # Show first 10 tables
            table_name = table['table_name']
            try:
                count_query = f"SELECT COUNT(*) FROM {table_name}"
                count = await conn.fetchval(count_query)
                print(f"  {table_name}: {count:,} records")
            except Exception as e:
                print(f"  {table_name}: Error getting count - {e}")
        
        if len(tables) > 10:
            print(f"  ... and {len(tables) - 10} more tables")
        
        await conn.close()
        print(f"\n✅ Supabase connection test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Failed to connect to Supabase: {e}")
        print("\n🔧 Troubleshooting tips:")
        print("  1. Check if Supabase project is active")
        print("  2. Verify database credentials in .env file")
        print("  3. Ensure database is accessible from your IP")
        print("  4. Check if database password is correct")
        return False

async def test_supabase_api():
    """Test Supabase API connection (if configured)"""
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_anon_key = os.getenv('SUPABASE_ANON_KEY')
    
    if not supabase_url or not supabase_anon_key:
        print("\n⚠️  Supabase API configuration not found")
        print("   Skipping API connection test")
        return True
    
    print(f"\n🌐 Testing Supabase API Connection...")
    print(f"URL: {supabase_url}")
    print("-" * 50)
    
    try:
        import httpx
        
        # Test basic API connectivity
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{supabase_url}/rest/v1/",
                headers={
                    "apikey": supabase_anon_key,
                    "Authorization": f"Bearer {supabase_anon_key}"
                }
            )
            
            if response.status_code == 200:
                print("✅ Supabase API connection successful")
                return True
            else:
                print(f"⚠️  Supabase API returned status: {response.status_code}")
                return False
                
    except ImportError:
        print("⚠️  httpx not installed, skipping API test")
        print("   Install with: pip install httpx")
        return True
    except Exception as e:
        print(f"❌ Supabase API connection failed: {e}")
        return False

async def main():
    """Main function"""
    print("🚀 Supabase Connection Test")
    print("=" * 50)
    
    # Test database connection
    db_success = await test_supabase_connection()
    
    # Test API connection
    api_success = await test_supabase_api()
    
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    if db_success and api_success:
        print("🎉 All tests passed! Supabase is ready for data integrity verification.")
        print("\n🔄 Next Steps:")
        print("   1. Run full verification: python scripts/data_integrity_verification.py")
        print("   2. Address any drift issues found")
        print("   3. Validate 100% migration completeness")
        sys.exit(0)
    else:
        print("❌ Some tests failed. Please fix the issues before proceeding.")
        print("\n🔧 Recommended actions:")
        if not db_success:
            print("   - Fix database connection issues")
        if not api_success:
            print("   - Fix API connection issues")
        print("   - Re-run this test after fixing issues")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
