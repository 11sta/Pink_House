from tkinter import *
from client_bll import *
import tkinter.messagebox
from ui_friend_window import MainWindow
from tkinter import font


class Application:
    def __init__(self, master):
        self.root = master
        # 窗口大小
        self.root.geometry("330x270+400+200")
        # 设置窗口标题
        self.root.title("登录")
        # 设置窗口不可变
        self.root.resizable(0, 0)
        self.login_window() # 登录窗口
        self.win_list = []  # 已打开的窗口
        self.client = None


    def login_window(self):  # 创建登录窗口
        # 设置窗口背景图
        self.photo = PhotoImage(file="b1.png")
        self.label = Label(self.root, image=self.photo)
        self.label.pack()
        custom_font = font.Font(family="Helvetica", size=18, weight="bold")
        title_label = Label(self.root, text="Pink_House", font=custom_font, fg="pink", bg="black")  # 设置标题字体、颜色等
        title_label.place(x=90, y=52)  # 设置标题位置，x 和 y 需要根据实际窗口调整

        # 创建账号密码标签
        Label(self.root, text='账号', ).place(x=50, y=120)
        Label(self.root, text='密码', ).place(x=50, y=160)

        # 创建输入框
        E1 = Entry(self.root, )
        E1.place(x=110, y=120)
        E2 = Entry(self.root, show="*", )
        E2.place(x=110, y=160)
        # 创建按钮
        Button(self.root, text="注册", command=self.register_window).place(x=120, y=210)
        Button(self.root, text="登录", command=lambda: self.send_data(E1.get(), E2.get())).place(x=200, y=210)
        # self.root.bind("<Key-Return>",self.a)


    def close_window(self):
        self.win_list[0].destroy()
        del self.win_list[0]

    # 创建注册窗口
    def register_window(self):
        if len(self.win_list) > 0: # 如果窗口存在
            self.win_list[0].deiconify() # 显示窗口
            return
        self.reg = Toplevel()
        # 窗口大小
        self.reg.geometry("350x270+430+230")
        # 设置窗口大小固定
        self.reg.resizable(0, 0)
        # 设置窗口标题
        self.reg.title("注册")
        self.win_list.append(self.reg)
        # 设置窗口背景图
        photo = PhotoImage(file="b1.png")
        label = Label(self.reg, image=photo)  # 图片
        label.pack()
        # 创建账号密码标签
        Label(self.reg, text='昵称').place(x=50, y=30)
        Label(self.reg, text='账号').place(x=50, y=70)
        Label(self.reg, text='手机号').place(x=50, y=110)
        Label(self.reg, text='密码').place(x=50, y=150)
        Label(self.reg, text='确认密码').place(x=26, y=190)
        # 创建输入框
        name = Entry(self.reg, )
        name.place(x=110, y=30)
        uid = Entry(self.reg, )
        uid.place(x=110, y=70)
        phone = Entry(self.reg, )
        phone.place(x=110, y=110)
        pwd1 = Entry(self.reg, show="*", )
        pwd1.place(x=110, y=150)
        pwd2 = Entry(self.reg, show="*", )
        pwd2.place(x=110, y=190)
        # 创建按钮
        Button(self.reg, text="确认注册",
               command=lambda: self.send_data(uid.get(), pwd1.get(), pwd2.get(), name.get(),phone.get())).place(
            x=150, y=220)
        # 点击关闭按钮触发事件
        self.reg.protocol("WM_DELETE_WINDOW", lambda: self.close_window())
        # 循环
        self.reg.mainloop()

    def send_data(self, uid, pwd1, pwd2=None, name=None, phone=None):
        """
            发送数据
        :param uid: 用户名
        :param pwd1: 密码
        :param pwd2: 确认密码
        :return:
        """
        if pwd2 == None:
            Message(self.root, text='正在登录，请稍候...', ).place(x=10, y=130)
            self.root.update()
        else:
            Message(self.reg, text='发送请求，请稍候...', ).place(x=10, y=175)
            self.reg.update()
        try:
            self.client = ClientSend()
        except:
            self.messagebox("无法连接到服务器")
            return
        if pwd2 == None:
            data = self.client.login(uid, pwd1)
            if data:
                msg = self.client.get_friends(uid)
                msg1 = self.client.get_rooms(uid)
                msg['room_list'] = msg1
                print(msg)
                self.login_successfully(msg)
            else:
                self.messagebox("账号或密码不正确")
        else:
            data = self.client.register(uid, pwd1, pwd2, name,phone)
            if data == "OK":
                self.messagebox("注册成功，请返回登录")
                self.win_list[0].destroy()
            else:
                self.messagebox(data)

    # 弹窗提示
    def messagebox(self, msg):
        tkinter.messagebox.showinfo(title='提示', message=msg)

    # 登录成功
    def login_successfully(self, data):
        Message(self.root, text='登录成功，正在跳转，请稍候...', ).place(x=10, y=130)
        # 更新窗口
        self.root.update()
        # sleep(2)
        # 关闭登录窗口
        self.root.destroy()
        # 跳转到主窗口
        MainWindow(self.client, data)





if __name__ == '__main__':
    root = Tk()
    Application(root)
    root.mainloop()
