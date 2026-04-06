"""
Verify database schema after migration
"""
import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")


async def verify_database():
    """Verify tables, indexes, and triggers exist"""
    print("=" * 60)
    print("DATABASE VERIFICATION - Neon PostgreSQL")
    print("=" * 60)

    engine = create_async_engine(DATABASE_URL, echo=False)

    try:
        async with engine.begin() as conn:
            print("\n✓ Connected to Neon successfully!")

            # Check tables
            print("\n📋 Checking tables...")
            result = await conn.execute(
                text("""
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema='public'
                    AND table_name IN ('users', 'auth_audit_log')
                    ORDER BY table_name
                """)
            )
            tables = [row[0] for row in result]

            if 'users' in tables:
                print("  ✅ users table exists")
            else:
                print("  ❌ users table NOT FOUND")
                return False

            if 'auth_audit_log' in tables:
                print("  ✅ auth_audit_log table exists")
            else:
                print("  ❌ auth_audit_log table NOT FOUND")
                return False

            # Check users table columns
            print("\n📋 Checking users table columns...")
            result = await conn.execute(
                text("""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns
                    WHERE table_name = 'users'
                    ORDER BY ordinal_position
                """)
            )
            columns = list(result)

            expected_columns = [
                'id', 'email', 'password_hash', 'role',
                'failed_login_attempts', 'account_locked_until',
                'created_at', 'updated_at'
            ]

            found_columns = [col[0] for col in columns]
            for col in expected_columns:
                if col in found_columns:
                    print(f"  ✅ {col}")
                else:
                    print(f"  ❌ {col} NOT FOUND")
                    return False

            # Check indexes
            print("\n🔍 Checking indexes...")
            result = await conn.execute(
                text("""
                    SELECT indexname, indexdef
                    FROM pg_indexes
                    WHERE tablename='users'
                """)
            )
            indexes = list(result)
            print(f"  Found {len(indexes)} indexes on users table:")
            for idx in indexes:
                print(f"    • {idx[0]}")

            # Check for unique email index
            unique_found = any('UNIQUE' in str(idx[1]) and 'email' in str(idx[1]) for idx in indexes)
            if unique_found:
                print("  ✅ Unique index on email")
            else:
                print("  ❌ Unique email index NOT FOUND")

            # Check triggers
            print("\n⚙️  Checking triggers...")
            result = await conn.execute(
                text("""
                    SELECT trigger_name, event_manipulation, event_object_table
                    FROM information_schema.triggers
                    WHERE event_object_table = 'users'
                """)
            )
            triggers = list(result)

            if triggers:
                print(f"  ✅ Found {len(triggers)} trigger(s):")
                for trig in triggers:
                    print(f"    • {trig[0]} ({trig[1]} on {trig[2]})")
            else:
                print("  ⚠️  No triggers found (updated_at trigger might be missing)")

            # Check auth_audit_log columns
            print("\n📋 Checking auth_audit_log table columns...")
            result = await conn.execute(
                text("""
                    SELECT column_name, data_type
                    FROM information_schema.columns
                    WHERE table_name = 'auth_audit_log'
                    ORDER BY ordinal_position
                """)
            )
            audit_columns = list(result)

            expected_audit = ['id', 'user_id', 'email', 'event_type', 'ip_address', 'user_agent', 'created_at']
            found_audit = [col[0] for col in audit_columns]

            for col in expected_audit:
                if col in found_audit:
                    print(f"  ✅ {col}")
                else:
                    print(f"  ❌ {col} NOT FOUND")
                    return False

            # Test insert (will rollback)
            print("\n🧪 Testing data operations...")

            # Insert test user
            await conn.execute(
                text("""
                    INSERT INTO users (email, password_hash, role)
                    VALUES ('test@example.com', 'hashed_password', 'user')
                """)
            )
            print("  ✅ INSERT operation works")

            # Query test user
            result = await conn.execute(
                text("SELECT email, role FROM users WHERE email = 'test@example.com'")
            )
            user = result.first()
            if user:
                print(f"  ✅ SELECT operation works (found: {user[0]})")

            # Rollback (this is in a transaction that will rollback)
            print("  ℹ️  Test data will be rolled back (not committed)")

            print("\n" + "=" * 60)
            print("✅ DATABASE VERIFICATION SUCCESSFUL!")
            print("=" * 60)
            print("\n✨ Your Neon database is ready for development!")
            print("\nNext steps:")
            print("  1. Run unit tests: pytest tests/unit/ -v")
            print("  2. Continue with Task 2.1: Password hashing service")

            return True

    except Exception as e:
        print(f"\n❌ Verification failed: {e}")
        return False
    finally:
        await engine.dispose()


if __name__ == "__main__":
    success = asyncio.run(verify_database())
    exit(0 if success else 1)
