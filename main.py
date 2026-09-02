# imports 
from tkinter import *
from threading import *
from sqlite3 import *
import re
import os
# tk init
root = Tk()
root.title("contacts")
root.geometry("1000x1000")
root.config(bg="white")
root.grid_columnconfigure(0,weight=1)
root.grid_columnconfigure(1,weight=1)
root.grid_columnconfigure(2,weight=1)
root.minsize(1300,600)

# sqlite init
try:
    cnn = connect(fr"{os.path.splitdrive(os.path.abspath(__file__))[0]}"+r"\contact_with_sqlite_and_tk_and_venv\database.db")
except OperationalError as err:
    print("خطا در اتصال به دیتابیس: ",err.sqlite_errorname)
else:
    print("database connection sucessful!")
cur = cnn.cursor()
cnn.execute("""
CREATE TABLE IF NOT EXISTS "contacts" (
	"id"	INTEGER NOT NULL UNIQUE,
	"name"	TEXT NOT NULL,
	"phoneNumber"	TEXT NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT)
);
""")
cnn.commit()

# variable
getName = StringVar()
getPhoneNumber = StringVar()

# classes
class User:
    def __init__(self,name,phoneNumber):
        self.name = name
        self.phoneNumber = phoneNumber
        self.pattern = r"^09[0-9]{9}$"
    def save(self):
        if re.match(self.pattern,self.phoneNumber):
            row = cur.execute("select * from contacts where name=?",(self.name,)).fetchone()
            if not row:
                cur.execute("insert into contacts(name,phoneNumber) values (?,?)",(self.name,self.phoneNumber))
                cnn.commit()
                result.config(text="!!مخاطب ذخیره شد",fg="green")
                t = Timer(5,lambda:result.config(text="",fg="black"))
                t.start()
            else:
                result.config(text="!مخاطبی با این اسم وجود دارد",fg="black")
                t = Timer(5,lambda:result.config(text=""))
                t.start()
            getAllContacts()
        else:
            result.config(text="!!فرمت شماره تلفن نادرست است",fg="red")
            t = Timer(5,lambda:result.config(text=""))
            phoneNumber.delete(0,END)
            t.start()

    def delete(self):
        row = cur.execute("select * from contacts where name=?",(self.name,)).fetchone()
        if not row:
            result.config(text="!!مخاطبی با این نام وجود ندارد",fg="black")
            t = Timer(5,lambda:result.config(text="",fg="black"))
            t.start()
        else:
            newWin = Toplevel(root)
            Label(newWin,text=f"آیا مطمئنی {row[1]} رو با شماره {row[2]} حذف کنی؟؟").grid(row=0,column=0,columnspan=2)
            Button(newWin,text="بله",command=lambda:dt(self.name,newWin),fg="green").grid(row=1,column=0)
            Button(newWin,text="خیر",command=lambda:newWin.destroy(),fg="red").grid(row=1,column=2)
            newWin.mainloop()
    def search(self):
        row = cur.execute("select * from contacts where name=?",(self.name,)).fetchone()
        if row:
            result.config(text=f"""
ایدی: {row[0]}
اسم: {row[1]}
شماره تلفن: {row[2]}
""")  
            t = Timer(10,lambda:result.config(text=""))
            t.start()
        else:
            result.config(text="!مخاطبی با این اسم وجود ندارد",fg="black")
            t = Timer(5,lambda:result.config(text=""))
            t.start()
    def printData(self):
        print(self.name,self.phoneNumber)
    def update(self):
        row = cur.execute("select * from contacts where name=?",(self.name,)).fetchone()
        if row:
            uName= StringVar()
            uPhoneNumber = StringVar()
            newWin = Toplevel(root)
            newWin.title("بروزرسانی")
            newWin.grid_columnconfigure(1,weight=1)
            newWin.grid_columnconfigure(2,weight=1)
            newWin.grid_columnconfigure(3,weight=1)

            Label(newWin,text=":اسم جدید").grid(row=0,column=3,sticky="e")
            newName = Entry(newWin,textvariable=uName)
            newName.grid(row=0,column=3,sticky="e",padx=(0,90))

            Label(newWin,text=":شماره تلفن جدید").grid(row=0,column=2,sticky="e")
            newPhoneNumber = Entry(newWin,textvariable=uPhoneNumber)
            newPhoneNumber.grid(row=0,column=2,sticky="e",padx=(0,90))

            Button(newWin,text="بروزرسانی",command=lambda:upToDate(uName.get(),uPhoneNumber.get(),self.name,newWin)).grid(row=0,columnspan=1)
            newWin.mainloop()
        else:
            result.config(text="!مخاطبی با این اسم وجود ندارد",fg="black")
            t = Timer(5,lambda:result.config(text=""))
            t.start()
    
        
            
        
