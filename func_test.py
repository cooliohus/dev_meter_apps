def run(cmd_list):
    print('>run',cmd_list[1])

def hlt(cmd_list):
    print('>hlt')

def str(cmd_str):
    params = cmd_str.split(',')
    if int(params[1]) > 5:
        print('error')
    else:
        print('>'+cmd_str)

cmds = {'run':run,
        'hlt':hlt,
        'str':str
        }

cmd = 'str,4,5000'
cmds['str'](cmd)
