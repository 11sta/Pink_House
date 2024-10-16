"""
    sql模块
"""

import pymysql
pymysql.install_as_MySQLdb()
import sys
from config import *

"""
    开始服务器后，先判断是否存在chat数据库,
    如果存在，则提示自行检查数据库的所有表是否ok
    如果chat数据库不存在，则创建chat数据库，然后建立表,数据库的初始化

"""
class MySql(object):
    def __init__(self):
        self.db_conf = DbConf()
        # 创建数据库连接对象
        self.db_conn = self.open_conn()
        # 创建游标
        self.cur = self.db_conn.cursor()

    def sql_init(self):
        """
            初始化数据库
        """
        re = self.create_chatdb()
        if re == True:
            self.create_user_tb()
            self.create_firs_tb()
            self.create_chat_history_tb()
            self.create_group_room()
            self.create_room_user()
        else:
            print("数据库chat已存在,请检查")
            

    def open_conn(self):
        """
            连接数据库
        """
        try:
            # 建立连接对象
            conn = pymysql.connect(host='localhost', user='root', passwd='123456',db='user',charset='utf8')
        except Exception as e:
            print("连接数据库错误")
            print(e)
            sys.exit("数据库连接失败，程序退出")
        return conn


    def create_chatdb(self):
        """
            访问或创建chat库
        """
        try:
            self.cur.execute("create database chat default charset=utf8")
        except Exception as e:
            # print(e)
            return False
        else:
            print("创建chat成功")
            return True

    def create_user_tb(self):
        """
            创建用户表
            编号：id
            用户账号:uid
            电话号码：uphone
            用户名:uname
            用户密码:upwd
        """
        # 进入chat数据库
        self.cur.execute("use chat;")
        # print("进入数据库成功")
        sql = """create table if not exists user (uid varchar(32) primary key
         ,uname varchar(64) not null,upwd varchar(32) not null,uphone varchar(64) not null,);"""
        # 创建user表
        self.cur.execute(sql)
        print("创建user表成功")

    def create_chat_history_tb(self):
        """
            创建聊天历史记录表
        """
        # sql = """create table if not exists history (uid varchar(32) primary key,
        #     fuid VARCHAR(32) not NULL ,msg VARCHAR (2048) not NULL);"""
        sql = """create table if not exists chat_history (uid varchar(32) not NULL,
        fuid VARCHAR(32) not NULL ,msg VARCHAR (2048) not NULL,times VARCHAR(128) not NULL,re enum('y','n'));"""
        # 创建history表
        self.cur.execute(sql)
        print("创建chat history表成功")


    def create_group_room(self):
        """
            创建群聊表
            rooms ：群id
            uid :　创建的用户id
            room_name：群名字
        """
        sql = """create table if not exists rooms (room_id varchar(32) primary key,uid varchar(32) not NULL,room_name varchar(64) not null);"""
        self.cur.execute(sql)
        print("创建rooms表成功")


    def create_room_user(self):
        """"
            创建群使用着
            id:主键,自增
            room_id :　群的id
            room_user:群成员uid

        """
        sql = """create table if not exists room_user (id INT auto_increment  primary key 
                         ,room_id varchar(32) not NULL,room_user varchar(32) not null,room_name varchar(64) not null);"""
        self.cur.execute(sql)
        print("创建room_user表成功")


    def create_firs_tb(self):
        """
            创建添加好友数据库
            好友表
            主用户:user_id1
            好友:user_id2
        """
        sql = """create table if not exists friends ( user_id1 varchar(32) not null,
        user_id2 varchar(32) not null,primary key (user_id1,user_id2));
        """
        # 创建friends表
        self.cur.execute(sql)
        print("创建friends表成功")



if __name__ == '__main__':
    db = MySql()
    db.create_user_tb()
    










# class DBhelper:
#     def __init__(self):
#         """
#             构造方法
#         """
#         # 数据库连接对象
#         self.db_conn = None
#         self.db_conf = DbConf()

#     def open_conn(self):
#         """
#             连接数据库
#         :return:
#         """
#         try:
#             # 建立连接对象
#             self.db_conn = pymysql.connect(self.db_conf.host, self.db_conf.user, self.db_conf.passwd,
#                                            self.db_conf.dbname)
#         except Exception as e:
#             print("连接数据库错误")
#             print(e)
#         else:
#             print("连接数据库成功")
#         return True

#     def close_conn(self):
#         """
#             关闭数据库连接
#         :return:
#         """
#         try:
#             self.db_conn.close()
#         except Exception as e:
#             print("关闭数据库错误")
#             print(e)
#         else:
#             print("关闭数据库成功")


#     def commit():

#          self.db_conn.commit()


# def get_user(user_id):
#     fields = ['id', 'username', 'nickname']
#     row = c.execute('SELECT ' + ','.join(fields) + ' FROM users WHERE id=?', [user_id]).fetchall()
#     if len(row) == 0:
#         return None
#     else:
#         user = dict(zip(fields, row[0]))
#         user['online'] = user_id in user_id_to_sc
#         return user