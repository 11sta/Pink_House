from tkinter import *
from tkinter import scrolledtext
from tkinter import filedialog
from datetime import datetime
from client_bll import *
import tkinter.messagebox
from PIL import Image, ImageTk
import pymysql
import io

class MainWindow:
    def __init__(self, client, data):
        self.client = client
        self.data = data
        self.fri_list = self.get_fri_list()  # 获取所有好友列表
        self.fris_on_line = self.get_fris_on_line()  # 获取在线好友列表
        self.room_list = self.get_room_list()  # 获取群列表
        self.myuid = data['uid']  # 我的账号
        self.myname = data['uname']  # 我的昵称
        # self.friend_frame = {}
        # 创建主窗口
        self.root = Tk()
        # 窗口大小
        self.root.geometry("255x600+900+40")
        # 设置窗口标题
        self.root.title(self.myname)
        # 设置窗口大小固定
        self.root.resizable(0, 0)
        # self.win_dict = {}  # 保存已经打开窗口
        self.chatdict = {}  # 聊天
        self.client.thread()
        self.thread1()
        self.start()

    # 获取所有好友列表
    def get_fri_list(self):
        if "fri_list" in self.data:
            print("所有好友列表",self.data["fri_list"])
            return self.data["fri_list"]
        return []

    # 获取在线好友列表
    def get_fris_on_line(self):
        if "fris_on_line" in self.data:
            return self.data["fris_on_line"]
        return []

    def get_room_list(self):
        if "room_list" in self.data:
            print("所有群聊列表",self.data["room_list"])
            return self.data["room_list"]
        return []

    # 创建线程处理服务端的消息
    def thread1(self):
        # 创建新的线程
        t = Thread(target=self.recv_msg, )
        t.daemon = True # 分支线程会随主线程退出
        t.start()

    # 线程函数
    def recv_msg(self):
        while True:
            if len(disconnect) > 0:  # 别处登录
                self.quit()
            if len(chat_list) != 0:  # 处理聊天信息
                print(chat_list)
                for item in chat_list:
                    for fuid, msglist in item.items():
                        if fuid not in win_dict:  # 如果该聊天窗口不存在
                            friend_frame[fuid].config(text=len(msglist))  # 显示未读信息个数
                            friend_frame[fuid].place(x=220, y=20)
                        else:
                            copy_msglist = msglist[::]
                            for i in copy_msglist:
                                for times, msg in i.items():
                                    friend_frame[fuid].place_forget()
                                    self.recv_message(win_dict[fuid][1], msg, times,fname=win_dict[fuid][3])
                                    msglist.remove(i)
                            chat_list.remove(item)

            if len(friend_on_list) != 0:  # 好友上线
                self.fris_on_line.append(friend_on_list[0])
                self.friend_list()
                del friend_on_list[0]
            if len(friend_off_list) != 0:  # 好友离线
                self.fris_on_line.remove(friend_off_list[0])
                self.friend_list()
                del friend_off_list[0]
            if len(is_friend) > 0:  # 好友是否存在
                if is_friend[0] == "yes":
                    self.messagebox("请求已发送")
                elif is_friend[0] == "no":
                    self.messagebox("该账号不存在")
                elif is_friend[0] == "is":
                    self.messagebox("已经是好友")
                del is_friend[0]

            if len(add_friend_list) > 0:  # 好友请求
                self.btn_fr_re.place(x=0, y=170)
                self.btn_fr_re["command"] = self.friend_request
            if len(fri_re) > 0:  # 添加好友结果
                self.btn_fr_re.place(x=0, y=170)
                self.btn_fr_re["command"] = self.friend_result
                if fri_re[0]["re"] == "yes":
                    fuid = fri_re[0]["fuid"]
                    fname = fri_re[0]["fname"]
                    dict = {}
                    dict[fuid] = fname
                    if dict not in self.fri_list:
                        self.fri_list.append(dict)
                        if fri_re[0]["state"] == "yes":
                            self.fris_on_line.append(fuid)  # 在线列表
                            self.friend_list()

            if len(del_re) > 0: # 删除好友结果
                fuid = del_re[0]['fuid']
                funame = del_re[0]['funame']
                # dict = {}
                # dict[fuid] = funame
                if del_re[0]['re'] == 'deleted':
                    self.fri_list = [f for f in self.fri_list if fuid not in f.keys()]
                    self.friend_list()  # 更新好友列表显示
                    self.messagebox(f'删除好友成功', '提示')
                elif del_re[0]['re'] == 'wrong':
                    self.messagebox(f'该用户非好友', '提示')
                else:
                    self.messagebox(f"删除好友失败",'提示' )
                del del_re[0]

            if len(create_room) > 0:  # 创建群结果
                dict1 = {}
                if "yes" in create_room[0]['re']:
                    self.messagebox("群号:%s\n创建成功"% create_room[0]["rid"])
                    rid = create_room[0]['rid']
                    rname = create_room[0]['rname']
                    dict1[rid] = rname
                    self.data['room_list'].append(dict1)
                    self.room_list = self.get_room_list()
                    self.sh_room_list()
                    del create_room[0]
                    # self.btn_fr_re.place(x=30, y=560)
                    # self.btn_fr_re["command"] = self.create_room_succeed()
                else:
                    self.messagebox("群号:%s\n已被占用"% create_room[0]["rid"])
                    del create_room[0]
                    del create_room[1]
            time.sleep(0.1)

            if len(add_room_re) > 0:  #加入群结果
                rid = add_room_re[0]['rid']
                dict = {}
                if add_room_re[0]["re"] == "no":
                    self.messagebox("该群聊不存在")
                elif add_room_re[0]["re"] == "yes":
                    self.messagebox("成功加入该群聊")
                    rname = add_room_re[0]['rname']
                    dict[rid] = rname
                    self.data['room_list'].append(dict)
                    self.room_list = self.get_room_list()
                    self.sh_room_list()
                elif add_room_re[0]["re"] == "wrong":
                    self.messagebox("您已经在群聊中")
                else:
                    self.messagebox("加入群聊出错", add_room_re[0]["error"])

                del add_room_re[0]

    # 添加好友结果
    def friend_result(self):
        # self.btn_fr_re.place_forget()
        item = fri_re[0]
        del fri_re[0]
        fuid = item["fuid"]
        fname = item["fname"]
        if item["re"] == "yes":
            re = "同意"
        else:
            re = "拒绝"
        msg = "昵称：%s\n账号：%s\n%s加您为好友" % (fname, fuid, re)
        self.messagebox(msg, "好友请求")

    # 好友请求
    def friend_request(self):
        # self.btn_fr_re.place_forget()
        item = add_friend_list[0]
        del add_friend_list[0]
        for fuid, fname in item.items():
            msg = "昵称：%s\n账号：%s\n请求加您为好友，是否同意" % (fname, fuid)
            re = tkinter.messagebox.askquestion('好友请求', msg)
            if re == "yes":
                dict = {}
                dict[fuid] = fname
                self.fri_list.append(dict)  # 好友列表
                # self.fris_on_line.append(fuid)  # 在线列表
                self.friend_list()
            self.client.friend_request_result(self.myuid, fuid, re)

    def create_room_succeed(self):
        self.btn_fr_re.place_forget()
        self.messagebox(create_room[0])
        self.room_list.append
        del create_room[0]

    def add_room_result(self):
        self.messagebox(add_room_re[0])

    # 联系人主界面
    def start(self):
        self.root.geometry('315x500')
        photo = PhotoImage(file="b2.png")
        label = Label(self.root, image=photo)  # 图片
        label.place(x=0, y=0, relwidth=1, relheight=1)
        # 创建左侧的侧边栏
        self.sidebar = Frame(self.root, width=60, bg='white', highlightthickness=0)  # 创建侧边栏
        self.sidebar.place(x=0, y=0, height=500)  # 侧边栏高度与窗口相同

        self.add_friend_icon = ImageTk.PhotoImage(Image.open("添加好友.png").resize((55, 65)))  # 调整图标大小
        self.delete_friend_icon = ImageTk.PhotoImage(Image.open("删除好友.png").resize((55, 65)))
        self.create_group_icon = ImageTk.PhotoImage(Image.open("创建群聊.png").resize((55, 65)))
        self.join_group_icon = ImageTk.PhotoImage(Image.open("加入群聊.png").resize((55, 65)))
        self.friend_list_icon = ImageTk.PhotoImage(Image.open("好友列表.png").resize((55, 65)))
        self.btn_fr_re_icon = ImageTk.PhotoImage(Image.open("系统消息.png").resize((55, 65)))
        self.room_list_icon = ImageTk.PhotoImage(Image.open("群聊列表.png").resize((55, 65)))

        # 初始化好友列表显示状态为 False（隐藏状态）
        self.friend_list_visible = False
        self.room_list_visible = False
        # # 创建一个切换显示好友列表的按钮
        self.friend_list_btn = Button(self.sidebar, image=self.friend_list_icon,text="好友列表", fg="white", bg="lightgrey",
                                      borderwidth=0, highlightthickness=0,command=self.toggle_friend_list)
        self.friend_list_btn.place(x=0, y=60)
        #创建一个显示切换显示群聊列表的按钮
        self.room_list_btn = Button(self.sidebar, image=self.room_list_icon,text="群聊列表", fg="white", bg="lightgrey",
                                      borderwidth=0, highlightthickness=0,command=self.toggle_room_list)
        self.room_list_btn.place(x=0, y=385)
        # 头像框
        self.avatar_label = Label(self.sidebar, width=65, height=65, bg="lightpink",relief="ridge",bd=2)
        self.avatar_label.place(x=0, y=2,width=60, height=60)
        self.avatar_label.bind("<Double-Button-1>", self.upload_avatar)  # 绑定双击事件
        # 获取并显示头像
        avatar_binary_data = self.get_avatar_from_db(self.myuid)
        if avatar_binary_data:
            # 将二进制数据转换为图像并显示
            image_stream = io.BytesIO(avatar_binary_data)
            img = Image.open(image_stream)
            img = img.resize((60, 60), Image.LANCZOS)
            avatar = ImageTk.PhotoImage(img)
            self.avatar_label.config(image=avatar)  # 更新头像框显示
            self.avatar_label.image = avatar  # 保持对图像的引用

        Button(self.sidebar, image=self.add_friend_icon, text="添加好友", fg="white", bg="lightgrey",
               borderwidth=0, highlightthickness=0,
               command=lambda: self.create_win("添加好友", "输入好友账号", self.add_friend)).place(x=0, y=115)

        Button(self.sidebar, image=self.delete_friend_icon, text="删除好友", fg="white", bg="lightgrey",
               borderwidth=0, highlightthickness=0,
               command=lambda: self.create_win("删除好友", "输入好友账号", self.del_friend)).place(x=0, y=227)

        Button(self.sidebar, image=self.create_group_icon, text="创建群", fg="white", bg="lightgrey",
               borderwidth=0, highlightthickness=0,
               command=lambda: self.create_win("创建群", "输入群号", self.create_room, 1)).place(x=0, y=285)

        Button(self.sidebar, image=self.join_group_icon, text="加入群", fg="white", bg="lightgrey",
               borderwidth=0, highlightthickness=0,
               command=lambda: self.create_win("加入群", "输入群号", self.add_room)).place(x=0, y=330)

        self.btn_fr_re = Button(self.sidebar,borderwidth=0, highlightthickness=0,image=self.btn_fr_re_icon, text="系统信息", )
        self.btn_fr_re.place(x=0, y=170)  # 消息按钮
        # self.btn_fr_re.place_forget()  # 隐藏按钮
        self.root.mainloop()

    def toggle_friend_list(self):
        # 根据当前好友列表是否可见来切换显示或隐藏
        if self.friend_list_visible:
            self.hide_friend_list()  # 当前显示中，隐藏它
        else:
            self.show_friend_list()  # 当前隐藏，显示它

    def toggle_room_list(self):
        # 根据当前好友列表是否可见来切换显示或隐藏
        if self.room_list_visible:
            self.hide_room_list()  # 当前显示中，隐藏它
        else:
            self.show_room_list()  # 当前隐藏，显示它

    def show_friend_list(self):
        # 调用 friend_list() 函数来显示好友列表
        self.friend_list()
        # 切换按钮文本为 "隐藏好友列表"
        self.friend_list_btn.config(text="隐藏好友")
        self.friend_list_visible = True

    def show_room_list(self):
        # 调用 room_list() 函数来显示好友列表
        self.room_list = self.get_room_list()
        self.sh_room_list()
        # 切换按钮文本为 "隐藏群聊列表"
        self.room_list_btn.config(text="隐藏群聊")
        self.room_list_visible = True

    def hide_friend_list(self):
        # 隐藏好友列表，通过清除好友列表的组件或使用 place_forget
        self.clear_friend_list()
        self.friend_list_btn.config(text="显示好友")  # 切换按钮文本为 "显示好友列表"
        self.friend_list_visible = False  # 更新状态为隐藏

    def hide_room_list(self):
        # 隐藏好友列表，通过清除群聊列表的组件或使用 place_forget
        self.clear_friend_list()  #借用清除好友列表方法
        self.room_list_btn.config(text="显示群聊")  # 切换按钮文本为 "显示群聊列表"
        self.room_list_visible = False  # 更新状态为隐藏

    def clear_friend_list(self):
        # 移除好友列表的所有组件，这里可以根据你使用的具体布局方式调整
        for widget in self.root.winfo_children():
            if isinstance(widget, Canvas):
                widget.place_forget()  # 隐藏 canvas
    # 显示好友列表
    def friend_list(self, ):
        count = len(self.fri_list)
        canvas = Canvas(self.root, width=250, height=500, scrollregion=(0, 0, 520, count * 57))  # 创建canvas
        canvas.place(x=60, y=0, )
        frame = Frame(canvas)  # 把frame放在canvas里
        frame.place(x=60, y=0, width=200, height=180)  # frame的长宽，和canvas差不多的
        vbar = Scrollbar(canvas, orient=VERTICAL)  # 竖直滚动条
        vbar.place(x=240, width=20, height=500)
        vbar.configure(command=canvas.yview)
        canvas.config(yscrollcommand=vbar.set)  # 设置

        for i in self.fri_list:
            for fuid, fname in i.items():
                if fuid in self.fris_on_line:
                    f1 = Frame(frame, width=240, height=50, bg="white", borderwidth=3, relief=RIDGE)
                    f1.pack(side=TOP, )
                    L = Label(f1, text=fname + "(在线)", fg="green", font=("隶书", 18))
                    L.place(x=55, y=8)

                    # 从数据库中获取好友的头像二进制数据
                    avatar_binary_data = self.get_avatar_from_db(fuid)
                    if avatar_binary_data:
                        # 将二进制数据转换为图片
                        image_stream = io.BytesIO(avatar_binary_data)
                        img = Image.open(image_stream)
                        img = img.resize((40, 40), Image.LANCZOS)  # 调整头像大小
                        avatar = ImageTk.PhotoImage(img)

                        # 显示头像
                        avatar_label = Label(f1, image=avatar, width=40, height=40)
                        avatar_label.image = avatar  # 防止垃圾回收
                        avatar_label.place(x=2, y=2)

                    msg_count = Label(f1, text='', width=2, height=2, bg="white", fg="red")
                    msg_count.place(x=220, y=20)
                    msg_count.place_forget()  # 隐藏
                    msg_count.bind("<Double-Button-1>", self.dblclickAdaptor(self.chat_window, fuid=fuid, fname=fname))
                    L.bind("<Double-Button-1>", self.dblclickAdaptor(self.chat_window, fuid=fuid, fname=fname))
                    f1.bind("<Double-Button-1>", self.dblclickAdaptor(self.chat_window, fuid=fuid, fname=fname))
                    friend_frame[fuid] = msg_count
        for i in self.fri_list:
            for fuid, fname in i.items():
                if fuid not in self.fris_on_line:
                    f1 = Frame(frame, width=240, height=50, bg="white", borderwidth=3, relief=RIDGE)
                    f1.pack(side=TOP, )
                    L = Label(f1, text=fname + "(离线)", fg="gray", font=("隶书", 18))
                    L.place(x=55, y=8)

                    # 从数据库中获取好友的头像二进制数据
                    avatar_binary_data = self.get_avatar_from_db(fuid)
                    if avatar_binary_data:
                        # 将二进制数据转换为图片
                        image_stream = io.BytesIO(avatar_binary_data)
                        img = Image.open(image_stream)
                        img = img.resize((40, 40), Image.LANCZOS)  # 调整头像大小
                        avatar = ImageTk.PhotoImage(img)

                        # 显示头像
                        avatar_label = Label(f1, image=avatar, width=40, height=40)
                        avatar_label.image = avatar  # 防止垃圾回收
                        avatar_label.place(x=2, y=2)

                    msg_count = Label(f1, text='', width=1, height=1, bg="white", fg="red")
                    msg_count.place(x=210, y=10)
                    msg_count.place_forget()
                    msg_count.bind("<Double-Button-1>", self.dblclickAdaptor(self.chat_window, fuid=fuid, fname=fname))
                    L.bind("<Double-Button-1>", self.dblclickAdaptor(self.chat_window, fuid=fuid, fname=fname))
                    f1.bind("<Double-Button-1>", self.dblclickAdaptor(self.chat_window, fuid=fuid, fname=fname))
                    friend_frame[fuid] = msg_count

        canvas.create_window(0, count * 26, window=frame, anchor=W)  # create_window

    def sh_room_list(self, ):
        count = len(self.room_list)
        canvas = Canvas(self.root, width=250, height=500, scrollregion=(0, 0, 520, count * 57))  # 创建canvas
        canvas.place(x=60, y=0, )
        frame = Frame(canvas)  # 把frame放在canvas里
        frame.place(x=60, y=0, width=200, height=180)  # frame的长宽，和canvas差不多的
        vbar = Scrollbar(canvas, orient=VERTICAL)  # 竖直滚动条
        vbar.place(x=240, width=20, height=500)
        vbar.configure(command=canvas.yview)
        canvas.config(yscrollcommand=vbar.set)  # 设置

        for i in self.room_list:
            for rid, rname in i.items():
                f1 = Frame(frame, width=250, height=50, bg="white", borderwidth=3, relief=RIDGE)
                f1.pack(side=TOP, )
                L = Label(f1, text=f'{rname}: {rid}', fg="green", font=("隶书", 18))
                L.place(x=0, y=8)

                # msg_count = Label(f1, text='', width=2, height=2, bg="white", fg="red")
                # msg_count.place(x=220, y=20)
                # msg_count.place_forget()  # 隐藏
                # msg_count.bind("<Double-Button-1>", self.dblclickAdaptor(self.group_chat_window, rid=rid, rname=rname))
                # L.bind("<Double-Button-1>", self.dblclickAdaptor(self.group_chat_window, rid=rid, rname=rname))
                # f1.bind("<Double-Button-1>", self.dblclickAdaptor(self.group_chat_window, rid=rid, rname=rname))
        canvas.create_window(0, count * 26, window=frame, anchor=W)  # create_window

    def dblclickAdaptor(self, fun, **kwds):
        return lambda event: fun(event, **kwds)

    def upload_avatar(self, event=None):
        # 打开文件选择对话框
        file_path = filedialog.askopenfilename(title="选择头像", filetypes=[("Image files", "*.jpg *.png *.jpeg")])
        if file_path:
            # 打开并调整图片大小以适应头像框
            img = Image.open(file_path)
            img = img.resize((60, 60), Image.LANCZOS)  # 使用 Image.LANCZOS 替换 ANTI_ALIAS
            avatar = ImageTk.PhotoImage(img)
            # 更新头像框显示
            self.avatar_label.config(image=avatar)  # 确保使用 'image' 参数
            self.avatar_label.image = avatar  # 保持对图像的引用，防止被垃圾回收
            #保存头像
            with open(file_path, 'rb') as file:
                avatar_data = file.read()  # 读取图像文件为二进制数据
                # 保存到数据库
            conn = pymysql.connect(host='localhost', user='root', passwd='123456',db='chat',charset='utf8')
            cursor = conn.cursor()
            cursor.execute('UPDATE user SET image = %s WHERE uname = %s',
                           (avatar_data, self.myname))  # 更新当前用户的头像
            conn.commit()
            conn.close()

    def get_avatar_from_db(self, uid):
        conn = pymysql.connect(host='localhost', user='root', passwd='123456', db='chat', charset='utf8')
        cursor = conn.cursor()
        # 执行查询，使用 %s 作为参数占位符
        cursor.execute('SELECT image FROM user WHERE uid = %s', (uid,))
        # 获取查询结果
        result = cursor.fetchone()
        conn.close()
        # 如果有结果，返回头像的二进制数据；如果没有，返回 None
        if result:
            return result[0]  # result[0] 是头像的二进制数据
        return None


    # 判断窗口是否已存在
    def win_exist(self, key):
        # 如果窗口存在，则显示该窗口
        if key in win_dict:
            win_dict[key][0].deiconify()
            return True

    # 创建聊天窗口
    def chat_window(self, event, fuid, fname):
        # 判断窗口是否已存在
        if self.win_exist(fuid):
            # 窗口存在则返回
            return
        # 创建聊天窗口
        self.chat = Toplevel()
        # self.win_dict[name] = self.chat
        # 窗口大小
        self.chat.geometry("470x420")
        # 设置窗口大小固定
        self.chat.resizable(0, 0)
        # 设置窗口标题
        self.chat.title("与%s聊天中" % fname)
        message_block = Frame(self.chat, width=580, height=450, bg="#D3D0C6")
        message_block.pack()
        # 设置窗口背景图
        photo = PhotoImage(file="b4.png")
        label = Label(self.chat, image=photo)  # 图片
        label.place(in_=message_block, )
        # 聊天信息块
        text1 = scrolledtext.ScrolledText(self.chat,font=("隶书", 18))
        text1.place(in_=message_block, x=10, y=10, width=450, height=250)  # 滚动文本框在页面的位置

        # 发送信息块
        text2 = scrolledtext.ScrolledText(self.chat,)
        text2.place(in_=message_block, x=10, y=290, width=450, height=100)
        win_dict[fuid] = [self.chat, text1, text2,fname]
        # self.chatdict[self.chat] = [self.chat,text1, text2]
        # 设置文本框不可编辑
        text1.config(state=DISABLED)

        # 发送按钮
        # b = Button(self.chat, text="发送", command=lambda: self.recv_message(scr, text2,))
        b = Button(self.chat, text="发送", command=lambda: self.send_message(fuid, text1, text2))
        b.place(in_=message_block, width=30, height=22, x=430, y=395)
        # 聊天记录按钮
        record = Button(self.chat, text="聊天记录", command=lambda: self.chat_history(self.myuid, fuid, text1))
        record.place(in_=message_block, width=50, height=22, x=410, y=265)
        # 更新聊天信息
        # self.recv_message(text1, "3546843")

        # 点击关闭按钮触发事件
        self.chat.protocol("WM_DELETE_WINDOW", lambda: self.close_window(key=fuid))
        self.chat.mainloop()


    def get_group_members(self,rid):
        conn = pymysql.connect(host='localhost', user='root', passwd='123456', db='chat', charset='utf8')
        cursor = conn.cursor()
        # 执行查询，使用 %s 作为参数占位符
        cursor.execute('SELECT room_user FROM room_user WHERE room_id = %s', (rid,))
        # 获取查询结果
        result = cursor.fetchall()
        conn.close()
        # 如果有结果，返回头像的二进制数据；如果没有，返回 None
        if result:
            return [member[0] for member in result]
        else:
            return None

    def send_group_message(self, group_id, text_input, text_messages):
        # 这里可以添加发送消息的逻辑
        message = text_input.get("1.0", END).strip()
        if message:
            text_messages.insert(END, f"你: {message}\n")
            text_input.delete("1.0", END)

    def close_window(self, group_id):
        # 关闭窗口并从字典中移除
        if group_id in win_dict:
            win_dict[group_id][0].destroy()
            del win_dict[group_id]

    def run(self):
        self.root.mainloop()
     # 发送信息
    def send_message(self, fuid, text1, text2):
        time = str(datetime.now())[0:19]
        self.client.send_chat_msg(self.myuid, fuid, text2.get("1.0", END), time)
        self.recv_message(text1, text2.get("1.0", END), time, 1)
        # 清空发送框
        text2.delete('1.0', 'end')

    def chat_history(self, uid, fuid, text1):
        conn = pymysql.connect(host='localhost', user='root', passwd='123456', db='chat', charset='utf8')
        cursor = conn.cursor()
        # 查询双方的聊天记录
        cursor.execute(
            "SELECT uid, fuid, msg, times FROM chat_history WHERE (uid = %s AND fuid = %s) OR (uid = %s AND fuid = %s) ORDER BY times ASC",
            (uid, fuid, fuid, uid))
        # 获取查询结果
        rows = cursor.fetchall()
        # 关闭数据库连接
        conn.close()
        # 遍历查询结果并显示聊天记录
        if rows:
            for row in rows:
                sender_uid = row[0]
                receiver_uid = row[1]
                msg = row[2]
                time = row[3]
                # 判断是自己发送的消息还是对方发送的消息
                if sender_uid == uid:
                    # 自己发送的消息
                    self.recv_message(text1, msg, time, 1)
                else:
                    # 对方发送的消息
                    self.recv_message(text1, msg, time, 0, receiver_uid)

    # 收发信息文本框
    def recv_message(self, text1, msg, times, num=0, fname=None):
        # 设置文本框可编辑
        text1.config(state=NORMAL)
        # 获取当前光标行和列
        l = text1.index('insert')

        if num == 0:  # 收到好友消息的时间颜色为绿色
            # 插入名字和时间
            text1.insert(END, fname +" " + times + ":\n")
            text1.tag_add('tag1', l, l[0:-2] + ".end")
            text1.tag_config('tag1', foreground='green', font=("隶书", 13))
            text1.insert(END, "  " + msg)
        elif num == 1:  # 自己发送消息的时间颜色为蓝色
            # 插入名字和时间
            text1.insert(END, self.myname +" " + times + ":\n")
            text1.tag_add('tag2', l, l[0:-2] + ".end")
            text1.tag_config('tag2', foreground='blue', justify=RIGHT, font=("隶书", 13))
            l = text1.index('insert')
            text1.insert(END, msg)
            text1.tag_add('tag22', l, l[0:-2] + ".end")
            text1.tag_config('tag22', justify=RIGHT)

        # 显示文本框最近的信息
        text1.see(END)
        # 设置文本框不可编辑
        text1.config(state=DISABLED)
        time.sleep(0.1)
    # 关闭窗口
    def close_window(self, key):
        win_dict[key][0].destroy()
        del win_dict[key]

    # 创建窗口(添加好友，删除好友，创建群，加群)
    def create_win(self, name, text, fun,cname=0):
        # 判断窗口是否已存在
        if self.win_exist(name):
            # 窗口存在则返回
            return
        # 创建窗口
        self.win = Toplevel()
        # 窗口大小
        self.win.geometry("400x130")
        # 设置窗口大小固定
        self.win.resizable(0, 0)
        # 设置窗口标题
        self.win.title(name)
        # 设置窗口背景图
        photo = PhotoImage(file="b5.png")
        label = Label(self.win, image=photo)  # 图片
        label.pack()
        # 将窗口对象加入字典
        win_dict[name] = [self.win]
        # 标签
        L1 = Label(self.win, text="群名字")
        L1.place(x=50, y=20)
        L2 = Label(self.win, text=text)
        L2.place(x=50, y=60)
        # 输入框
        E1 = Entry(self.win, )
        E1.place(x=130, y=20)
        E2 = Entry(self.win, )
        E2.place(x=130, y=60)
        if cname == 0:
            L1.place_forget()
            E1.place_forget()

        # 按钮
        B = Button(self.win, text=name, command=lambda: fun(E2.get(), E1.get()))
        B.place(x=300, y=60, height=25)
        # 点击关闭按钮触发事件
        self.win.protocol("WM_DELETE_WINDOW", lambda: self.close_window(key=name))
        self.win.mainloop()

    # 添加好友
    def add_friend(self, fuid,*args):
        msg = self.client.add_friend(self.myuid, fuid)
        if msg:
            self.messagebox(msg)

    def del_friend(self,fuid,*args):
        msg = self.client.del_friend(self.myuid, fuid)
        if msg:
            self.messagebox(msg)
            print("msg:", msg)

    # 创建群聊
    def create_room(self,cid, cname):
        msg = self.client.create_room(self.myuid, cid, cname)
        if msg:
            self.messagebox(msg)
    # 加入群聊
    def add_room(self, rid, *args):
        self.client.add_room(self.myuid, rid)


    # 弹窗提示
    def messagebox(self, msg, title='提示'):
        tkinter.messagebox.showinfo(title=title, message=msg)

    # 强迫下线
    def quit(self):
        self.messagebox(disconnect[0])
        self.root.destroy()
        sys.exit()


