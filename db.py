import aiosqlite
from datetime import datetime, timedelta
from config import DB_PATH

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            full_name TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            plan_code TEXT NOT NULL,
            amount INTEGER NOT NULL,
            currency TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            payload TEXT UNIQUE,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            paid_at TEXT
        );
        CREATE TABLE IF NOT EXISTS subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            plan_code TEXT NOT NULL,
            started_at TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            active INTEGER NOT NULL DEFAULT 1
        );
        """)
        await db.commit()

async def upsert_user(user_id, username, full_name):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO users(user_id, username, full_name) VALUES(?,?,?) "
            "ON CONFLICT(user_id) DO UPDATE SET username=excluded.username, full_name=excluded.full_name",
            (user_id, username, full_name),
        )
        await db.commit()

async def create_order(user_id, plan_code, amount, currency, payload):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "INSERT INTO orders(user_id, plan_code, amount, currency, payload) VALUES(?,?,?,?,?)",
            (user_id, plan_code, amount, currency, payload),
        )
        await db.commit()
        return cur.lastrowid

async def get_order_by_payload(payload):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT * FROM orders WHERE payload=?", (payload,))
        return await cur.fetchone()

async def mark_order_paid(payload):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE orders SET status='paid', paid_at=? WHERE payload=? AND status='pending'",
            (datetime.utcnow().isoformat(), payload),
        )
        await db.commit()

async def add_subscription(user_id, plan_code, days):
    now = datetime.utcnow()
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "SELECT expires_at FROM subscriptions WHERE user_id=? AND active=1 ORDER BY expires_at DESC LIMIT 1",
            (user_id,),
        )
        row = await cur.fetchone()
        start = now
        if row:
            try:
                prev = datetime.fromisoformat(row[0])
                if prev > now:
                    start = prev
            except ValueError:
                pass
        expires = start + timedelta(days=days)
        await db.execute(
            "INSERT INTO subscriptions(user_id, plan_code, started_at, expires_at, active) VALUES(?,?,?,?,1)",
            (user_id, plan_code, now.isoformat(), expires.isoformat()),
        )
        await db.commit()
        return expires

async def get_active_subscription(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "SELECT * FROM subscriptions WHERE user_id=? AND active=1 ORDER BY expires_at DESC LIMIT 1",
            (user_id,),
        )
        return await cur.fetchone()

async def stats():
    async with aiosqlite.connect(DB_PATH) as db:
        users = (await (await db.execute("SELECT COUNT(*) FROM users")).fetchone())[0]
        paid = (await (await db.execute("SELECT COUNT(*) FROM orders WHERE status='paid'")).fetchone())[0]
        revenue = (await (await db.execute("SELECT COALESCE(SUM(amount),0) FROM orders WHERE status='paid'")).fetchone())[0]
        active = (await (await db.execute(
            "SELECT COUNT(*) FROM subscriptions WHERE active=1 AND expires_at > ?",
            (datetime.utcnow().isoformat(),),
        )).fetchone())[0]
        return {"users": users, "paid_orders": paid, "revenue": revenue, "active_subs": active}
