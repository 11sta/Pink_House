"""
    数据库tool模块
    对数据库的查找，写入，删除操作

"""
import pymysql
from sql_db import *

class Sql_tool():
    def __init__(self):
        self.sql_tool = MySql()
        # 进入chat数据库
        self.sql_tool.cur.execute("use chat;")

    def query_user_by_uid(self,uid):
        """
            查询用户表
            返回用户名是否存在数据库
        """
        sql = "select * from user where uid = '%s'"%uid
        # sql = "select * from user where uid = " + uid
        self.sql_tool.cur.execute(sql)
        r = self.sql_tool.cur.fetchone()
        if r != None:
            return False
        else:
            return True
    def query_is_friend(self, user_id1, user_id2):
        """
            查询是否是好友
        """
        sql01 = "select * from friends where user_id1 = '%s' and user_id2 = '%s'" % (user_id1, user_id2)
        self.sql_tool.cur.execute(sql01)
        result01 = self.sql_tool.cur.fetchone()
        sql02 = "select * from friends where user_id2 = '%s' and user_id1 = '%s'" % (user_id1, user_id2)
        self.sql_tool.cur.execute(sql02)
        result02 = self.sql_tool.cur.fetchone()
        if result01 or result02:  # 是好友
            return True
        else:  # 非好友
            return False

    def verify_login(self,uid,upwd):
        """
            验证用户登录
            验证账号跟密码是否一致
        """
        sql = "select * from user where uid = '%s' and upwd = '%s'" %(uid,upwd)
        self.sql_tool.cur.execute(sql)
        r = self.sql_tool.cur.fetchone()
        if r != None:
            return True
        else:
            return False

    def insert_user(self,uid,uname,upwd,uphone):
        """
            创建用户
            用户信息写入到数据库
        """
        sql = "insert into user (uid ,uname,upwd,uphone) values ('%s','%s',%s, %s)"%(uid,uname,upwd,uphone)
        try:
            self.sql_tool.cur.execute(sql)
            self.sql_tool.db_conn.commit()
            return True
        except Exception as e:
            print(e)
            self.sql_tool.db_conn.rollback()
            return False


    def insert_friends(self,uid,fuid):
        """
            存储添加好友信息
        """
        sql = "insert into friends (user_id1 ,user_id2) values ('%s','%s')"%(uid,fuid)
        try:
            self.sql_tool.cur.execute(sql)
            self.sql_tool.db_conn.commit()
            return True
        except:
            self.sql_tool.db_conn.rollback()
            return False

    # def retrieve_offline_messages(receiver_id):
    #     sql = ("SELECT uid, fuid, msg, time, re "
    #             FROM chat_history WHERE )
    #
    #     '''
    #         SELECT id, sender_id, message, timestamp
    #         FROM offline_messages
    #         WHERE receiver_id = ?
    #     ''', (receiver_id,))
    #     messages = c.fetchall()
    #     conn.close()
    #     return messages

    def insert_chat_history(self,uid,fuid,msg,times,re):
        """
            查询历史记录
        :param uid:
        :param fuid:
        :param msg:
        :return:
        """
        sql = "insert into chat_history values ('%s','%s','%s','%s','%s')" % (uid, fuid, msg, times, re)
        try:
            self.sql_tool.cur.execute(sql)
            self.sql_tool.db_conn.commit()
            return True
        except Exception as e:
            print(e)
            self.sql_tool.db_conn.rollback()
            return False


    def get_friends_list_by_uid(self,uid):
        """
            通过用户名查询所有好友
        """
        temp_list = []
        sql = "select user_id2 from friends where user_id1 = '%s' " % uid
        self.sql_tool.cur.execute(sql)
        result01 = self.sql_tool.cur.fetchall()
        sql = "select user_id1 from friends where user_id2 = '%s' " % uid
        self.sql_tool.cur.execute(sql)
        result02 = self.sql_tool.cur.fetchall()
        result = result01 + result02
        if result == None:
            return []
        else:
            for i in result:
                temp_list.append(''.join(i))
        # 此时temp_list 为用户所有好友的账号
        return temp_list

    def query_is_friend(self,user_id1,user_id2):
        """
            查询是否是好友
        """
        sql01 = "select * from friends where user_id1 = '%s' and user_id2 = '%s'" % (user_id1,user_id2)
        self.sql_tool.cur.execute(sql01)
        result01 = self.sql_tool.cur.fetchone()
        sql02 = "select * from friends where user_id2 = '%s' and user_id1 = '%s'" % (user_id1,user_id2)
        self.sql_tool.cur.execute(sql02)
        result02 = self.sql_tool.cur.fetchone()
        if result01 or result02:  #是好友
            return True
        else:   #非好友
            return False

    def delete_friend_by_uid(self, user_id1, user_id2):
        """
            通过用户好友账号从数据库中删除好友的信息
        """
        sql1 = "DELETE FROM friends WHERE user_id1 = %s AND user_id2 = %s"
        sql2 = "DELETE FROM friends WHERE user_id2 = %s AND user_id1 = %s"
        try:
            self.sql_tool.cur.execute(sql1, (user_id1, user_id2))
            self.sql_tool.cur.execute(sql2, (user_id1, user_id2))
            self.sql_tool.db_conn.commit()
            return True
        except Exception as e:
            print("删除失败:", e)
            self.sql_tool.db_conn.rollback()
            return False
    def get_uname_by_uid(self,uid):
        """
            通过查询账号获得昵称
            返回用户昵称,字符串
        """
        sql = "select uname from user where uid = '%s' " % uid
        self.sql_tool.cur.execute(sql)
        result = self.sql_tool.cur.fetchone()
        # 结果是一个元组，需要将元组转换为字符串
        result = ''.join(result)
        return result

    def insert_rooms(self,room_id,uid,room_name):
        """
            插入创建的群号到数据库
        :param uid:
        :param room_id:
        :param room_name:
        :return:
        """
        sql = "insert into rooms values ('%s','%s','%s')" % (room_id, uid, room_name,)
        try:
            self.sql_tool.cur.execute(sql)
            self.sql_tool.db_conn.commit()
            return True
        except Exception as e:
            print(e)
            self.sql_tool.db_conn.rollback()
            return False

    def insert_room_user(self,room_id,room_user):
        """
            插入群的成员
        :param uid:
        :param room_id:
        :return:
        """
        room_name = self.get_rname_by_rid(room_id)
        sql = "INSERT INTO room_user (room_id, room_user, room_name) VALUES (%s, %s, %s)"
        try:
            self.sql_tool.cur.execute(sql, (room_id, room_user, room_name))
            self.sql_tool.db_conn.commit()
            return True
        except Exception as e:
            print(f"插入群成员时发生错误: {e}. SQL: {sql}, 参数: ({room_id}, {room_user})")
            self.sql_tool.db_conn.rollback()
            return False

    def veriaty_room_id(self,room_id):
        """
            验证创建的群是否唯一
        :param room_id:
        :return:
        """
        sql = "select * from rooms where room_id = '%s'" % room_id
        self.sql_tool.cur.execute(sql)
        r = self.sql_tool.cur.fetchone()
        if r != None:  #不唯一,群存在
            return False
        else:   #唯一，群不存在
            return True

    def get_rooms_by_uid(self,uid):
        """
            通过rid查找rid和rname
        :param uid:
        :return: rid, rname
        """
        sql = "select room_id,room_name from room_user where room_user = '%s' " % uid
        self.sql_tool.cur.execute(sql)
        result = self.sql_tool.cur.fetchall()
        # result = ''.join(result)
        room_list = [{room_id: room_name} for room_id, room_name in result]
        print(room_list)
        return room_list

    def get_rname_by_rid(self,room_id):
        """
            通过rid查找群名
        :param rid:
        :return:
        """
        sql = "select room_name from rooms where room_id = '%s'" % room_id
        self.sql_tool.cur.execute(sql)
        result = self.sql_tool.cur.fetchone()
        # 结果是一个元组，需要将元组转换为字符串
        result = ''.join(result)
        return result


    def get_room_user_by_rid(self,room_id):
        """
            通过群room_id获取群成员
        :param room_id:
        :return:
        """
        temp_list = []
        sql = "select room_user from room_user where room_id = '%s' " % room_id
        self.sql_tool.cur.execute(sql)
        result = self.sql_tool.cur.fetchall()
        for i in result:
            temp_list.append(''.join(i))
        # 此时temp_list 为用户的账号
        return temp_list


    def get_history_msg(self,uid,fuid):
        self.sql_tool.cur.execute(
            "SELECT uid, fuid, msg, times FROM chat_history WHERE (uid = %s AND fuid = %s) OR (uid = %s AND fuid = %s) ORDER BY times ASC",
            (uid, fuid, fuid, uid))
        rows = self.sql_tool.cur.fetchall()
        return rows

# if __name__ == "__main__":
#     re = Sql_tool()
#     re.get_rooms_by_uid('123456')
    # re.insert_friends('13750050640','13750050642')
    # print(result)
    # result = re.verify_login("12311111111","123456")
    # print(result)

    # result = re.get_uname_by_uid("12311111111")
    # print(result)
    # print(type(result))

    # result = re.query_friens_by_uid("12345678")
    # print(result)
    # print(type(result))
    # result = re.insert_user("12345678","456","45678")
    # print(result)
    # print(type(result))
    # result = re.insert_chat_history('1235','456','hah我是')
    # result = re.query_is_friend('12369874105','12345678910')
    # result = re.insert_room_user('147258',"123456")
    # print(result)
