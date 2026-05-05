#
#    K3JSE Pico based deviation meter Meters
#    Copyright (C) 2026  W. Andy Cooper, K3JSE
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#    The author can be contacted by email at k3jse@coolioh.com#


import customtkinter,time
from tkdial import Meter
#from tkinter import messagebox

import serial
from time import sleep

VERSION = "1.03.2 05/05/2026"
R_SAMPLE_RATE = 0
R_SAMPLE_BUFFER = 1
R_SHIFT = 2
R_REF = 3
R_XX = 4
R_X = 5
R_C = 6
R_SCALE = 7
R_SCRATCH = 8
R_VERSION = 9


visible = True
raw = False
stm = False
calibrate = False

app = customtkinter.CTk()
#app.geometry("320x350")
app.geometry("640x550")
app.title('GImeter')


ser = serial.Serial('/dev/ttyACM1')
print(ser.name)

#ser.write(b">h\r")

waiting = ser.in_waiting
while waiting > 0:
    data = ser.read(waiting)
    print("purged serial in:",len(data))
    waiting = ser.in_waiting
print("Starting")

#ser.write(b">m\r")
print("sending commands")
ser.write(b">run\r")
#ser.write(b">avg\r")
ser.write(b">con\r")
#time.sleep(0.5)
#ser.write(b">stm\r")     # calibrate frequency offset to current value
#ser.write(b">str,3,2070\r")     # calibrate frequency offset
#ser.write(b">flp\r")
#sleep(0.5)
#ser.write(b">stm\r")

dev = 0
adc = 0
ferror = 0
fmedian = 2225
adcsum = 0
devsum = 0
adccnt = 0
err = False

def c_r(value):
    if value % 10 < 5:
        return value - (value % 5)
    else:
        return value + (5 - (value % 5))

def r_d(x, base=5):
    return x - (x % base)

def on_closing():
    #if messagebox.askokcancel("Quit", "Do you want to quit?"):
    print("closing commands")
    ser.write(b">bye\r")
    app.destroy()

def idle_loop():
    global adc, dev, ferror, adcsum, devsum, adccnt,raw, err
    ser_in = str(ser.readline()).split(" ")
    #ser_in = str(ser.readline()).split(",")
    if not calibrate:
        print(ser_in)
    try:
        #ferror = int((int(ser_in[5]) - int(ser_in[4])) *5000/1590)
        #ferror = int((int(ser_in[5]) - int(ser_in[4])) *5000/1550)   # RP2350
        if int(ser_in[2]) == 1:
            err = "ovf"
        elif int(ser_in[2]) == 2:
            err = "ufl"
        else:
            err = "none"
        ferror = int(ser_in[4])
        if raw:
            dev = int(ser_in[3])
        else:
            dev = int(ser_in[3])
            if abs(ferror) < 35:
                ferror = 0
        adc = int(ser_in[5])
    except:
        #dev = 0
        print("try exception")
    if calibrate:
        adcsum += adc
        devsum += dev
        adccnt += 1
        if adccnt == 10:
            print("Average:",devsum/adccnt,adcsum/adccnt)
            adccnt = 0
            devsum = 0
            adcsum = 0
        #if 
        #print("update",ser_in[0],ser_in[1])
        #print(dev,adc,ferror)
    app.after(0,update_gauge)


def update_gauge():
    global adc, dev, ferror, raw, err
    #print("update",dev, adc)
    #dev = int(dev * 1.005)
    if err == "ovf":
      meter1.text_color="red"
      meter2.text_color = "red"
    elif err == "ufl":
      meter1.text_color="yellow"
      meter2.text_color = "yellow"  
    else:
        if visible:
            meter1.text_color="white"
            meter2.text_color="white"
        else:
            meter1.text_color="black"
            meter2.text_color="black"
    if dev > 6015:
        dev = 0
        ferror = 0
    if raw:
        meter1.set(dev)
        meter2.set(ferror)
    else:
        meter1.set(r_d(dev,5))
        #meter1.set(c_r(dev))
        meter2.set(c_r(ferror))
    #meter1.set(dev)
    #meter2.set(r_d(adc))
    #meter3.set(adc)
    #meter3.set_mark(10,15,"green")
    #meter3.set(c_r(ferror))
    meter2.set_mark(19,22,"green")
    app.after_idle(idle_loop)



