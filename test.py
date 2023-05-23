import sqlite3

conn = sqlite3.connect('online.db')

# conn.execute('''CREATE TABLE products
#          (ID INTEGER PRIMARY KEY AUTOINCREMENT    NOT NULL,
#          NAME           TEXT    NOT NULL,
#          DESC            TEXT     NOT NULL,
#          IMAGE        TEXT,
#          PRICE         TEXT);''')
# conn.execute('''CREATE TABLE users
#          (id INTEGER PRIMARY KEY AUTOINCREMENT    NOT NULL,
#          name           TEXT    NOT NULL,
#          email            TEXT     NOT NULL,
#          password        CHAR(60),
#          address char(120),
#          city text,
#          state text);''')
# conn.execute('''CREATE TABLE bag
#          (id INTEGER PRIMARY KEY AUTOINCREMENT    NOT NULL,
#          user           TEXT    NOT NULL,
#          product           TEXT     NOT NULL);''')
# conn.execute('''CREATE TABLE wishlist
#          (id INTEGER PRIMARY KEY AUTOINCREMENT    NOT NULL,
#          user           TEXT    NOT NULL,
#          product           TEXT     NOT NULL);''')
# conn.execute('''CREATE TABLE orders
#          (id INTEGER PRIMARY KEY AUTOINCREMENT    NOT NULL,
#          name           TEXT    NOT NULL,
#          email  Text,
#          products          char(120)     NOT NULL,
#          address char(120),
#          completed text   );''')
# conn.execute("drop table users")
conn.commit()
conn.close()