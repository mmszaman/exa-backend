import asyncio
import asyncpg

async def check_tables():
    # Connect using asyncpg directly with SSL disabled for local check
    conn = await asyncpg.connect(
        'postgresql://neondb_owner:npg_mIqbMEV8TuG0@ep-super-mud-adzd7g4h-pooler.c-2.us-east-1.aws.neon.tech/exadb',
        ssl='require'
    )
    
    # Check tables
    tables = await conn.fetch(
        "SELECT table_name FROM information_schema.tables "
        "WHERE table_schema = 'public' ORDER BY table_name"
    )
    print('\n✓ Tables in database:')
    for t in tables:
        print(f'  • {t["table_name"]}')
    
    # Check columns for our new tables
    for table in ['users', 'sessions', 'tenants']:
        columns = await conn.fetch(
            f"SELECT column_name, data_type FROM information_schema.columns "
            f"WHERE table_name = '{table}' ORDER BY ordinal_position"
        )
        if columns:
            print(f'\n✓ {table.upper()} table has {len(columns)} columns:')
            for col in columns[:5]:  # Show first 5 columns
                print(f'  • {col["column_name"]} ({col["data_type"]})')
            if len(columns) > 5:
                print(f'  ... and {len(columns) - 5} more columns')
    
    await conn.close()

asyncio.run(check_tables())

