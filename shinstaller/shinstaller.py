import tkinter as tk
import ttkbootstrap as ttk

import sys
import requests
import os
import zipfile

from tkinter                import *
from zipfile                import *
from threading              import Thread
from ttkbootstrap.constants import *
from PIL                    import Image, ImageTk
from os                     import _wrap_close



#sadly this is the closest thing to a C struct
class shInfo:
    program:ttk.StringVar        = ""
    install_dir:ttk.StringVar    = ""
    run_prerequisites:BooleanVar 
    run_build:BooleanVar        
    run_after_install:BooleanVar

    url:str                        = ""
    after_install_win32_dir:str    = ""
    after_install_linux_dir:str    = ""   
    after_install_win32:str        = ""
    after_install_linux:str        = ""   

    output_text:ttk.ScrolledText
    progress:ttk.Floodgauge



def shinstaller_read_file(path:str) -> str:
    file = open(path, "r")
    code = file.read()
    file.close()
    return code

def shinstaller_ui_command(info:shInfo, _cmd:str) -> int:
    _cmd += " > tmp.txt\n"

    msg:str = f"shinstaller command: {_cmd}\n"
    info.output_text.insert(INSERT, msg)
    print(msg)

    #os.system(_cmd)
    r:_wrap_close = os.popen(cmd=_cmd)
    exit_code:int = r._proc.wait()

    output:str = shinstaller_read_file(f"tmp.txt")

    info.output_text.insert(INSERT, output)

    return 1

def shinstaller_msg(msg:str) -> None:
    print(f"shinstaller message: {msg}\n")
    return

def shinstaller_ui_msg(info:shInfo, msg:str) -> None:
    _msg:str = f"shinstaller message: {msg}\n"
    
    info.output_text.insert(INSERT, _msg)
    print(_msg)
    return

def getBool(literal:str) -> bool:
    if (literal == "True" or literal == "true"):
        return True
    else:
        return False

def read_arg(arg:str, info:shInfo, root:Misc) -> None:
    if (arg.startswith("program=")):
        info.program = StringVar(master=root, value=arg.removeprefix("program="))
    elif (arg.startswith("install_dir=")):
        info.install_dir = StringVar(master=root, value=arg.removeprefix("install_dir="))
    elif (arg.startswith("run_prerequisites=")):
        info.run_prerequisites = BooleanVar(master=root, value=getBool(arg.removeprefix("run_prerequisites=")))
    elif (arg.startswith("run_build=")):
        info.run_build = BooleanVar(master=root, value=getBool(arg.removeprefix("run_build=")))
    elif (arg.startswith("url=")):
        info.url = arg.removeprefix("url=")
    elif (arg.startswith("run_after_install=")):
        info.run_after_install = BooleanVar(master=root, value=getBool(arg.removeprefix("run_after_install=")))
    elif (arg.startswith("after_install_win32=")):
        info.after_install_win32 = arg.removeprefix("after_install_win32=")
    elif (arg.startswith("after_install_linux=")):
        info.after_install_linux = arg.removeprefix("after_install_linux=")
    return

def get_info(info:shInfo) -> None:
    shinstaller_msg(f"""
    shInfo:
        program                    : {info.program.get()},
        install_dir                : {info.install_dir.get()}
        run_prerequisites          : {str(info.run_prerequisites.get())}
        run_build                  : {str(info.run_build.get())}
        url                        : {info.url}
        run_after_install          : {info.run_after_install}
        after_install_win32        : {info.after_install_win32}
        after_install_linux        : {info.after_install_linux}
""")

def install(info:shInfo) -> None:
    info.progress["bootstyle"] = "success"#for second attempts


    get_info(info)

    dst_dir:str    = f"{info.install_dir.get()}/{info.program.get()}"
    dst_path:str   = f"{dst_dir}/{info.program.get()}.zip"
    unzip_dir:str  = f"{dst_dir}/{info.program.get()}"
    repo_dir:str   = f"{unzip_dir}/{info.program.get()}"

    shinstaller_ui_command(info, f"mkdir \"{info.install_dir.get()}\"")
    shinstaller_ui_command(info, f"mkdir \"{dst_dir}\"")
    shinstaller_ui_command(info, f"mkdir \"{unzip_dir}\"")#for unzipping

    shinstaller_ui_msg(info, f"destination directory : {dst_dir}")
    shinstaller_ui_msg(info, f"destination path: {dst_path}")

    shinstaller_ui_msg(info, "downloading...")

    info.progress["value"] = 25

    try:
        buffer:requests.Response = requests.get(url=info.url)
    except Exception as exception:
        shinstaller_ui_msg(info, f"exception: {exception}")
        info.progress["bootstyle"] = "warning"
        return

    shinstaller_ui_msg(info, "writing files...")

    info.progress["value"] = 50

    try:
        dst = open(dst_path, "wb")
        dst.write(buffer.content)
        dst.close()
    except Exception as exception:
        shinstaller_ui_msg(info, f"exception: {exception}")
        info.progress["bootstyle"] = "warning"
        return

    shinstaller_ui_msg(info, "extracting...")

    try:
        zip = zipfile.ZipFile(file=dst_path, mode="r")
        zip.extractall(path=unzip_dir)
    except Exception as exception:
        shinstaller_ui_msg(info, f"exception: {exception}")
        info.progress["bootstyle"] = "warning"
        return

    shinstaller_ui_msg(info, f"installing...")

    info.progress["value"] = 75

    cmd:str = ""
    try:
        if (info.run_prerequisites.get() == True):

            info.progress["value"] = 80

            shinstaller_ui_msg(info, "running prerequisites...")

            if (sys.platform == "win32"):
                cmd = f"call \"{repo_dir}/.shci/windows/prerequisites.bat\""
            else:
                cmd = f"sudo bash \"{repo_dir}/.shci/linux/prerequisites.sh\""

            shinstaller_ui_command(info, cmd)


    except Exception as exception:
        shinstaller_ui_msg(info, f"exception: {exception}")
        info.progress["bootstyle"] = "warning"
        return


    shinstaller_ui_msg(info, f"done")

    info.progress["value"] = 100

    return



