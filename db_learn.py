import sqlite3
conn = sqlite3.connect('example.db')

c = conn.cursor()

# learn db select
#SELECT COUNT(*) FROM TT
#取前两个 select *from dataTab limit 2
#去从二开始的两个 select * from tt limit 2,2


# Create table 
c.execute('''CREATE TABLE stocks              
    (date text, trans text, symbol text, qty real, price real)''')

# Insert a row of data 
c.execute("INSERT INTO stocks VALUES ('2006-01-05','BUY','RHAT',100,35.14)")

# Save (commit) the changes 
conn.commit()

# We can also close the connection if we are done with it. 
# Just be sure any changes have been committed or they will be lost. 
conn.close()


c.execute("create table catalog (id integer primary key,pid integer,name varchar(10) UNIQUE,nickname text NULL)")
c.execute("drop table catalog")
c.execute("delete from catalog")


# Larger example that inserts many records at a time
purchases = [('2006-03-28', 'BUY', 'IBM', 1000, 45.00),
             ('2006-04-05', 'BUY', 'MSFT', 1000, 72.00),
             ('2006-04-06', 'SELL', 'IBM', 500, 53.00),
            ]
c.executemany('INSERT INTO stocks VALUES (?,?,?,?,?)', purchases)

c.execute("UPDATE catalog SET trans='SELL' WHERE symbol = 'IBM'")


# Never do this -- insecure!
symbol = 'RHAT'
c.execute("SELECT * FROM stocks WHERE symbol = '%s'" % symbol)

# Do this instead
t = ('RHAT',)
c.execute('SELECT * FROM stocks WHERE symbol=?', t)
print(c.fetchone())

t=('RHAT')
c.execute("DELETE * FROM stocks WHERE symbol=?", t)
