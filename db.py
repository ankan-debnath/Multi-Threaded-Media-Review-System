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
            media_name TEXT UNIQUE,
            user_name TEXT,
            FOREIGN KEY (user_name) REFERENCES USERS(user_name)
        )'''
    )
    c.execute("SELECT * FROM MEDIAS ORDER BY media_type, media_name")
    conn.commit()
    return c.fetchall()

def add_review_with_media_id(user_name, media_id, rating, comment, conn):
    conn.execute('PRAGMA foreign_keys = ON;')
    c = conn.cursor()
    c.execute('''
            CREATE TABLE IF NOT EXISTS USERS(
                user_name TEXT UNIQUE
            )
        ''')
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

def add_review_with_media_name(user_name, media_name, rating, comment, conn):
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
    c.execute(
        '''CREATE TABLE IF NOT EXISTS MEDIAS(
            media_id INTEGER PRIMARY KEY AUTOINCREMENT,
            media_type TEXT,
            media_name TEXT UNIQUE,
            user_name TEXT,
            FOREIGN KEY (user_name) REFERENCES USERS(user_name)
        )'''
    )

    c.execute('''SELECT media_id FROM MEDIAS WHERE LOWER(media_name) = LOWER(?)''', (media_name,))

    media = c.fetchall()
    media_id = media[0][0] if media else None

    if not media_id:
        raise sqlite3.OperationalError("No such media available")

    c.execute("INSERT INTO REVIEWS VALUES(?, ?, ?, ?)", (user_name, media_id, rating, comment))
    conn.commit()
    console.print(f"[green]Review added by \nUser : {user_name}\nMedia : {media_id}, Rating : {rating},\nComment : {comment}[/green]", style='cyan')

    return media_id

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

def get_recommendations_from_review_data(user_name, media_type, conn):
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
    c.execute(
        '''CREATE TABLE IF NOT EXISTS MEDIAS(
            media_id INTEGER PRIMARY KEY AUTOINCREMENT,
            media_type TEXT,
            media_name TEXT UNIQUE,
            user_name TEXT,
            FOREIGN KEY (user_name) REFERENCES USERS(user_name)
        )'''
    )

    #Getting recommendations from review data
    query = '''
        SELECT m1.media_id, m1.media_name, m1.media_type, m2.avg_rating, "From reviews"
        FROM MEDIAS m1 JOIN (
            SELECT media_id, ROUND(AVG(rating), 2) as avg_rating
            FROM REVIEWS
            WHERE user_name IN (
                SELECT DISTINCT user_name
                from REVIEWS
                WHERE media_id in (
                    SELECT DISTINCT(media_id) FROM REVIEWS WHERE user_name = ?  and rating >= 3
                ) and user_name != ?
            ) 
            and media_id not in ( SELECT DISTINCT(media_id) FROM REVIEWS WHERE user_name = ?  and rating >= 3)  
            and rating >= 3
            GROUP BY media_id
        ) m2
        ON m1.media_id = m2.media_id
        WHERE m1.user_name != ? 
    '''

    # print(c.execute('''SELECT media_id, ROUND(AVG(rating), 2) as avg_rating
    #         FROM REVIEWS
    #         WHERE user_name IN (
    #             SELECT DISTINCT user_name
    #             from REVIEWS
    #             WHERE media_id in (
    #                 SELECT DISTINCT(media_id) FROM REVIEWS WHERE user_name = ?  and rating >= 3
    #             ) and user_name != ?
    #         ) and rating >= 3.5
    #         GROUP BY media_id
    #         ORDER BY RANDOM()
    #         LIMIT 10''', (user_name, user_name)).fetchall())

    params = [user_name, user_name, user_name, user_name]

    if media_type:
        query += "and m1.media_type = ? "
        params.append(media_type)

    query += " ORDER BY RANDOM() LIMIT 5"

    c.execute(query, params)
    recommendations = c.fetchall()

    conn.commit()
    return recommendations