def main() -> int:#example call: python shinstaller.py
    
    info:shInfo = shInfo()

    #ROOT
    #
    #
    root = ttk.Window(themename="cyborg")
    root.geometry("400x650")
    root.title("Sinho Softworks installer")

    root.rowconfigure(0, weight=1)
    root.rowconfigure(1, weight=4)
    root.columnconfigure(0, weight=1)

    _image = Image.open("media/noise.png")
    icon   = ImageTk.PhotoImage(image=_image)
    root.wm_iconphoto(False, icon)

    #GET INFO
    #
    #
    if (len(sys.argv) > 1):
        for i in range (0, len(sys.argv), 1):
            read_arg(sys.argc[i], info, root)
    else :
        try:
        
            file        = open("shinstaller.txt", "r")
            s_info:list = file.read().split("\n") 
            file.close()
            shinstaller_msg(f"info: {s_info}")
            for i in range (0, len(s_info), 1):
                read_arg(s_info[i], info, root)
        
        except Exception as exception:
            print(f"failed reading shinstaller.txt: {exception}\n")

    get_info(info)


    #SETUP
    #
    #
    f0 = ttk.LabelFrame(master=root, text="setup", bootstyle="primary")
    f0.rowconfigure(0, weight=1)
    f0.rowconfigure(1, weight=1)
    f0.rowconfigure(2, weight=1)
    f0.rowconfigure(3, weight=1)
    f0.rowconfigure(4, weight=1)
    f0.rowconfigure(5, weight=1)
    f0.columnconfigure(0, weight=1)
    f0.columnconfigure(1, weight=2)

    f0.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

    #PROGRAM
    #
    t = ttk.Label(master=f0, text="program", bootstyle="light")
    t.grid(row=0, column=0, padx=5, pady=5, sticky="w")

    t = ttk.Entry(master=f0, textvariable=info.program, bootstyle="light") 
    t.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

    #INSTALL DIR
    #
    t = ttk.Label(master=f0, text="install dir", bootstyle="light")
    t.grid(row=1, column=0, padx=5, pady=5, sticky="w")

    t = ttk.Entry(master=f0, textvariable=info.install_dir, bootstyle="light")
    t.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

    #RUN REQUIREMENTS
    #run .shci/os/requirements.sh
    t = ttk.Label(master=f0, text="run prerequisites (dev)", bootstyle="light")
    t.grid(row=2, column=0, padx=5, pady=5, sticky="w")

    t = ttk.Checkbutton(master=f0, variable=info.run_prerequisites, onvalue=True, offvalue=False, bootstyle="round-toggle-light")
    t.grid(row=2, column=1, padx=5, pady=5, sticky="e")

    #INSTALL
    #just downloads plain files
    t = ttk.Button(master=f0, text="install", bootstyle="outline-toolbutton-primary", command=lambda:Thread(target=install, args=[info]).start())
    t.grid(row=7,  column=1, padx=5, pady=5, sticky="nsew")




    #OUTPUT AND STATUS
    #
    #
    f1 = ttk.LabelFrame(master=root, text="output", bootstyle="success")
    f1.rowconfigure(0, weight=1)
    f1.rowconfigure(1, weight=1)
    f1.columnconfigure(0, weight=1)

    f1.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
    
    #SCROLLED TEXT
    #
    info.output_text = ttk.ScrolledText(master=f1)
    info.output_text.grid(row=0, column=0, padx=5, pady=5, sticky="nsew", )

    #PROGRESS BAR
    #
    info.progress = ttk.Floodgauge(master=f1, text="progress...", bootstyle="success")
    info.progress.grid(row=1, column=0, padx=5, pady=5, sticky="sew")

    root.mainloop()

    return 0


if (__name__ == "__main__"):
    main()