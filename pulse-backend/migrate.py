import asyncio
import asyncpg
import os
from dotenv import load_dotenv
import socket

load_dotenv()

async def main():
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        print("DATABASE_URL not found")
        return
    
    # Replace host with IPv6
    db_url = db_url.replace("db.mqivykdignpqiotcobqf.supabase.co", "[2406:da14:271:9921:5888:5bbd:9391:8ca]")
    
    with open('schema.sql', 'r') as f:
        schema = f.read()

    print("Connecting to db...")
    try:
        conn = await asyncpg.connect(db_url)
        print("Executing schema...")
        await conn.execute(schema)
        print("Done")
        await conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
