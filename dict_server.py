'''
name :Sam
date :2019-08-26
email:karta059488@gmail.com
modules:pymongo
'''
from socket import *
import os
import time
import signal
import pymysql
import sys

# 定義需要的全局變量
DICT_TEXT = './dict.txt'
HOST = '0.0.0.0'
PORT = 8000
ADDR = (HOST, PORT)

# 流程控制


def main():
    # 創建數據庫連接
    db = pymysql.connect('localhost', 'root', 'a123456', 'dict')

    # 創建套接字
    s = socket()
    s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    s.bind(ADDR)
    s.listen(5)

    # 忽略子進程信號  在父進程中忽略子進程狀態改變，子進程自動退出由系統處理
    signal.signal(signal.SIGCHLD, signal.SIG_IGN)

    while True:
        try:
            c, addr = s.accept()
            print("Connect from", addr)
        except KeyboardInterrupt:
            s.close()
            sys.exit("服務器退出")
        except Exception as e:
            print(e)
            continue

        # 沒有產生異常正常情況下創建子進程
        pid = os.fork()
        if pid == 0:
            s.close()
            do_child(c, db)  # 　都需要調用到數據庫
            # sys.exit(0) # 處理完請求退出一次
        else:
            c.close()
            continue


def do_child(c, db):
    # 循環接收客戶端的請求
    while True:
        data = c.recv(128).decode()
        print(c.getpeername(), ":", data)
        if (not data) or data[0] == 'E':
            c.close()
            sys.exit(0)
        elif data[0] == 'R':
            do_register(c, db, data)
        elif data[0] == 'L':
            do_login(c, db, data)  # c跟客戶端連接 db 去數據庫比對 data獲取資料
        elif data[0] == 'Q':
            do_query(c, db, data)
        elif data[0] == 'H':
            do_hist(c, db, data)


def do_login(c, db, data):
    print("登錄操作")
    l = data.split(' ')
    name = l[1]
    passwd = l[2]
    cursor = db.cursor()   # 游標

    sql = "select * from user where name='%s' and passwd='%s'" % (name, passwd)

    cursor.execute(sql)
    r = cursor.fetchone()

    if r == None:
        c.send(b'FALL')
    else:
        print("%s登入成功" % name)
        c.send(b'OK')


def do_register(c, db, data):
    print("註冊操作")
    l = data.split(' ')
    name = l[1]      # R  name passwd
    passwd = l[2]
    cursor = db.cursor()

    sql = "select * from user where name='%s'" % name
    cursor.execute(sql)
    r = cursor.fetchone()

    if r != None:
        c.send(b'EXISTS')  # 如果不為空代表有東西名字相符在資料庫當中
        return
    # 用戶不存在情況下藥插入用戶
    sql = "insert into user (name,passwd) values ('%s','%s')" % (
        name, passwd)
    try:
        cursor.execute(sql)
        db.commit()
        c.send(b'OK')
    except:
        db.rollback()
        c.send(b'FALL')
    else:
        print("%s註冊成功" % name)


def do_query(c, db, data):
    print("查詢操作")
    l = data.split(' ')
    name = l[1]
    word = l[2]
    cursor = db.cursor()

    def insert_history():  # 寫在裡面可以直接使用do_query外部函數變量不用在定義一次
        tm = time.ctime()

        sql = "insert into hist (name,word,time) \
    	values('%s','%s','%s')" % (name, word, tm)
        try:
            cursor.execute(sql)
            db.commit()
        except:
            db.rollback()

    # 透過文本查詢
    try:
        f = open(DICT_TEXT)
    except:
        c.send(b'FALL')
        return

    for line in f:
        tmp = line.split(' ')[0]  # 切割出每行首單詞
        if tmp > word:
            c.send(b'FALL')
            f.close()
            return  # 查不到或查錯的情況下都return回到重查
        elif tmp == word:
            c.send(b'OK')
            time.sleep(0.1)  # 防止傳送沾粘
            c.send(line.encode())
            f.close()
            insert_history()  # 插入成功情況下才加入到歷史紀錄
            return
    c.send(b'FALL')  # ex:zzzz變歷到最後都不會比它大的情況(其他情況)
    f.close()


def do_hist(c, db, data):
    print("歷史紀錄")
    l = data.split(' ')
    name = l[1]
    cursor = db.cursor()

    sql = "select * from hist where name='%s'" % name  #limit 可以限制發送幾條
    cursor.execute(sql)
    r = cursor.fetchall()  # 獲取所有紀錄
    if not r:
        c.send(b'FALL')  # 你沒有歷史紀錄
        return
    else:
        c.send(b'OK')

    # 循環發送歷史紀錄
    for i in r:
        time.sleep(0.1)
        # 每條紀錄每個字段的值id | name | word | time
        msg = "%s   %s   %s" % (i[1], i[2], i[3])
        c.send(msg.encode())
    time.sleep(0.1)
    c.send(b'##')


if __name__ == '__main__':
    main()
