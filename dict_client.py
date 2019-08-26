#!/usr/bin/python3
# coding=utf-8

from socket import *
import sys
import getpass

# 創建網路連接


def main():
    if len(sys.argv) < 3:
        print("argv is error")
        return
    HOST = sys.argv[1]
    PORT = int(sys.argv[2])
    s = socket()
    try:
        s.connect((HOST, PORT))
    except Exception as e:
        print(e)
        return
    while True:
        print('''
    		=====================Welcome======================
    		----------- 1.註冊      2.登入      3.退出--------
    		==================================================
    		''')
        try:
            cmd = int(input("請輸入選項"))
        except Exception as e:
            print("命令錯誤")
            continue
        if cmd not in [1, 2, 3]:
            print("請輸入正確選項")
            sys.stdin.flush()  # 清除標準輸入 防止惡意快速輸入
            continue
        elif cmd == 1:
            r = do_register(s)
            if r == 0:
                print("註冊成功")
                # login(s,name)   # 進入二級界面
            elif r == 1:
                print("用戶存在")
            else:
                print("註冊失敗")
        elif cmd == 2:
            name = do_login(s)
            if name:
                print("登錄成功")  # 這樣可以取得登入者名字
                login(s, name)

            else:
                print("用戶名稱或密碼不正確")
        elif cmd == 3:
            s.send(b'E')
            sys.exit("謝謝使用")


def do_register(s):
    while True:
        name = input("User:")
        passwd = getpass.getpass()
        passwd1 = getpass.getpass("Again:")

        if (' ' in name) or (' ' in passwd):
            print("用戶名稱和密碼不許有空格")
            continue
        if passwd != passwd1:
            print("兩次密碼不一致")
            continue

        msg = 'R {} {}'.format(name, passwd)
        # 發送請求
        s.send(msg.encode())
        # 等待回覆
        data = s.recv(128).decode()
        if data == 'OK':
            return name
        elif data == "EXISTS":
            return 1
        else:
            return 2


def do_login(s):
    name = input("User:")
    passwd = getpass.getpass()
    msg = 'L {} {}'.format(name, passwd)
    s.send(msg.encode())
    data = s.recv(128).decode()

    if data == 'OK':
        return name
    else:
        return


def login(s, name):
    while True:
        print('''
			==============查詢界面==============
			1.查詞    2.歷史紀錄    3.退出       
			====================================
	        ''')
        try:
            cmd = int(input("請輸入選項>>"))
        except Exception as e:
            print("命令錯誤")
            continue

        if cmd not in [1, 2, 3]:
            print("請輸入正確選項")
            sys.stdin.flush()  # 清除標準輸入 防止惡意快速輸入
            continue
        elif cmd == 1:
            do_query(s, name)    # s數據傳輸  name要歷史紀錄誰在查
        elif cmd == 2:
            do_hist(s, name)  # name查自己的歷史紀錄
        elif cmd == 3:
            return              # 回到一級大界面


def do_query(s, name):
    while True:
        print("輸入##退出")
        word = input("單詞：")
        if word == '##':
            break
        msg = 'Q {} {}'.format(name, word)
        s.send(msg.encode())
        data = s.recv(128).decode()
        if data == 'OK':
            data = s.recv(2048).decode()
            print(data)

        else:
            print("沒有查到單詞")


def do_hist(s, name):
    msg = 'H {} '.format(name)
    s.send(msg.encode())
    data = s.recv(128).decode()
    if data == 'OK':
        while True:
            data = s.recv(1024).decode()
            if data == '##':
                break
            print(data)

    else:
        print("沒有歷史紀錄")


if __name__ == '__main__':
    main()
