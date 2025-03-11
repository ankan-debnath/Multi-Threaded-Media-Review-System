import  sqlite3
from rich.console import Console

console = Console()

def get_all_media(conn):
    conn.execute('PRAGMA foreign_keys = ON;')
    c = conn.cursor()
    c.execute(
        '''CREATE TABLE IF NOT EXISTS MEDIAS(
            media_id INTEGER PRIMARY KEY AUTOINCREMENT,
            media_type TEXT,
            media_name TEXT
        )'''
    )
    c.execute("SELECT * FROM MEDIAS")
    conn.commit()
    return c.fetchall()

def add_review(user_name, media_id, rating, comment, conn):
    try:
        conn.execute('PRAGMA foreign_keys = ON;')
        c = conn.cursor()
        c.execute(
            '''CREATE TABLE IF NOT EXISTS REVIEWS(
                user_name TEXT,
                media_id INTEGER,
                rating REAL,
                comment TEXT,
                FOREIGN KEY (media_id) REFERENCES MEDIAS(media_id)
                FOREIGN KEY (user_name) REFERENCES USERS(user_name)
            )'''
        )
        c.execute('''INSERT INTO REVIEWS VALUES(?, ?, ?, ?)''', (user_name, media_id, rating, comment))
        conn.commit()
        console.print(f"[green]Review added by \nUser : {user_name}\nMedia : {media_id}, Rating : {rating},\nComment : {comment}[/green]", style='cyan')

    except sqlite3.IntegrityError:
        console.print(f"[red]Error:[/red] media_id or user_name is invalid ",)

def create_user(user_name, conn):
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS USERS(
            user_name TEXT UNIQUE
        )
    ''')
    try:
        c.execute('''INSERT INTO USERS(user_name) VALUES(?)''', (user_name,))
        console.print(f"[green]User created with user_name : {user_name}[/green]", style='cyan')
    except sqlite3.IntegrityError:
        console.print(f"[red]Error:[/red] Same user_name already exists : {user_name}",)

def get_reviews_by_title(title, conn):
    conn.execute('PRAGMA foreign_keys = ON;')
    c = conn.cursor()
    c.execute(
        '''CREATE TABLE IF NOT EXISTS MEDIAS(
            media_id INTEGER PRIMARY KEY AUTOINCREMENT,
            media_type TEXT,
            media_name TEXT
        )'''
    )
    c.execute(
        '''CREATE TABLE IF NOT EXISTS REVIEWS(
            user_name TEXT,
            media_id INTEGER,
            rating REAL,
            comment TEXT,
            FOREIGN KEY (media_id) REFERENCES MEDIAS(media_id)
            FOREIGN KEY (user_name) REFERENCES USERS(user_name)
        )'''
    )
    c.execute('''
            SELECT R.user_name, R.rating, R.comment
            FROM MEDIAS AS M JOIN REVIEWS AS R
            ON M.media_id = R.media_id
            WHERE LOWER(M.media_name) = LOWER(?)
        ''', (title,))
    conn.commit()
    return c.fetchall()

def get_top_rated_media(category, conn):
    conn.execute('PRAGMA foreign_keys = ON;')
    c = conn.cursor()
    c.execute(
        '''CREATE TABLE IF NOT EXISTS MEDIAS(
            media_id INTEGER PRIMARY KEY AUTOINCREMENT,
            media_type TEXT,
            media_name TEXT
        )'''
    )
    c.execute(
        '''CREATE TABLE IF NOT EXISTS REVIEWS(
            user_name TEXT,
            media_id INTEGER,
            rating REAL,
            comment TEXT,
            FOREIGN KEY (media_id) REFERENCES MEDIAS(media_id)
            FOREIGN KEY (user_name) REFERENCES USERS(user_name)
        )'''
    )
    c.execute('''
                SELECT M.media_name, AVG(R.rating) as avg_rating
                FROM MEDIAS AS M JOIN REVIEWS AS R
                ON M.media_id = R.media_id
                WHERE M.media_type = ?
                GROUP BY M.media_name
                ORDER BY avg_rating DESC
            ''', (category,))
    conn.commit()
    return c.fetchall()

def add_media(user_name, media_type, media_name, conn):
        conn.execute('PRAGMA foreign_keys = ON;')
        c = conn.cursor()
        c.execute(
            '''CREATE TABLE IF NOT EXISTS MEDIAS(
                media_id INTEGER PRIMARY KEY AUTOINCREMENT,
                media_type TEXT,
                media_name TEXT,
                user_name TEXT,
                FOREIGN KEY (user_name) REFERENCES USERS(user_name)
            )'''
        )
        c.execute('''INSERT INTO MEDIAS(media_type, media_name, user_name) VALUES(?, ?, ?)''', (media_type, media_name, user_name))
        conn.commit()