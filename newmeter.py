import customtkinter
from tkdial import Meter

import serial
from time import sleep

app = customtkinter.CTk()
#app.geometry("320x350")
app.geometry("1000x350")
app.title('GImeter')


ser = serial.Serial('/dev/ttyACM1')
print(ser.name)
#ser.readline()
ser.write(b">x\r")

dev = 0
adc = 0
ferror = 0
fmedian = 2106

def idle_loop():
    global adc, dev, ferror
    ser_in = str(ser.readline()).split(",")
    print(ser_in)
    try:
        dev = int(ser_in[1])
        adc = int(ser_in[2])
        ferror = int((int(ser_in[3]) - fmedian) *5000/1755)
    except:
        #dev = 0
        print("exception")
    #print("update",ser_in[0],ser_in[1])
    #print(dev,adc,ferror)
    app.after(0,update_gauge)

def update_gauge():
    global adc, dev, ferror
    #print("update",dev, adc)
    meter1.set(dev)
    #meter1.set(dev)
    meter2.set(adc)
    meter2.set_mark(10,15,"green")
    meter3.set(ferror)
    meter3.set_mark(-25,25,"green")
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
#meter1.set(2500)


meter2 = Meter(app, radius=270, start=-0, end=4100, border_width=10,
               fg="black", text_color="white", start_angle=225, end_angle=-270,
               major_divisions=500, minor_divisions=100,text="\n P2P",
text_font="DS-Digital 14", scale_color="white", needle_color="white")
#meter2.set_mark(0, 12) # set red marking from 140 to 160
#meter2.set_mark(12, 18,"yellow") # set red marking from 140 to 160
#meter2.set_mark(18, 25,"green") # set red marking from 140 to 160
#meter2.set_mark(25, 30,"yellow") # set red marking from 140 to 160
#meter2.set_mark(30, 65) # set red marking from 140 to 160
meter2.grid(row=0, column=2, padx=20, pady=30)


meter3 = Meter(app, radius=270, start=-5000, end=5000, border_width=10,
               fg="black", text_color="white", start_angle=225, end_angle=-270,
               major_divisions=1000, minor_divisions=250,text="\n freq  \nerror",
text_font="DS-Digital 14", scale_color="white", needle_color="red")
#meter2.set_mark(0, 12) # set red marking from 140 to 160
#meter2.set_mark(12, 18,"yellow") # set red marking from 140 to 160
#meter2.set_mark(18, 25,"green") # set red marking from 140 to 160
#meter2.set_mark(25, 30,"yellow") # set red marking from 140 to 160
#meter2.set_mark(30, 65) # set red marking from 140 to 160
meter3.grid(row=0, column=3, padx=20, pady=30)




#meter2 = Meter(app, radius=260, start=0, end=200, border_width=5,
#               fg="black", text_color="white", start_angle=270, end_angle=-360,
#               text_font="DS-Digital 30", scale_color="black", axis_color="white",
#               needle_color="white")
#meter2.set_mark(1, 100, "#92d050")
#meter2.set_mark(105, 150, "yellow")
#meter2.set_mark(155, 196, "red")
#meter2.set(80) # set value
#meter2.grid(row=0, column=0, padx=20, pady=30)

#meter3 = Meter(app, fg="#242424", radius=300, start=0, end=50,
#               major_divisions=10, border_width=0, text_color="white",
#               start_angle=0, end_angle=-360, scale_color="white", axis_color="cyan",
#               needle_color="white",  scroll_steps=0.2)
#meter3.set(15)
#meter3.grid(row=0, column=2, pady=30)

#app.after(1, update_gauge
app.after_idle(idle_loop)
app.mainloop()
