import sqlite3
from logger import logger
from config import ADMIN_ID, ADMIN_CONTACT


class Users:
    unknown_user_alias = '!unknown_user!'

    def __init__(self, db_path: str):
        self.db_file = db_path
        try:
            self._check_table_presence()
            self.add_user(ADMIN_ID, ADMIN_CONTACT)
            logger.debug("Database instance created", action={'action': 'db'})
        except Exception as error:
            logger.critical(f'User database init crashed. App stopped. Error:{error}')

    def _check_table_presence(self):
        """Create new table if not exist in DB"""
        sql_create_table = """CREATE TABLE if not exists users (
        record INTEGER NOT NULL UNIQUE, 
        telegram_id TEXT NOT NULL UNIQUE, 
        alias TEXT NOT NULL, 
        access_level INTEGER NOT NULL DEFAULT 1, 
        PRIMARY KEY(record AUTOINCREMENT));"""
        with sqlite3.Connection(self.db_file) as con:
            cur = con.cursor()
            cur.execute(sql_create_table)
        logger.debug('Database table checked', action={'action': 'db'})

    def check_id(self, user_id: str) -> bool:
        """Check user in list and access permision"""
        with sqlite3.Connection(self.db_file) as con:
            cur = con.cursor()
            cur.execute('SELECT access_level FROM users WHERE telegram_id=(?)', [user_id])
            res = cur.fetchone()
        if bool(res):
            logger.debug(f'User ID {user_id} checked, access={bool(res)}', action={'action': 'db'})
        else:
            logger.warning(f'User ID {user_id} checked, access={bool(res)}', action={'action': 'db'})
        return bool(res)

    def get_alias(self, user_id: str) -> str:
        """Get user name by Telegram ID"""
        with sqlite3.Connection(self.db_file) as con:
            cur = con.cursor()
            cur.execute('SELECT alias FROM users WHERE telegram_id=(?)', [user_id])
            res = cur.fetchone()
        return res[0] if res else self.unknown_user_alias

    def add_user(self, user_id, user_alias, user_level=1) -> None:
        """Add new user (or unblock exist, sets 1 access level)"""
        add_command = """INSERT OR REPLACE INTO users (telegram_id, alias, access_level) VALUES (?, ?, ?);"""
        with sqlite3.Connection(self.db_file) as con:
            cur = con.cursor()
            cur.execute(add_command, [user_id, user_alias, user_level])
        logger.debug(f'Admin added user {user_alias} ({user_id})', action={'action': 'db'})

    def block_user(self, user_id) -> None:
        """Set 0 access level for user"""
        alias = self.get_alias(user_id)
        if alias != self.unknown_user_alias:
            block_command = """INSERT OR REPLACE INTO users (telegram_id, alias, access_level) VALUES (?, ?, 0);"""
            with sqlite3.Connection(self.db_file) as con:
                cur = con.cursor()
                cur.execute(block_command, [user_id, alias])
            logger.debug(f'Admin blocked user {alias} ({user_id})', action={'action': 'db'})

    def get_users(self) -> str:
        """Get users list in string format"""
        with sqlite3.Connection(self.db_file) as con:
            cur = con.cursor()
            cur.execute('SELECT telegram_id, alias, access_level FROM users')
            user_list_res = cur.fetchall()
            user_list_str = ''
            for row in user_list_res:
                row_str = ''
                for pos, element in enumerate(row):
                    if pos == 0:
                        row_str += f'🆔:{element} '
                    if pos == 1:
                        row_str += f'👨:{element} '
                    if pos == 2:
                        access = bool(int(element))
                        symb = '✅' if access is True else '🚧'
                        row_str += f' {symb}'
                user_list_str += row_str + '\n'
            logger.debug('Concated user list', action={'action': 'db'})
            return user_list_str