def get_recommendations_from_subscriber_data(user_name, media_type, conn):
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
    c.execute(
        '''CREATE TABLE IF NOT EXISTS MEDIAS(
            media_id INTEGER PRIMARY KEY AUTOINCREMENT,
            media_type TEXT,
            media_name TEXT UNIQUE,
            user_name TEXT,
            FOREIGN KEY (user_name) REFERENCES USERS(user_name)
        )'''
    )

    query = '''
        SELECT m1.media_id, m1.media_name, m1.media_type, m2.avg_rating, "From subscription data"
        FROM MEDIAS as m1 JOIN (
            SELECT media_id, ROUND(AVG(rating), 2) as avg_rating
            FROM REVIEWS
            WHERE user_name in (
                SELECT DISTINCT user_name
                FROM SUBSCRIBERS
                WHERE media_id in (
                    SELECT media_id
                    FROM SUBSCRIBERS
                    WHERE user_name = ?
                )
                and user_name != ?
            )
            and media_id not in ( SELECT DISTINCT(media_id) FROM REVIEWS WHERE user_name = ?  and rating >= 3)  
            and media_id not in ( SELECT media_id FROM SUBSCRIBERS WHERE user_name = ? )
            and rating >= 3
            GROUP BY media_id
        ) as m2
        ON m1.media_id = m2.media_id
        WHERE m1.user_name != ?
    '''

    params = [user_name, user_name, user_name, user_name, user_name]

    if media_type:
        query += "and m1.media_type = ?"
        params.append(media_type)

    query += " ORDER BY RANDOM() LIMIT 5"

    c.execute(query, params)
    recommendations = c.fetchall()

    # print(c.execute('''SELECT media_id, ROUND(AVG(rating), 2) as avg_rating
    #         FROM REVIEWS
    #         WHERE user_name in (
    #             SELECT DISTINCT user_name
    #             FROM SUBSCRIBERS
    #             WHERE media_id in (
    #                 SELECT media_id
    #                 FROM SUBSCRIBERS
    #                 WHERE user_name = ?
    #             )
    #             and user_name != ?
    #         )
    #         and media_id not in ( SELECT DISTINCT(media_id) FROM REVIEWS WHERE user_name = ?  and rating >= 3)
    #         and media_id not in ( SELECT media_id FROM SUBSCRIBERS WHERE user_name = ? )
    #         and rating >= 3.5
    #         GROUP BY media_id''', (user_name, user_name, user_name, user_name)).fetchall())

    print(user_name)
    conn.commit()
    return recommendations

def get_reviews_by_title(title, conn):
    conn.execute('PRAGMA foreign_keys = ON;')
    c = conn.cursor()
    c.execute(
        '''CREATE TABLE IF NOT EXISTS MEDIAS(
            media_id INTEGER PRIMARY KEY AUTOINCREMENT,
            media_type TEXT,
            media_name TEXT UNIQUE,
            user_name TEXT,
            FOREIGN KEY (user_name) REFERENCES USERS(user_name)
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
            media_name TEXT UNIQUE,
            user_name TEXT,
            FOREIGN KEY (user_name) REFERENCES USERS(user_name)
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
                SELECT M.media_name, ROUND(AVG(R.rating), 2) as avg_rating
                FROM MEDIAS AS M JOIN REVIEWS AS R
                ON M.media_id = R.media_id
                WHERE M.media_type = ?
                GROUP BY M.media_name
                ORDER BY avg_rating DESC
                LIMIT 5
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
                media_name TEXT UNIQUE,
                user_name TEXT,
                FOREIGN KEY (user_name) REFERENCES USERS(user_name)
            )'''
        )
        c.execute('''INSERT INTO MEDIAS(media_type, media_name, user_name) VALUES(?, ?, ?)''', (media_type, media_name, user_name))
        conn.commit()