meter1 = Meter(app, radius=270, start=0, end=6000, border_width=10,
               fg="black", text_color="White", start_angle=225, end_angle=-270,
               major_divisions=500, minor_divisions=100,integer=True,
               text_font="DS-Digital 14", scale_color="white", needle_color="white")
meter1.set_mark(0, 12) # set red marking from 140 to 160
meter1.set_mark(12, 18,"yellow") # set red marking from 140 to 160
meter1.set_mark(18, 25,"green") # set red marking from 140 to 160
meter1.set_mark(25, 30,"yellow") # set red marking from 140 to 160
meter1.set_mark(30, 60) # set red marking from 140 to 160
meter1.grid(row=0, column=1, padx=20, pady=30)
#major_divisions=500, minor_divisions=100, text="    ",


#meter3 = Meter(app, radius=270, start=-0, end=4100, border_width=10,
#               fg="black", text_color="white", start_angle=225, end_angle=-270,
#               major_divisions=500, minor_divisions=100,text="\nADC P2P",
#text_font="DS-Digital 14", scale_color="white", needle_color="white")
#meter3.grid(row=0, column=3, padx=20, pady=30)


meter2 = Meter(app, radius=270, start=-5000, end=5000, border_width=10,
               fg="black", text_color="white", start_angle=225, end_angle=-270,
               major_divisions=1000, minor_divisions=250,
text_font="DS-Digital 14", scale_color="white", needle_color="white")
meter2.grid(row=0, column=2, padx=20, pady=30)


def b_visible_event():
    global visible
    #print("button pressed")
    if visible:
        meter1.text_color="black"
        meter2.text_color="black"
        b_visible.configure(text="Show")
        visible = False
    else:
        meter1.text_color="white"
        meter2.text_color="white"
        b_visible.configure(text="Hide")
        visible = True
    #meter1.configure(text_font="DS-Digital 14")

b_visible = customtkinter.CTkButton(app, text="Hide", command=b_visible_event)
b_visible.grid(row=1,column=1)

def b_raw_event():
    global raw
    if raw:
        b_raw.configure(text="Raw")
    else:
        b_raw.configure(text="Filtered")
    raw = not raw

b_raw = customtkinter.CTkButton(app, text="Raw", command=b_raw_event)
b_raw.grid(row=1,column=2)

def b_stm_event():
    global stm
    if stm:
        #print("stm")
        ser.write(b">str,3,2047\r")
        stm = False
    else:
        ser.write(b">stm\r")
        stm = True

b_stm = customtkinter.CTkButton(app, text="STM", command=b_stm_event)
b_stm.grid(row=2,column=1,pady=20)

def b_flp_event():
    ser.write(b">flp\r")

b_flp = customtkinter.CTkButton(app, text="Flip 1106 Display", command=b_flp_event)
b_flp.grid(row=2,column=2,pady=20)

def b_cal_event():
    global calibrate
    if calibrate:
        b_cal.configure(text="Calibrate")
    else:
        b_cal.configure(text="Run")
    calibrate = not calibrate

b_cal = customtkinter.CTkButton(app, text="Calibrate", command=b_cal_event)
b_cal.grid(row=3,column=1,pady=0)


#label = customtkinter.CTkLabel(app, text="Deviation", fg_color="transparent")
#label.grid(row=1,column=1)


#app.after(500, check)  #  time in ms.
#app.bind_all('<Control-c>', quit)
app.protocol("WM_DELETE_WINDOW", on_closing)

#app.after_idle(idle_loop)
idle_loop()
app.mainloop()

