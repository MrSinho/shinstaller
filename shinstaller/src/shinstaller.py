import tkinter as tk
from tkinter import *
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

import sys



#sadly this is the closest thing to a C struct
class shInfo:
    program:str                 = ""
    install_dir:ttk.StringVar   = ""
    run_requirements:BooleanVar 
    run_build:BooleanVar        
    
    output_text:ttk.StringVar  = ""
    percentage:IntVar          = 0



def shinstaller_msg(msg:str) -> None:
    print(f"shinstaller message: {msg}\n")
    return

def getBool(literal:str) -> bool:
    if (literal == "True" or literal == "true"):
        return True
    else:
        return False

def read_arg(arg:str, info:shInfo, root:Misc) -> None:
    if (arg.startswith("program=")):
        info.program = arg.removeprefix("program=")
    elif (arg.startswith("install_dir=")):
        info.install_dir = arg.removeprefix("install_dir=")
    elif (arg.startswith("run_requirements=")):
        info.run_requirements = BooleanVar(master=root, value=getBool(arg.removeprefix("run_requirements=")))
    elif (arg.startswith("run_build=")):
        info.run_build = BooleanVar(master=root, value=getBool(arg.removeprefix("run_build=")))
    return


def install(info:shInfo) -> None:
    url:str = f"https://github.com/mrsinho/{info.program}/latest"
    shinstaller_msg(f"downloading {url}...")

    return



def main() -> int:
    
    info:shInfo = shInfo()

    #ROOT
    #
    #
    root = ttk.Window(themename="cyborg")
    root.geometry("400x700")
    root.title("Sinho Softworks installer")

    root.rowconfigure(0, weight=1)
    root.rowconfigure(1, weight=4)
    root.columnconfigure(0, weight=1)

    #GET INFO
    #
    #
    if (len(sys.argv) > 1):
        for i in range (0, len(sys.argv), 1):
            read_arg(sys.argc[i], info, root)
    else :
        try:
        
            file        = open("info.txt", "r")
            s_info:list = file.read().split("\n") 
            file.close()
            shinstaller_msg(f"info: {s_info}")
            for i in range (0, len(s_info), 1):
                read_arg(s_info[i], info, root)
        
        except:
            print("failed reading info.txt\n")

    shinstaller_msg(f"""
    shInfo:
        program          : {info.program},
        install_dir      : {info.install_dir}
        run_requirements : {str(info.run_requirements.get())}
        run_build        : {str(info.run_build.get())}
""")


    #SETUP
    #
    #
    f0 = ttk.LabelFrame(master=root, text="setup", bootstyle="primary")
    f0.rowconfigure(0, weight=1)
    f0.rowconfigure(1, weight=1)
    f0.rowconfigure(2, weight=1)
    f0.rowconfigure(3, weight=1)
    f0.rowconfigure(4, weight=1)
    f0.columnconfigure(0, weight=1)
    f0.columnconfigure(1, weight=2)

    f0.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

    #PROGRAM
    #
    l = ttk.Label(master=f0, text="program", bootstyle="light")
    l.grid(row=0, column=0, padx=5, pady=5, sticky="w")

    m = ttk.Combobox(master=f0, values=info.program, bootstyle="light") 
    m.insert(0, info.program)
    m.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

    #INSTALL DIR
    #
    l = ttk.Label(master=f0, text="install dir", bootstyle="light")
    l.grid(row=1, column=0, padx=5, pady=5, sticky="w")

    m = ttk.Entry(master=f0, bootstyle="light")
    m.insert(0, info.install_dir)
    m.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

    #RUN REQUIREMENTS
    #run .shci/os/requirements.sh
    l = ttk.Label(master=f0, text="run requirements", bootstyle="light")
    l.grid(row=2, column=0, padx=5, pady=5, sticky="w")

    b = ttk.Checkbutton(master=f0, variable=info.run_requirements, bootstyle="round-toggle-light")
    b.grid(row=2, column=1, padx=5, pady=5, sticky="e")

    #RUN BUILD
    #run .shci/os/build.sh (doesn't matter if something fails)
    l = ttk.Label(master=f0, text="run build", bootstyle="light")
    l.grid(row=3, column=0, padx=5, pady=5, sticky="w")

    b = ttk.Checkbutton(master=f0, var=info.run_build, bootstyle="round-toggle-light")
    b.grid(row=3, column=1, padx=5, pady=5, sticky="e")


    #INSTALL
    #just downloads plain files
    i = ttk.Button(master=f0, text="install", bootstyle="outline-toolbutton-primary", command=lambda:install(info))
    i.grid(row=4,  column=1, padx=5, pady=5, sticky="nsew")

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
    t = ttk.ScrolledText(master=f1)
    t.grid(row=0, column=0, padx=5, pady=5, sticky="nsew", )

    #PROGRESS BAR
    #
    h = ttk.Floodgauge(master=f1, value=info.percentage, text="progress...", bootstyle="success")
    h.grid(row=1, column=0, padx=5, pady=5, sticky="sew")

    root.mainloop()

    return 0


if (__name__ == "__main__"):
    main()