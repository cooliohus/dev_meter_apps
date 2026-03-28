import customtkinter
from tkdial import Meter
#from tkinter import messagebox

import serial
from time import sleep

app = customtkinter.CTk()
#app.geometry("320x350")
app.geometry("1000x350")
app.title('GImeter')


ser = serial.Serial('/dev/ttyACM1')
print(ser.name)

ser.write(b">h\r")

waiting = ser.in_waiting
while waiting > 0:
    data = ser.read(waiting)
    print("purged serial in:",len(data))
    waiting = ser.in_waiting
print("Starting")

#ser.write(b">m\r")
print("sending commands")
ser.write(b">run\r")
ser.write(b">con\r")
ser.write(b">flp\r")
#sleep(0.5)
#ser.write(b">stm\r")

dev = 0
adc = 0
ferror = 0
fmedian = 2225
adcsum = 0
adccnt = 0

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
    global adc, dev, ferror, adcsum, adccnt
    ser_in = str(ser.readline()).split(" ")
    #ser_in = str(ser.readline()).split(",")
    print(ser_in)
    try:
        dev = int(ser_in[2])
        adc = int(ser_in[3])
        ferror = int((int(ser_in[5]) - int(ser_in[4])) *5000/1755)
        if abs(ferror) < 35:
            ferror = 0
    except:
        #dev = 0
        print("try exception")
    #adcsum += adc
    #adccnt += 1
    #if adccnt == 25:
    #    print("Average:",adcsum/adccnt)
    #    adccnt = 0
    #    adcsum = 0
    #if 
    #print("update",ser_in[0],ser_in[1])
    #print(dev,adc,ferror)
    app.after(0,update_gauge)


def update_gauge():
    global adc, dev, ferror
    #print("update",dev, adc)
    meter1.set(r_d(dev,5))
    #meter1.set(dev)
    #meter2.set(r_d(adc))
    meter2.set(adc)
    meter2.set_mark(10,15,"green")
    meter3.set(c_r(ferror))
    meter3.set_mark(18,23,"green")
    app.after_idle(idle_loop)



meter1 = Meter(app, radius=270, start=0, end=6000, border_width=10,
               fg="black", text_color="white", start_angle=225, end_angle=-270,
               major_divisions=500, minor_divisions=100, text="    ",
               text_font="DS-Digital 14", scale_color="white", needle_color="white")
meter1.set_mark(0, 12) # set red marking from 140 to 160
meter1.set_mark(12, 18,"yellow") # set red marking from 140 to 160
meter1.set_mark(18, 25,"green") # set red marking from 140 to 160
meter1.set_mark(25, 30,"yellow") # set red marking from 140 to 160
meter1.set_mark(30, 60) # set red marking from 140 to 160
meter1.grid(row=0, column=1, padx=20, pady=30)


meter2 = Meter(app, radius=270, start=-0, end=4100, border_width=10,
               fg="black", text_color="white", start_angle=225, end_angle=-270,
               major_divisions=500, minor_divisions=100,text="\n ADC P2P",
text_font="DS-Digital 14", scale_color="white", needle_color="white")
meter2.grid(row=0, column=3, padx=20, pady=30)


meter3 = Meter(app, radius=270, start=-5000, end=5000, border_width=10,
               fg="black", text_color="white", start_angle=225, end_angle=-270,
               major_divisions=1000, minor_divisions=250,text="\n freq  \nerror",
text_font="DS-Digital 14", scale_color="white", needle_color="white")
meter3.grid(row=0, column=2, padx=20, pady=30)



#app.after(500, check)  #  time in ms.
#app.bind_all('<Control-c>', quit)
app.protocol("WM_DELETE_WINDOW", on_closing)

#app.after_idle(idle_loop)
idle_loop()
app.mainloop()
