from __future__ import annotations
import hashlib
import sqlite3
import os
def hash_password(password: str, salt: bytes | None = None) -> tuple[str, str]:
    if salt is None:
        salt = os.urandom(16)

    pwd_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        100_000,
    )
    return salt.hex(), pwd_hash.hex()
conn = sqlite3.connect("pitcha.db")
crs = conn.cursor()

crs.execute(
    """
CREATE TABLE IF NOT EXISTS user_information (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_name TEXT UNIQUE,
    user_password_hash TEXT,
    user_salt TEXT,
    user_email TEXT UNIQUE
)
"""
)
conn.commit()

# Schema migration: add missing columns if they don't exist
try:
    crs.execute("PRAGMA table_info(user_information)")
    columns = {row[1] for row in crs.fetchall()}
    
    if "user_password_hash" not in columns:
        crs.execute("ALTER TABLE user_information ADD COLUMN user_password_hash TEXT")
        conn.commit()
    
    if "user_salt" not in columns:
        crs.execute("ALTER TABLE user_information ADD COLUMN user_salt TEXT")
        conn.commit()
except sqlite3.Error:
    pass
def add_user(name: str, password: str, email: str) -> bool:
    salt, pwd_hash = hash_password(password)
    try:
        crs.execute(
            """
            INSERT INTO user_information
            (user_name, user_password_hash, user_salt, user_email)
            VALUES (?, ?, ?, ?)
            """,
            (name, pwd_hash, salt, email),
        )
        conn.commit()
        return True
    except sqlite3.Error as err:
        print("SQLite Error:", err)
        return False
def load_user(email: str, password: str):
    crs.execute(
        """
        SELECT user_id, user_name, user_password_hash, user_salt
        FROM user_information
        WHERE user_email=?
        LIMIT 1
        """,
        (email,),
    )
    row = crs.fetchone()

    if row is None:
        return None

    user_id, user_name, stored_hash, salt_hex = row
    
    # Handle old users without salt (migrate them)
    if salt_hex is None or stored_hash is None:
        # Regenerate password hash with new salt and update record
        salt, pwd_hash = hash_password(password)
        try:
            crs.execute(
                """
                UPDATE user_information
                SET user_password_hash = ?, user_salt = ?
                WHERE user_id = ?
                """,
                (pwd_hash, salt, user_id),
            )
            conn.commit()
            return user_id
        except sqlite3.Error:
            return None
    
    _, check_hash = hash_password(password, bytes.fromhex(salt_hex))

    if check_hash != stored_hash:
        return None

    return user_id
