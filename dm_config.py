import sys, getopt, serial, time

ser_device = '/dev/ttyACM0'  # default device
cmd = ''                     # optional command
mode = 'run'                 # mode = run or avg

args = sys.argv[1:]
options = "hd:c:m:o:p:s:"
long_options = ["help", "dev=", "cmd=", "mode=", "offset=", "profile=", "scale="]

try:
    arguments, values = getopt.getopt(args, options, long_options)
    #arguments, values = getopt.getopt(args, options)
    for currentArg, currentVal in arguments:
        if currentArg in ("-h", "--help"):
            print("Showing Help")
        elif currentArg in ("-d", "--dev"):
            ser_device = currentVal
        elif currentArg in ("-c", "--cmd"):
            cmd = currentVal
            print("Command",cmd)


except getopt.error as err:
    print("Getopt Error:",str(err))
    sys.exit()

print("Serial device:",ser_device)
try:
    ser = serial.Serial(ser_device)
except:
    # Error open serial device, print message then exit
    print("Error opening device",ser_device)
    sys.exit()

ser.write(b">hlt\r")
time.sleep(.5)

waiting = ser.in_waiting
print("Waiting:",waiting)
while waiting > 0:
    data = ser.read(waiting)
    print("purged serial in:",len(data))
    time.sleep(.2)
    waiting = ser.in_waiting

print("Connecting to meter")


ser.write(b">lsr\r")
time.sleep(.2)
if ser.in_waiting == 0:
    print("Error: can't connect")
    sys.exit()
data = ser.readline()
print("Registers:",data)


if currentArg in ("-o", "--offset"):
    print("Setting DC Offset",currentVal)
    s = ">str,3,"+currentVal+"\r"
    #ser.write(b">str,3,"+currentVal+"\r")
    ser.write(s.encode("utf-8"))

if currentArg in ("-s", "--scale"):
    print("Setting DC Offset",currentVal)
    s = ">str,7,"+currentVal+"\r"
    ser.write(s.encode("utf-8"))


if currentArg in ("-p", "--profile"):
    if (currentVal in ["ha2040", "ha2350", "hp2040", "hp2350"]):
        print("Setting profile:",currentVal)
        if currentVal == 'hp2040':
            ser.write(b">str,4,0.00001626\r")
            ser.write(b">str,5,1.609244\r")
            ser.write(b">str,6,-93.121\r")
        elif currentVal == 'ha2040':
            ser.write(b">str,4,0.000012389634\r")
            ser.write(b">str,5,1.6107685\r")
            ser.write(b">str,6,-93.211\r")
        elif currentVal == 'hp2350':
            ser.write(b">str,4,0.00001797804\r")
            ser.write(b">str,5,1.603437\r")
            ser.write(b">str,6,-83.752\r")
    else:
        print("Error: unknown profile - valid profiles")
        print("  ha2040 - handy andy, PICO 1 / RP2040")
        print("  hp2040 - hewlett packard, PICO 1 / RP2040")
        print("  ha2350 - handy andy, PICO 2 / RP2350")
        print("  hp2350 - hewlett packard, PICO 2 / RP2350")
        ser.close()
        sys.exit()

if cmd in ["", "wrr"]:
    #opcodes = {
    #    ">avg":cmd_avg,     # run in average mode
    #    ">bye":cmd_bye,     # disconnect from client
    #    ">con":cmd_con,     # connect to client
    #    ">dmp":cmd_dmp,     # dump one ASDC buffer to serial port then halt
    #    ">flp":cmd_flp,     # flip display (only some OLEDs)
    #    ">hlt":cmd_hlt,     # halt
    #    ">lsr":cmd_lsr,     # list registers
    #    ">rdr":load_regs,   # load registers from config file
    #    ">run":cmd_run,     # run in sliding window mode
    #    ">stm":cmd_stm,     # stoe median value to registers
    #    ">wrr":save_regs,   # save current registers to config file
    #    ">str":cmd_str      # store value register
    #}

    if cmd != "":
        print("Running command:",cmd)
else:
    print("Error: Unknown command")
    ser.close()
    sys.exit()

ser.write(b">lsr\r")
time.sleep(.2)
if ser.in_waiting == 0:
    print("Error: can't connect")
    sys.exit()
data = ser.readline()
print("Registers:",data)

# disconnect from the deviation meter
print("Disconnect from meter and halt")
ser.write(b">bye\r")
ser.write(b">run\r")
ser.close()
