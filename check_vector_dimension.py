
import asyncio

from sqlalchemy import text

from app.database.session import engine


async def main():
    query = text("""
        SELECT
            column_name,
            format_type(a.atttypid, a.atttypmod) AS data_type
        FROM information_schema.columns c
        JOIN pg_attribute a
            ON a.attname = c.column_name
        JOIN pg_class t
            ON t.oid = a.attrelid
        JOIN pg_namespace n
            ON n.oid = t.relnamespace
        WHERE c.table_schema = 'public'
          AND c.table_name = 'document_chunks'
          AND c.column_name = 'embedding'
          AND t.relname = c.table_name
          AND n.nspname = c.table_schema;
    """)

    try:
        async with engine.connect() as connection:
            result = await connection.execute(query)
            row = result.fetchone()

            if row:
                print("Column:", row.column_name)
                print("Database vector type:", row.data_type)
            else:
                print("Embedding column not found.")

    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
