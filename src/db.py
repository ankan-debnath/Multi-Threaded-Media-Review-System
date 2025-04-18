import  sqlite3
from rich.console import Console

console = Console()

def get_all_media(conn, lock):
    with lock:
        conn.execute('PRAGMA foreign_keys = ON;')
        c = conn.cursor()
        c.execute("SELECT * FROM MEDIAS ORDER BY media_type, media_name")
        conn.commit()
    return c.fetchall()

def add_review_with_media_id(user_name, media_id, rating, comment, conn, lock):
    with lock:
        conn.execute('PRAGMA foreign_keys = ON;')
        c = conn.cursor()
        c.execute('''INSERT INTO REVIEWS VALUES(?, ?, ?, ?)''', (user_name, media_id, rating, comment))
        conn.commit()

def add_review_with_media_name(user_name, media_name, rating, comment, conn, lock):
    with lock:
        conn.execute('PRAGMA foreign_keys = ON;')
        c = conn.cursor()

        c.execute('''SELECT media_id FROM MEDIAS WHERE LOWER(media_name) = LOWER(?)''', (media_name,))

        media = c.fetchall()
        media_id = media[0][0] if media else None

        if not media_id:
            raise sqlite3.OperationalError("No such media available")

        c.execute("INSERT INTO REVIEWS VALUES(?, ?, ?, ?)", (user_name, media_id, rating, comment))
        conn.commit()
        console.print(f"[green]Review added by \nUser : {user_name}\nMedia : {media_id}, Rating : {rating},\nComment : {comment}[/green]", style='cyan')

    return media_id

def create_user(user_name, conn, lock):
    with lock:
        c = conn.cursor()
        c.execute('''INSERT INTO USERS(user_name) VALUES(?)''', (user_name,))
        conn.commit()

def get_recommendations_from_review_data(user_name, media_type, conn, lock):
    with lock:
        conn.execute('PRAGMA foreign_keys = ON;')
        c = conn.cursor()

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

        params = [user_name, user_name, user_name, user_name]

        if media_type:
            query += "and m1.media_type = ? "
            params.append(media_type)

        query += " ORDER BY RANDOM() LIMIT 5"

        c.execute(query, params)
        recommendations = c.fetchall()

        conn.commit()
    return recommendations

def get_recommendations_from_subscriber_data(user_name, media_type, conn, lock):
    with lock:
        conn.execute('PRAGMA foreign_keys = ON;')
        c = conn.cursor()

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

        conn.commit()
    return recommendations

def get_reviews_by_title(title, conn, lock):
    with lock:
        conn.execute('PRAGMA foreign_keys = ON;')
        c = conn.cursor()
        c.execute('''
                SELECT R.user_name, R.rating, R.comment
                FROM MEDIAS AS M JOIN REVIEWS AS R
                ON M.media_id = R.media_id
                WHERE LOWER(M.media_name) = LOWER(?)
            ''', (title,))
        conn.commit()
    return c.fetchall()

def get_top_rated_media(category, conn, lock):
    with lock:
        conn.execute('PRAGMA foreign_keys = ON;')
        c = conn.cursor()
        c.execute('''
                    SELECT M.media_id, M.media_name, M.media_type, ROUND(AVG(R.rating), 2) as avg_rating
                    FROM MEDIAS AS M JOIN REVIEWS AS R
                    ON M.media_id = R.media_id
                    WHERE M.media_type = ?
                    GROUP BY M.media_name
                    ORDER BY avg_rating DESC
                    LIMIT 5
                ''', (category,))
        conn.commit()
    return c.fetchall()

def add_media(user_name, media_type, media_name, conn, lock):
    with lock:
        conn.execute('PRAGMA foreign_keys = ON;')
        c = conn.cursor()
        c.execute('''INSERT INTO MEDIAS(media_type, media_name, user_name) VALUES(?, ?, ?)''', (media_type, media_name, user_name))
        conn.commit()

