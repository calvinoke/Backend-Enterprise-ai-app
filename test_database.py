
import asyncio

from sqlalchemy import text

from app.database.session import engine


async def main():
    confirmation = input(
        "This permanently deletes all tables and data in "
        "'enterprise_ai'. Type RESET enterprise_ai to continue: "
    )

    if confirmation != "RESET enterprise_ai":
        print("Cancelled. No database changes were made.")
        await engine.dispose()
        return

    try:
        async with engine.begin() as connection:
            # Remove all objects in the public schema, including
            # the old Alembic version table and existing tables.
            await connection.execute(
                text("DROP SCHEMA public CASCADE")
            )

            await connection.execute(
                text("CREATE SCHEMA public")
            )

            # Reinstall pgvector for the new RAG schema.
            await connection.execute(
                text("CREATE EXTENSION IF NOT EXISTS vector")
            )

            await connection.execute(
                text("GRANT ALL ON SCHEMA public TO postgres")
            )

            await connection.execute(
                text("GRANT ALL ON SCHEMA public TO public")
            )

        print("SUCCESS: public schema reset.")
        print("SUCCESS: pgvector extension is available.")
        print("Next: generate a new Alembic baseline.")

    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
