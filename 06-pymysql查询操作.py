import pymysql

conn = pymysql.connect(
    host="localhost", port=3306, user="root", password="Yuan13888057275", database="yolo26", charset="utf8"
)

cur = conn.cursor()

# 查询条件sql语法：select * from 表名 where 列名=值
# %s是占位符
sql = "select * from user where username=%s"

cur.execute(sql, args=["cc"])

result = cur.fetchall()

cur.close()
conn.close()

if len(result) > 0:
    print("账号已存在")
else:
    print("账号不存在")
