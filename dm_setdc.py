import sys, getopt, serial

ser_device = '/dev/ttyACM1'  # default device
cmd = ''                     # optional command
mode = 'run'                 # mode = run or avg

args = sys.argv[1:]
options = "hd:c:m:o:p:"
long_options = ["help", "dev=", "cmd=", "mode=", "offset", "profile"]

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

waiting = ser.in_waiting
while waiting > 0:
    data = ser.read(waiting)
    print("purged serial in:",len(data))
    waiting = ser.in_waiting

print("Connecting to meter")

ser.write(b">run\r")
ser.write(b">con\r")

try:
    while True:
        ser_in = str(ser.readline()).split(" ")
        dev = int(ser_in[2])
        adc = int(ser_in[3])
        med = int(ser_in[5])
        print(ser_in[7],med,dev)
except KeyboardInterrupt:
    print("\nCaught Keyboard Exception....")
    if cmd != '':
        print("Running command:",cmd)
    # disconnect from the deviation meter
    print("Disconnect from meter and halt")
    ser.write(b">bye\r")