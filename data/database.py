import sqlite3
from typing import Optional, List, Tuple
from config.config import load_db_settings, DataBaseSettings
from logs.logger import logger

db_set: DataBaseSettings = load_db_settings()

class DataBase:
    def __init__(self, db_file: str = db_set.path):
        self.db_file = db_file
        self.create_tables()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_file)
        return conn

    def create_tables(self):
        queries = [
            '''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                is_subscriber INTEGER DEFAULT 0,
                is_admin INTEGER DEFAULT 0
            )
            ''',

            '''
            CREATE TABLE IF NOT EXISTS groups (
                group_id INTEGER PRIMARY KEY,
                title TEXT,
                last_post_id INTEGER DEFAULT 0,
                is_active INTEGER DEFAULT 1,
                source VARCHAR(10)
            )
            '''
        ]
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                for query in queries:
                    cursor.execute(query)
                conn.commit()
            logger.info('Таблицы созданы')
        except sqlite3.Error as e:
            logger.error(f'Ошибка при создании таблиц: {e}')

    def execute_query(self, query: str, params: tuple) -> None:
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
        except sqlite3.Error as e:
            logger.error(f'Ошибка выполнения запроса "{query}": {e}')

    def fetch_one(self, query: str, params: tuple) -> Optional[Tuple]:
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                return cursor.fetchone()
        except sqlite3.Error as e:
            logger.error(f'Ошибка чтения данных "{query}": {e}')
            return None

    def fetch_all(self, query: str, params: tuple) -> List[Tuple]:
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                return cursor.fetchall()
        except sqlite3.Error as e:
            logger.error(f'Ошибка чтения списка "{query}": {e}')
            return []

#=============таблица users===========================

    def reg_user(
        self,
        user_id: int,
        username: str | None,
        is_subscriber: int = 0,
        is_admin: int = 0
    ) -> None:
        self.execute_query(
            "INSERT OR REPLACE INTO users VALUES (?, ?, ?, ?)",
            (user_id, username, is_subscriber, is_admin)
        )

    def add_sub(self, user_id: int) -> None:
        self.execute_query(
            'UPDATE users SET is_subscriber = 1 WHERE user_id = ?',
            (user_id,)
        )

    def del_sub(self, user_id: int) -> None:
        self.execute_query(
            'UPDATE users SET is_subscriber = 0 WHERE user_id = ?',
            (user_id,)
        )

    def add_admin(self, user_id: int) -> None:
        self.execute_query(
            'UPDATE users SET is_admin = 1 WHERE user_id = ?',
            (user_id,)
        )

    def del_admin(self, user_id: int) -> None:
        self.execute_query(
            'UPDATE users SET is_admin = 0 WHERE user_id = ?',
            (user_id,)
        )

    def get_all_subs_ids(self) -> List[int]:
        results = self.fetch_all(
            'SELECT user_id FROM users WHERE is_subscriber = 1',
            ()
        )
        return [row[0] for row in results]

    def get_all_admins(self):
        results = self.fetch_all(
            'SELECT user_id FROM users WHERE is_admin = ?',
            (1,)
        )
        return [row[0] for row in results]

    def check_is_admin(self, user_id: int) -> bool:
        result = self.fetch_one(
            'SELECT is_admin FROM users WHERE user_id = ?',
            (user_id,)
        )
        if result is None:
            return False
        return bool(result[0])

#==============таблица groups=======================

    def reg_group(self, group_id: int, title: str, source: str) -> None:
        self.execute_query(
            "INSERT OR REPLACE INTO groups (group_id, title, last_post_id, is_active, source) "
            "VALUES (?, ?, 0, 1, ?)",
            (group_id, title, source)
        )

    def delete_group(self, group_id: int, source: str) -> None:
        self.execute_query(
            'DELETE FROM groups WHERE group_id = ? AND source = ?',
            (group_id, source)
        )

    def set_last_post_id(self, group_id: int, last_post_id: int) -> None:
        self.execute_query(
            "UPDATE groups SET last_post_id = ? WHERE group_id = ?",
            (last_post_id, group_id)
        )

    def get_last_post_id(self, group_id: int) -> int:
        result = self.fetch_one(
            "SELECT last_post_id FROM groups WHERE group_id = ?",
            (group_id,)
        )
        if result:
            return result[0]
        return 0

    def set_group_not_active(self, group_id: int) -> None:
        self.execute_query(
            "UPDATE groups SET is_active = 0 WHERE group_id = ?",
            (group_id,)
        )

    def set_group_active(self, group_id: int) -> None:
        self.execute_query(
            "UPDATE groups SET is_active = 1 WHERE group_id = ?",
            (group_id,)
        )

    def get_all_group_ids(self) -> List[Tuple[int, int]]:
        results = self.fetch_all(
            "SELECT group_id, last_post_id FROM groups WHERE is_active = 1",
            ()
        )
        return results

    def get_all_active_groups(self) -> List[dict]:
        results = self.fetch_all(
            "SELECT group_id, title FROM groups WHERE is_active = 1",
            ()
        )
        return [{"group_id": row[0], "title": row[1]} for row in results]

    def group_exists(self, group_id: int, source: str) -> bool:
        result = self.fetch_one(
            'SELECT 1 FROM groups WHERE group_id = ? AND source = ?',
            (group_id, source)
        )
        return result is not None


db = DataBase(db_set.path)