# functions
def dt(name,window):
    window.destroy()
    cur.execute("delete from contacts where name=?",(name,))
    cnn.commit()
    print("dt",getAllContacts())
    result.config(text="!!مخاطب با موفقیت حذف شد",fg="green")
    t = Timer(3,lambda:result.config(text="",fg="black"))
    t.start()
def upToDate(newName,newPhoneNumber,oldName,window):
    window.destroy()
    cur.execute("update contacts set name=?,phoneNumber=? where name=?",(newName,newPhoneNumber,oldName))
    cnn.commit()
    print("upToDate",getAllContacts())
    result.config(text="!مخاطب با موفقیت بروزرسانی شد",fg="green")
    t = Timer(5,lambda:result.config(text="",fg="black"))
    t.start()

# routes
def route(where):
    obj = User(getName.get(),getPhoneNumber.get())
    match where:
        case "printData":
            obj.printData()
        case "save":
            if getName.get() and getPhoneNumber.get():
                obj.save()
            else:
                result.config(text="!برای ذخیره مخاطب هردو فیلد را پر کنید",fg="red")
                t = Timer(3,lambda:result.config(text="",fg="black"))
                t.start()
        case "delete":
            if not getName.get():
                result.config(text="!وارد کردن اسم الزامی میباشد",fg="red")
                t = Timer(3,lambda:result.config(text="",fg="black"))
                t.start()  
            else:
                obj.delete()
        case "search":
            if not getName.get():
                result.config(text="!وارد کردن اسم الزامی میباشد",fg="red")
                t = Timer(3,lambda:result.config(text="",fg="black"))
                t.start()  
            else:
                obj.search()
        case "update":
            if not getName.get():
                result.config(text="!وارد کردن اسم الزامی میباشد",fg="red")
                t = Timer(3,lambda:result.config(text="",fg="black"))
                t.start() 
            else:
                obj.update()
        case _:
            pass
    name.delete(0,END)
    phoneNumber.delete(0,END)

# header
Label(root,text="!!به دفترچه مخاطبین خوش آمدید",bg="white",font="vazir").grid(row=0,column=0,columnspan=4)
result = Label(root,text="",bg="white",fg="black",font=("vazir",15,"bold"))
result.grid(row=1,column=0,columnspan=4)   



# add contact
Label(root,text=":اسم",bg="white",font=("vazir",15)).grid(row=2,column=2,sticky="e")
name = Entry(root,textvariable=getName,font=("vazir",15))
name.grid(row=2,column=2,columnspan=2)
Label(root,text=":شماره تلفن",bg="white",font=("vazir",15)).grid(row=2,column=1,sticky="e")
phoneNumber = Entry(root,textvariable=getPhoneNumber,font=("vazir",15))
phoneNumber.grid(row=2,column=1,columnspan=1)


Button(root,text="ذخیره",command=lambda:route("save"),font=("vazir",15),width=8).grid(row=2,column=0,sticky="e")
Button(root,text="حذف کردن",command=lambda:route("delete"),font=("vazir",15),width=8).grid(row=2,column=0,sticky="e",padx=(0,130))
Button(root,text="جست و جو",command=lambda:route("search"),font=("vazir",15),width=8).grid(row=2,column=0,sticky="w",padx=(110,0))
Button(root,text="آپدیت",command=lambda:route("update"),font=("vazir",15),width=8).grid(row=2,column=0,sticky="w")

Label(root,text=":لیست مخاطبین شما",font=("vazir",15),bg="white").grid(row=3,column=2,sticky="e")
frame = Frame(root,bg="white")
frame.grid(row=4,column=0,columnspan=4)
def getAllContacts():
    for widget in frame.winfo_children():
        widget.destroy()
    Label(frame,text="آیدی",font=("vazir",15),bg="white").grid(row=0,column=3,padx=(400,0))
    Label(frame,text="اسم",font=("vazir",15),bg="white").grid(row=0,column=2)
    Label(frame,text="شماره تلفن",font=("vazir",15),bg="white").grid(row=0,column=1,padx=(0,400))
    rows = cur.execute("select * from contacts").fetchall()
    r = 1
    for row in rows:
        Label(frame,text=f"{row[0]}",bg="white",font=("vazir",10)).grid(row=r,column=3,padx=(400,0))
        Label(frame,text=f"{row[1]}",bg="white",font=("vazir",10)).grid(row=r,column=2)
        Label(frame,text=f"{row[2]}",bg="white",font=("vazir",10)).grid(row=r,column=1,padx=(0,400))
        r += 1
    return True

getAllContacts()
# mainloop
root.mainloop()
