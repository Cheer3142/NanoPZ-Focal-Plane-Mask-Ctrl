import sys
import glob
import serial

'''
QByteArray SCAN_SWITCHBOX : "BX",
QByteArray RESTORE_EEPROM : "BZ",
QByteArray ACTUATOR_DESCRIPTION : "ID",
QByteArray CONTORL_JOG : "JA",
QByteArray MOTOR_OFF : "MF",
QByteArray MOTOR_ON : "MO",
QByteArray SELECT_SWITCHBOX : "MX",
QByteArray ZERO_POSITION : "OR",
QByteArray GET_HARDWARE_STATUS : "PH",
QByteArray POSITION_RELATIVE : "PR",
QByteArray RESET_CONTORLLER : "RS",
QByteArray SET_CONTORLLER_ADDRESS : "SA",
QByteArray SET_NEGATIVE_TRAVEL_LIMIT : "SL",
QByteArray SAVE_SETTING : "SM",
QByteArray SET_POSITIVE_TRAVEL_LIMIT : "SR",
QByteArray STOP_MOTION : "ST",
QByteArray READ_ERROR_CODE : "TE",
QByteArray READ_CURRENT_POSITION : "TP",
QByteArray CONTORLLER_STATUS : "TS",
QByteArray READ_CONTORLLER_FIRMWARE : "VE",
'''

def serial_ports():
    # window/linux/darwin
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = [] 
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result

def ConnectPort(label):
    Actuator = serial.Serial(label,
                        baudrate=19200,
                        bytesize=8,
                        parity='N',
                        stopbits=1,
                        xonxoff=True,
                        timeout=1)
    print("Selected COM port:", label)
    return Actuator

if __name__ == '__main__':
    '''
    import serial.tools.list_ports
    ports = serial.tools.list_ports.comports()

    for port, desc, hwid in sorted(ports):
        print("{}: {} [{}]".format(port, desc, hwid))
    '''
    print(serial_ports(),1)
    #Actuator=ConnectPort("COM1")
    #Actuator.close()
    #print(Actuator)
















