#!/usr/bin/env python3
"""
Database verification script to check if the database tables match our expected schema.
Run this after running alembic upgrade head to verify the migration worked correctly.
"""

import asyncio
import asyncpg
import sys
import os

async def verify_database_schema():
    """Verify that the database schema matches our expectations"""
    print("🔍 Verifying database schema...")
    
    try:
        # Connect to the database - Use environment variable to avoid hardcoding
        database_url = os.getenv(
            'DATABASE_URL',
            'postgresql://orchestration:orchestration@postgres-orchestration:5432/orchestration'
        )
        conn = await asyncpg.connect(database_url)
        
        # Check if workflow_events table exists with correct columns
        workflow_events_query = """
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns 
        WHERE table_name = 'workflow_events'
        ORDER BY ordinal_position;
        """
        
        workflow_events_cols = await conn.fetch(workflow_events_query)
        if not workflow_events_cols:
            print("❌ workflow_events table not found!")
            return False
        
        print("✅ workflow_events table found with columns:")
        for col in workflow_events_cols:
            print(f"   - {col['column_name']}: {col['data_type']} ({'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL'})")
        
        # Check if execution_snapshots table exists
        snapshots_query = """
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns 
        WHERE table_name = 'execution_snapshots'
        ORDER BY ordinal_position;
        """
        
        snapshots_cols = await conn.fetch(snapshots_query)
        if not snapshots_cols:
            print("❌ execution_snapshots table not found!")
            return False
        
        print("\n✅ execution_snapshots table found with columns:")
        for col in snapshots_cols:
            print(f"   - {col['column_name']}: {col['data_type']} ({'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL'})")
        
        # Check if alembic_version table exists
        alembic_query = """
        SELECT version_num FROM alembic_version;
        """
        
        try:
            alembic_version = await conn.fetchval(alembic_query)
            print(f"\n✅ Alembic version table found. Current version: {alembic_version}")
        except:
            print("\n❌ Alembic version table not found!")
            return False
        
        # Check indexes
        indexes_query = """
        SELECT indexname, tablename
        FROM pg_indexes 
        WHERE tablename IN ('workflow_events', 'execution_snapshots')
        ORDER BY tablename, indexname;
        """
        
        indexes = await conn.fetch(indexes_query)
        print(f"\n✅ Found {len(indexes)} indexes:")
        for idx in indexes:
            print(f"   - {idx['tablename']}.{idx['indexname']}")
        
        await conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database connection or query failed: {e}")
        return False

async def main():
    print("🚀 Verifying database schema for orchestration service...\n")
    
    success = await verify_database_schema()
    
    if success:
        print("\n🎉 Database schema verification passed!")
        print("💡 The database is ready for the orchestration service.")
        return 0
    else:
        print("\n💥 Database schema verification failed!")
        print("💡 Try running: docker compose exec orchestration-service alembic upgrade head")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
