import os
import json
import aiosqlite
from pathlib import Path
from config import USE_TURSO, TURSO_URL, TURSO_TOKEN

try:
    import certifi
    os.environ.setdefault("SSL_CERT_FILE", certifi.where())
    os.environ.setdefault("REQUESTS_CA_BUNDLE", certifi.where())
except ImportError:
    pass

DB_PATH = Path(__file__).parent / "portfolio.db"

if USE_TURSO:
    from libsql_client import create_client

    async def get_db():
        client = create_client(url=TURSO_URL, auth_token=TURSO_TOKEN)
        return client

    async def _execute(sql, params=None):
        client = await get_db()
        try:
            return await client.execute(sql, params or ())
        finally:
            await client.close()

    async def _fetchall(sql, params=None):
        rs = await _execute(sql, params)
        return [dict(zip(rs.columns, row)) for row in rs.rows]

    async def _fetchone(sql, params=None):
        rs = await _execute(sql, params)
        if rs.rows:
            return dict(zip(rs.columns, rs.rows[0]))
        return None

    async def _execute_insert(sql, params=None):
        rs = await _execute(sql, params)
        return rs.last_insert_rowid if hasattr(rs, 'last_insert_rowid') else None

    async def init_db():
        ddl = """
            CREATE TABLE IF NOT EXISTS hero (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                name TEXT NOT NULL,
                subtitle TEXT DEFAULT '',
                description TEXT DEFAULT ''
            );
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                tech TEXT NOT NULL,
                description TEXT DEFAULT '',
                features TEXT DEFAULT '[]',
                icon TEXT DEFAULT '',
                sort_order INTEGER DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS skills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                level INTEGER DEFAULT 0,
                icon TEXT DEFAULT '',
                sort_order INTEGER DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS contact (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                email TEXT DEFAULT '',
                github TEXT DEFAULT '',
                linkedin TEXT DEFAULT ''
            );
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            );
        """
        for stmt in ddl.split(";"):
            s = stmt.strip()
            if s:
                await _execute(s)

else:
    async def get_db():
        db = await aiosqlite.connect(str(DB_PATH))
        db.row_factory = aiosqlite.Row
        await db.execute("PRAGMA journal_mode=WAL")
        await db.execute("PRAGMA foreign_keys=ON")
        return db

    async def _fetchall(sql, params=None):
        db = await get_db()
        try:
            cursor = await db.execute(sql, params or ())
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]
        finally:
            await db.close()

    async def _fetchone(sql, params=None):
        db = await get_db()
        try:
            cursor = await db.execute(sql, params or ())
            row = await cursor.fetchone()
            return dict(row) if row else None
        finally:
            await db.close()

    async def _execute(sql, params=None):
        db = await get_db()
        try:
            cursor = await db.execute(sql, params or ())
            await db.commit()
            return cursor
        finally:
            await db.close()

    async def init_db():
        db = await get_db()
        try:
            await db.executescript("""
                CREATE TABLE IF NOT EXISTS hero (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    name TEXT NOT NULL,
                    subtitle TEXT DEFAULT '',
                    description TEXT DEFAULT ''
                );
                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    tech TEXT NOT NULL,
                    description TEXT DEFAULT '',
                    features TEXT DEFAULT '[]',
                    icon TEXT DEFAULT '',
                    sort_order INTEGER DEFAULT 0
                );
                CREATE TABLE IF NOT EXISTS skills (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    level INTEGER DEFAULT 0,
                    icon TEXT DEFAULT '',
                    sort_order INTEGER DEFAULT 0
                );
                CREATE TABLE IF NOT EXISTS contact (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    email TEXT DEFAULT '',
                    github TEXT DEFAULT '',
                    linkedin TEXT DEFAULT ''
                );
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL
                );
            """)
            await db.commit()
        finally:
            await db.close()

async def get_hero():
    row = await _fetchone("SELECT * FROM hero WHERE id = 1")
    return row or {"id": 1, "name": "", "subtitle": "", "description": ""}

async def update_hero(name: str, subtitle: str, description: str):
    sql = """
        INSERT INTO hero (id, name, subtitle, description)
        VALUES (1, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET name=excluded.name, subtitle=excluded.subtitle, description=excluded.description
    """
    await _execute(sql, (name, subtitle, description))

async def get_projects():
    rows = await _fetchall("SELECT * FROM projects ORDER BY sort_order")
    for r in rows:
        r["features"] = json.loads(r["features"])
    return rows

async def create_project(title: str, tech: str, description: str, features: list, icon: str):
    sql = "INSERT INTO projects (title, tech, description, features, icon) VALUES (?, ?, ?, ?, ?)"
    await _execute(sql, (title, tech, description, json.dumps(features), icon))

async def update_project(project_id: int, title: str, tech: str, description: str, features: list, icon: str):
    sql = "UPDATE projects SET title=?, tech=?, description=?, features=?, icon=? WHERE id=?"
    await _execute(sql, (title, tech, description, json.dumps(features), icon, project_id))

async def delete_project(project_id: int):
    await _execute("DELETE FROM projects WHERE id=?", (project_id,))

async def get_skills():
    return await _fetchall("SELECT * FROM skills ORDER BY sort_order")

async def create_skill(name: str, level: int, icon: str):
    await _execute("INSERT INTO skills (name, level, icon) VALUES (?, ?, ?)", (name, level, icon))

async def update_skill(skill_id: int, name: str, level: int, icon: str):
    await _execute("UPDATE skills SET name=?, level=?, icon=? WHERE id=?", (name, level, icon, skill_id))

async def delete_skill(skill_id: int):
    await _execute("DELETE FROM skills WHERE id=?", (skill_id,))

async def get_contact():
    row = await _fetchone("SELECT * FROM contact WHERE id = 1")
    return row or {"id": 1, "email": "", "github": "", "linkedin": ""}

async def update_contact(email: str, github: str, linkedin: str):
    sql = """
        INSERT INTO contact (id, email, github, linkedin)
        VALUES (1, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET email=excluded.email, github=excluded.github, linkedin=excluded.linkedin
    """
    await _execute(sql, (email, github, linkedin))

async def get_user(username: str):
    return await _fetchone("SELECT * FROM users WHERE username=?", (username,))