def get_all_subscribers(media_id, conn, lock):
    with lock:
        c = conn.cursor()

        c.execute('''SELECT user_name FROM SUBSCRIBERS WHERE media_id = ?''', (media_id,))
        subscribers = c.fetchall()
        conn.commit()
    return subscribers

def get_medias(media_id, conn, lock):
    with lock:
        c = conn.cursor()
        c.execute('''SELECT media_type, media_name FROM MEDIAS WHERE media_id = ?''', (media_id,))
        media = c.fetchall()
        conn.commit()
    return media

def subscribe_to_media(user_name, media_id, conn, lock):
    with lock:
        conn.execute('PRAGMA foreign_keys = ON;')
        c = conn.cursor()

        c.execute("INSERT INTO SUBSCRIBERS VALUES(?, ?)", (media_id, user_name))

def unsubscribe(user_name, media_id, conn, lock):
    c = conn.cursor()
    with lock:
        c.execute("DELETE FROM SUBSCRIBERS WHERE user_name = ? AND media_id = ?", (user_name, media_id))
        conn.commit()

def get_media_type(media_id, conn, lock):
    with lock:
        conn.execute('PRAGMA foreign_keys = ON;')
        c = conn.cursor()

        c.execute("SELECT media_type from MEDIAS WHERE media_id = ? ", (media_id,))

        media_type = c.fetchall()[0][0]
        conn.commit()
    return media_type

def is_available(user_name, conn, lock):
    with lock:
        conn.execute('PRAGMA foreign_keys = ON;')
        c = conn.cursor()
        c.execute("SELECT user_name FROM USERS WHERE user_name = ?", (user_name,))
        user_name = c.fetchall()
        conn.commit()
    return user_name

def is_subscribed(user_name, media_id, conn, lock):
    with lock:
        conn.execute('PRAGMA foreign_keys = ON;')
        c = conn.cursor()

        c.execute("SELECT user_name, media_id FROM SUBSCRIBERS WHERE user_name = ? and media_id = ? ", (user_name, media_id))
        sub_data = c.fetchall()
        conn.commit()
    return sub_data

def is_media_available(media_cred, conn, lock):
    with lock:
        conn.execute('PRAGMA foreign_keys = ON;')
        c = conn.cursor()

        if media_cred.isdigit():
            c.execute("SELECT media_id from MEDIAS WHERE media_id = ? ", (media_cred,))
        else:
            c.execute("SELECT media_id from MEDIAS WHERE LOWER(media_name) = LOWER(?)", (media_cred,))

        result = c.fetchall()
        conn.commit()

    return result[0][0] if result else None

def get_media_name(media_id, conn, lock):
    with lock:
        c = conn.cursor()
        c.execute("SELECT media_name from MEDIAS WHERE media_id = ?", (media_id,))
        c.commit()
    result = c.fetchall()
    return result[0][0] if result else None


def create_all_db_tables(conn, lock):
    with lock:
        c = conn.cursor()

        # Media Table
        c.execute(
            '''CREATE TABLE IF NOT EXISTS MEDIAS(
                media_id INTEGER PRIMARY KEY AUTOINCREMENT,
                media_type TEXT,
                media_name TEXT UNIQUE,
                user_name TEXT,
                FOREIGN KEY (user_name) REFERENCES USERS(user_name)
            )'''
        )

        # User Table
        c.execute('''
                    CREATE TABLE IF NOT EXISTS USERS(
                        user_name TEXT UNIQUE
                    )
                ''')

        # Reviews Table
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

        # Subscriber Table
        c.execute(
            '''CREATE TABLE IF NOT EXISTS SUBSCRIBERS(
                media_id INTEGER,
                user_name TEXT,
                FOREIGN KEY (media_id) REFERENCES MEDIAS(media_id),
                FOREIGN KEY (user_name) REFERENCES USERS(user_name),
                PRIMARY KEY (media_id, user_name)
            )'''
        )



        conn.commit()