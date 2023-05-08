import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import time
import datetime
import json
import PortModule
import serial
from PIL import Image, ImageTk
import cv2
import os

class NanoPZ(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.title("NanoPZ Motion Control")
        #self.geometry("410x350")
        self.minsize(420, 750) 
        self.maxsize(420, 750)
        self.configure(bg='#222831')
        self.protocol("WM_DELETE_WINDOW", self.exit_program)
        self.FWHM_value = tk.StringVar()
        self.name_value = tk.StringVar(value="None")
        self.c_value = tk.StringVar(value="None")

        # Creation Function
        self.create_menubar()
        self.create_actuator_frame()
        self.create_motion_frame()
        self.create_limit_frame()
        self.create_image_frame()
        
        # Hidden progressbar
        self.progress = ttk.Progressbar(self, orient="horizontal", mode="determinate", length = 100, takefocus=True,)
        self.progress.pack(side='left', padx=10)
        self.progress.pack_forget()
        
        # Initial configure
        if os.path.exists('NanoPZLog.txt'):
            with open('NanoPZLog.txt') as f:
                data = f.read()
            js = json.loads(data)
            self.pos_entry.insert(0, js["pos_entry"])
            self.neg_entry.insert(0, js["neg_entry"])
            self.move_entry.insert(0, js["move_entry"])
            self.step_entry.insert(0, js["step_entry"])
            time_label = tk.Label(self, text="Last time saved: {}".format(js["time_save"]), font=('Arial', 10), fg='white')
            time_label.pack(side='right', padx=10)
            time_label.config(bg='#222831')

            self.posinsys = js["pos_entry"]
            self.neginsys = js["neg_entry"]
            self.offset   = js["offset"]
        else:
            print("Warnning: no configure file")

        # One time set
        all_var = list(self.__dict__.keys())
        for i in all_var:
            if '_label' in i or '_frame' in i:
                self.__dict__[i].config(bg='#393E46')
                self.__dict__[i].config(fg='#F7E3AF')
            if '_button' in i:
                self.__dict__[i].config(bg='#00ADB5')
                            
        self.port_search()
        self.cmap = cv2.COLORMAP_JET
        
    # Define a function to write commands to the actuator
    def write(self, com):
        time.sleep(0.1)
        Actuator.write("{}{}\n\r".format(self.cid_combobox.get(), com).encode())
        print("{}{}\n\r".format(self.cid_combobox.get(), com).encode())
        
    
    # Define a function to write/read commands to the actuator    
    def query(self, com, option=0):
        time.sleep(0.1)
        if option:
            Actuator.write("{}{}\n\r".format(option, com).encode())
        else:
            Actuator.write("{}{}\n\r".format(self.cid_combobox.get(), com).encode())
        try:
            time.sleep(0.1)
            resp = Actuator.readline().split()[-1]
            print(resp)
            if com[:2] == "TP":
                resp = int(resp)+self.offset
            return resp
        except:
            print("Query Error: ", com)
            return False
        
    def create_menubar(self):
        menu_bar = tk.Menu(self)

        # "Settings" 
        settings_menu = tk.Menu(menu_bar, tearoff=0)
        self.connection_menu = tk.Menu(settings_menu, tearoff=0)
        self.connection_menu.add_command(label="Not working")
        settings_menu.add_cascade(label="COM PORT", menu=self.connection_menu)
        settings_menu.add_command(label="Rescan", command=self.port_search)
        settings_menu.add_command(label="Exit", command=self.exit_program)                

        # "About" 
        about_menu = tk.Menu(menu_bar, tearoff=0)
        about_menu.add_command(label="About")
        
        menu_bar.add_cascade(label="Settings", menu=settings_menu)
        menu_bar.add_cascade(label="About", menu=about_menu)        
        self.config(menu=menu_bar)
    
    def create_actuator_frame(self):
        self.actuator_frame = tk.LabelFrame(self, text="Actuator", bg = 'snow')
        self.actuator_frame.pack(fill="both", expand="no", padx=10, pady=10)
                              
        # "Controller ID"
        self.cid_label = tk.Label(self.actuator_frame, text="Controller")
        self.cid_label.grid(row=0, column=0, padx=5, pady=5)

        # "Controller ID" Combo box
        self.cid_combobox = ttk.Combobox(self.actuator_frame, values=["N/A"], justify = 'center', width=5, state="readonly")
        self.cid_combobox.option_add('*TCombobox*Listbox.Justify', 'center') 
        self.cid_combobox.grid(row=0, column=1, padx=5, pady=5)
        self.cid_combobox.bind("<<ComboboxSelected>>", self.on_select)
        self.cid_combobox.current(0)

        # "Actuator Name" 
        self.name_label = tk.Label(self.actuator_frame, text="Name")
        self.name_label.grid(row=0, column=2, padx=5, pady=5)
        self.name_value_label = tk.Label(self.actuator_frame, textvariable = self.name_value, width=10)
        self.name_value_label.grid(row=0, column=3, pady=5) 
        
        # Motor status" 
        self.c_status_label = tk.Label(self.actuator_frame, text="Motor status")
        self.c_status_label.grid(row=2, column=0, padx=5, pady=5)
        self.motor_buton = tk.Button(self.actuator_frame, text="Motor Off", command= self.motor_switch, bg='grey', fg='white', width=8)
        self.motor_buton.grid(row=2, column=1, padx=5, pady=5)

        # "Current Postion" 
        self.c_label = tk.Label(self.actuator_frame, text="Current Postion", width = 13)
        self.c_label.grid(row=4, column=0, padx=5, pady=5)
        self.c_label.bind("<Leave>", self.on_mouse_leave)
        self.c_label.bind("<Enter>", self.on_mouse_enter)
        self.c_postition_label = tk.Label(self.actuator_frame, textvariable = self.c_value, width=10)
        self.c_postition_label.grid(row=4, column=1, padx=5, pady=5)
        
        # "Zero adjustment" 
        self.zero_adj_button = tk.Button(self.actuator_frame, text="Zero Adjust", command= self.zero_adjust)
        self.zero_adj_button.grid(row=4, column=2, padx=5, pady=5)
        
        # "Auto Tune" 
        # self.auto_tune_buton = tk.Button(self.actuator_frame, text="Auto Tune ", width=10, command= self.auto_tune, bg='grey', fg='white')
        # self.auto_tune_buton.grid(row=4, column=3, padx=5, pady=5)

        # "FWHM update" 
        self.FWHM_label = tk.Label(self.actuator_frame, text="FWHM")
        self.FWHM_label.grid(row=2, column=2, padx=5, pady=5)
        self.FWHM_value_label = tk.Label(self.actuator_frame, textvariable = self.FWHM_value, width=10)
        self.FWHM_value_label.grid(row=2, column=3, pady=5)
    
    def create_motion_frame(self):
        self.motion_frame = tk.LabelFrame(self, text="Motion Control  (1 step input ≅ 10 nm)")
        self.motion_frame.pack(fill="both", expand="no", padx=10, pady=10)
        
        # "Move function"
        self.move_label = tk.Label(self.motion_frame, text="Move to position (+/-)")
        self.move_label.grid(row=0, column=0, padx=5, pady=5)
        self.move_entry = tk.Entry(self.motion_frame, width=10, justify='center')
        self.move_entry.grid(row=0, column=1, padx=5, pady=5)
        self.move_button = tk.Button(self.motion_frame, text="Move", command= self.move_function, bg='#453750', width=5)
        self.move_button.grid(row=0, column=2, padx=5, pady=5)
        
        # "Step function"
        self.step_entry = tk.Entry(self.motion_frame, width=8, justify='center')
        self.step_entry.grid(row=0, column=3, padx=5, pady=5)
        self.step_button0 = tk.Button(self.motion_frame, text= '➕', command = lambda arg='➕': self.step_function(arg), width = 3, font=('Arial', 8))
        self.step_button0.grid(row=0, column=4, padx=3, pady=5)
        self.step_button1 = tk.Button(self.motion_frame, text= '➖', command = lambda arg='➖': self.step_function(arg), width = 3, font=('Arial', 8))
        self.step_button1.grid(row=0, column=5, padx=3, pady=5)

        # "Move function"
        self.speed_label = tk.Label(self.motion_frame, text="Set speed (step/s)")
        self.speed_label.grid(row=1, column=0, padx=5, pady=5)
        
        self.speed_combobox = ttk.Combobox(self.motion_frame, values=["-48k", "-10k", "-2k", "-400", "-80", "-16", "-3.2", "0", "3.2", "16", "80", "400", "2k", "10k", "48k"],
                                           justify = 'center', width=7, state="readonly")
        self.speed_combobox.option_add('*TCombobox*Listbox.Justify', 'center') 
        self.speed_combobox.grid(row=1, column=1, padx=5, pady=5)
        self.speed_combobox.current(7)
        
        self.speed_button = tk.Button(self.motion_frame, text="Run", command= self.jog_function, bg='#453750', width=5)
        self.speed_button.grid(row=1, column=2, padx=1, pady=5)

        self.speed_stop_button = tk.Button(self.motion_frame, text="Stop", command= self.stop_jog_function, bg='#453750', width=5)
        self.speed_stop_button.grid(row=1, column=3, padx=1, pady=5)
    
    def create_limit_frame(self):
        self.limit_frame = tk.LabelFrame(self, text="Travel Limits")
        self.limit_frame.pack(fill="both", expand="no", padx=10, pady=10)
        
        # "Limit Label"
        self.pos_label = tk.Label(self.limit_frame, text="Positive Limit", width = 10)
        self.pos_label.grid(row=0, column=0, padx=10, pady=5)
        self.pos_label.bind("<Leave>", self.on_mouse_leave)
        self.pos_label.bind("<Enter>", self.on_mouse_enter)
        self.neg_label = tk.Label(self.limit_frame, text="Negative Limit", width = 10)
        self.neg_label.grid(row=1, column=0, padx=10, pady=5) 
        
        # "Limit Entry"
        self.pos_entry = tk.Entry(self.limit_frame, width=20)
        self.pos_entry.grid(row=0, column=1, padx=5, pady=5)
        self.neg_entry = tk.Entry(self.limit_frame, width=20)
        self.neg_entry.grid(row=1, column=1, padx=5, pady=5)
        
        self.set_limit_button = tk.Button(self.limit_frame, text="Update Controller Limit", command= self.limit_function, bg='#453750', height=2)
        self.set_limit_button.grid(row=0, column=2, rowspan=2, padx=5, pady=5)
    
    def limit_function(self):
        try:
            if int(self.pos_entry.get())>int(self.neg_entry.get()) and int(self.pos_entry.get()) < 10000001 and int(self.pos_entry.get()) > -1 and int(self.neg_entry.get()) < 1 and int(self.neg_entry.get()) > -10000001:
                self.set_limit()
                self.posinsys = self.pos_entry.get()
                self.neginsys = self.neg_entry.get()
                messagebox.showinfo("Update Limits Control", "Done")
                return True
            else:
                messagebox.showerror("Update Limits Control", "Wrong Input\nPositive = [0,10000000]\nNegative=[-10000000,0]")
                return False
        except:
            messagebox.showerror("Update Limits Control", "Error")
            return False

    def set_limit(self):
        self.write("SR{}".format(self.pos_entry.get()))
        self.write("SL{}".format(self.neg_entry.get()))        
        self.write("SM")
        print("------ Limit set ------")

    def create_image_frame(self):
        self.image_frame = tk.LabelFrame(self, text="Mask Fit")
        self.image_frame.pack(fill="both", padx=10, pady=10)

        # Color Map image (fixed)
        self.cmap_bar_img = cv2.imread("cmap_jet.png")
        self.cmap_bar_img = cv2.cvtColor(self.cmap_bar_img, cv2.COLOR_BGR2RGB)
        self.cmap_bar_img = cv2.resize(self.cmap_bar_img, (350, 15), interpolation=cv2.INTER_AREA)
        self.cmap_bar_img = Image.fromarray(self.cmap_bar_img)        
        self.cmap_bar_img = ImageTk.PhotoImage(self.cmap_bar_img)      
        cmap_bar = tk.Label(self.image_frame, image = self.cmap_bar_img)
        cmap_bar.pack(pady=3)

        # Mask fit image
        self.image_box = tk.Label(self.image_frame)
        self.image_box.pack(pady=3)

    def update_image(self, img_gauss):
        mask_gauss_scaled = cv2.normalize(img_gauss, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
        mask_gauss_scaled=cv2.applyColorMap(mask_gauss_scaled, self.cmap)
        
        self.img = Image.fromarray(mask_gauss_scaled)        
        self.img = ImageTk.PhotoImage(self.img)
        self.image_box.config(image=self.img)
        

    def step_function(self, desc):      #********        
        value = int(self.step_entry.get()) if desc == '➕' else -int(self.step_entry.get())
        self.write("PR{}".format(value))
        self.c_value.set(self.query("TP?"))

        self.update()
        print("------ StepMove ------")
        
    def move_function(self):            #********        
        position_relative = int(self.move_entry.get())-int(self.query("TP?")) 
        self.write("PR{}".format(position_relative))
        self.c_value.set(self.query("TP?"))

        self.update()
        print("------ MoveTo ------")

    def jog_function(self):
        if self.motor_buton['text'] == "Motor On":
            speed = self.speed_combobox.current()-7
            self.write("JA{}".format(speed))
            print("Speed = {}".format(speed))
            self.speed_button.config(bg="#16FF00")
            self.speed_combobox.configure(state="disable")
            self.update()
            print("------ Jogging ------")

    def stop_jog_function(self):
        self.write("ST")
        print("Stop = {}".format(self.speed_combobox.current()-7))
        self.speed_button.config(bg="#00ADB5")
        self.speed_combobox.configure(state="readonly")
        self.update()
        print("------ Stop ------")
         
    def motor_switch(self):
        if self.motor_buton['text'] == "Motor Off":
            self.write("MO")
            self.motor_buton['text'] = ("Motor On")
            self.motor_buton.config(bg="#16FF00")
            self.motor_buton.config(fg="black")
            self.c_value.set(self.query("TP?"))
            print("------ Motor On ------")
        else:
            #if self.auto_tune_buton['text'] == "Auto Tune":
            #    self.auto_tune()
            self.write("MF")
            self.motor_buton['text'] = ("Motor Off")
            self.motor_buton.config(bg="#F9CB40")
            self.motor_buton.config(fg="black")
            self.c_value.set(self.query("TP?"))
            print("------ Motor Off ------")
        self.update()
    
    def zero_adjust(self):              
        self.write("OR")
        self.c_value.set(int(self.query("TP?")))
        print("------ Zero Adj ------")
        
    def on_select(self, event):
        selected_option = self.cid_combobox.get()

        self.set_limit()
        self.c_value.set(self.query("TP?"))
        self.name_value.set(self.name_dict[selected_option])        
        self.update()
        print("Selected option:", selected_option)  
        
    def port_search(self):
        # Call "PortModule"
        a = PortModule.serial_ports()
        self.connection_menu.delete(0, "end")
        if "Actuator" in globals(): a.append(Actuator.port)
        # self.connection_menu.add_command(label='Test', command=lambda label='Test': self.select_port(label))
        for i in a:
            self.connection_menu.add_command(label=i, command=lambda label=i: self.select_port(label))

    def select_port(self, label):
        global Actuator
        
        if "Actuator" in globals(): Actuator.close()
        Actuator = PortModule.ConnectPort(label)         
        new_cid_options = []
        self.name_dict = {}
        
        # start the progress bar
        self.progress.pack(side='left', padx=10)
        self.pb_movement()

        for i in range(20):
            return_word =  self.query("ID?", str(i))
            # return_word = 1
            if return_word:
                new_cid_options.append(i)
                self.name_dict[str(i)] = return_word
                break
        if len(new_cid_options) == 0:
            new_cid_options.append("N/A")
            self.name_dict["N/A"] = "None"
        messagebox.showinfo("COM PORT", label)
        
        # reset the progress bar
        self.progress['value'] = 0
        self.progress.pack_forget()       
        self.cid_combobox['values'] = new_cid_options
        self.cid_combobox.current(0)
        self.on_select(0)

        self.write("MF")
        self.motor_buton['text'] = ("Motor Off")
        self.motor_buton.config(bg="#DF3B57")
        #self.auto_tune_buton['text'] = ("Auto Tune ")
        #self.auto_tune_buton.config(bg="#DF3B57")
        cp = self.query("TP?")-self.offset
        self.offset = self.offset-cp
        self.c_value.set(cp+self.offset)
        print("------ Motor Off ------")
    
    def save_setting(self):
        f = self.limit_function()
        cp = self.query("TP?")
        now = datetime.datetime.now()
        if f:
            details = {"time_save"  : now.strftime('%Y-%m-%d %H:%M:%S'),
                       "pos_entry"  : self.pos_entry.get(),
                       "neg_entry"  : self.neg_entry.get(),
                       "move_entry" : self.move_entry.get(),
                       "step_entry" : self.step_entry.get(),
                       "offset"     : cp}
            
            with open('NanoPZLog.txt', 'w') as convert_file:
                convert_file.write(json.dumps(details, indent = 4))
            messagebox.showinfo("Save Configuration", "Done")
        else:
            details = {"time_save"  : now.strftime('%Y-%m-%d %H:%M:%S'),
                       "pos_entry"  : "1000000",
                       "neg_entry"  : "-1000000",
                       "move_entry" : self.move_entry.get(),
                       "step_entry" : self.step_entry.get(),
                       "offset"     : cp}
            
            with open('NanoPZLog.txt', 'w') as convert_file:
                convert_file.write(json.dumps(details, indent = 4))
            messagebox.showinfo("Save Configuration", "Warning: Error Limit")

    def on_mouse_leave(self, event):
        self.pos_label['text'] = "Positive Limit"
        self.neg_label['text'] = "Negative Limit"
        self.c_label['text']   = "Current Postion"

    def on_mouse_enter(self, event):
        self.pos_label['text'] = self.posinsys
        self.neg_label['text'] = self.neginsys
        self.c_label['text']   = self.offset
        
    def exit_program(self):        
        if messagebox.askokcancel("Exit", "Are you sure you want to exit?"):            
            if "Actuator" in globals():           
                self.write("MF")
                self.save_setting()
                Actuator.close()
                print('------ Close Port ------')
            self.destroy()
        
    def pb_movement(self):
        if self.progress['value'] < 100:
            self.progress['value'] += 20
        else:
            return False
        self.after(100, self.pb_movement)
        
    def update_FWHM(self, FWHM):
        self.FWHM_value.set(FWHM)
        
    def call_param(self):
        if "Actuator" in globals(): return [Actuator, self.c_value]
        return False

    def auto_tune(self):
        if self.motor_buton['text'] == "Motor On":
            self.stop_jog_function()
            if self.auto_tune_buton['text'] == "Auto Tune ":
                self.auto_tune_buton['text'] = ("Auto Tune")
                self.auto_tune_buton.config(bg="#16FF00")
                self.auto_tune_buton.config(fg="black")
                print("------ Auto Tune On ------")
                all_var = list(self.__dict__.keys())
                for i in all_var:
                    if '_button' in i:
                        self.__dict__[i].configure(state="disabled")
            else:
                self.auto_tune_buton['text'] = ("Auto Tune ")
                self.auto_tune_buton.config(bg="#F9CB40")
                self.auto_tune_buton.config(fg="black")
                print("------ Auto Tune Off ------")
                all_var = list(self.__dict__.keys())
                for i in all_var:
                    if '_button' in i:
                        self.__dict__[i].configure(state="normal")
        self.update()

if __name__ == "__main__":
    print(">> App Start")
    app = NanoPZ()
    app.mainloop()
    # print(app.offset)









































'''
    def create_step_button(self):
        num = 0
        for i in ['➕', '➖']:
            step_buton = tk.Button(self.motion_frame, text= i, command = lambda arg=i: self.step_function(arg), width = 3, font=('Arial', 8), bg='#FBD1A2')
            step_buton.grid(row=0, column=4+num, padx=3, pady=5)
            num +=1
'''

