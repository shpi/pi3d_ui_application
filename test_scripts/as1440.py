#read  energymeter elster as1440  with ir-usb 

import sys, getopt, serial, time,regex as re, requests
#from requests.auth import HTTPBasicAuth
#from requests.auth import HTTPDigestAuth



def send( port, bytes):
    bytes = bytes.encode('ascii')
    port.write(bytes)
    time.sleep(0.2)

def read1( port ):
    x = port.read().decode('ascii')
    return x



ACK = '\x06'
STX = '\x02'
ETX = '\x03'


EnergyMeter = serial.Serial(port='/dev/ttyIR', baudrate=300, bytesize=7, \
                                    parity='E', stopbits=1, timeout=1.5);



send(EnergyMeter, '/2!\r\n')
EnergyMeter.readline()
time.sleep(0.1)
send(EnergyMeter, ACK + '050\r\n')
EnergyMeter.baudrate = 9600


#<SOH>R5<STX>P.01(;)<ETX><BCC> (01 52 35 02 50 2E 30 31 28 3B 29 03 23)
#<SOH>R5<STX>1.7.0()<ETX><BCC> (01 52 35 02 31 2e 37 2e 30 28 29 03 51)
#<SOH>R5<STX>0.9.1()<ETX><BCC>
#send(EnergyMeter,'\x01' + '\x52' + '\x35' + '\x02' + '\x50' + '\x2e' + '\x37' + '\x2e' + '\x30' + '\x28' + '\x29' + '\x03' + '\x23' + '\r\n')


data = ''
if (read1(EnergyMeter) == STX):

            x = read1(EnergyMeter)
            BCC = 0
            while (x != '!'):
                BCC = BCC ^ ord(x)
                data += x
                x = read1(EnergyMeter)
            while (x != ETX):
                BCC = BCC ^ ord(x)
                x = read1(EnergyMeter)
            BCC = BCC ^ ord(x)
            x = read1(EnergyMeter)
            ### x is now the Block Check Character
            
            if (BCC != ord(x)): # received correctly?
                data = data + 'ERROR'
                EnergyMeter.close()

print data


#for openhab implementation
#Number general_consumption "Power [%.0f W]" <energy>
#Number general_feedin "Power [%.0f W]" <energy>
#Number general_readout "Power [%.0f kWh]" <energy>
#Number general_readin "Power [%.0f kWh]" <energy>
#Number general_L1_V "Power [%.0f kWh]" <energy>
#Number general_L2_V "Power [%.0f kWh]" <energy>
#Number general_L3_V "Power [%.0f kWh]" <energy>
#Number general_L1_A "Power [%.0f kWh]" <energy>
#Number general_L2_A "Power [%.0f kWh]" <energy>
#Number general_L3_A "Power [%.0f kWh]" <energy>
#headers = {'content-type': 'text/plain','accept' : 'application/json' }
#requests.put('http://localhost:8080/rest/items/general_consumption/state', data = re.search('1\.7\.0\(([0-9\.]*)\*kW\)', data).group(1).replace('.',''), headers = headers)
#requests.put('http://localhost:8080/rest/items/general_feedin/state', data = re.search('2\.7\.0\(([0-9\.]*)\*kW\)', data).group(1).replace('.',''), headers = headers)
#requests.put('http://localhost:8080/rest/items/general_readout/state', data = re.search('1\.8\.0\(([0-9\.]*)\*kWh\)', data).group(1), headers = headers)
#requests.put('http://localhost:8080/rest/items/general_readin/state', data = re.search('2\.8\.0\(([0-9\.]*)\*kWh\)', data).group(1), headers = headers)
#requests.put('http://localhost:8080/rest/items/general_L1_V/state', data = re.search('32\.7\.0\(([0-9\.]*)\*V', data).group(1), headers = headers)
#requests.put('http://localhost:8080/rest/items/general_L2_V/state', data = re.search('52\.7\.0\(([0-9\.]*)\*V', data).group(1), headers = headers)
#requests.put('http://localhost:8080/rest/items/general_L3_V/state', data = re.search('72\.7\.0\(([0-9\.]*)\*V', data).group(1), headers = headers)
#requests.put('http://localhost:8080/rest/items/general_L1_A/state', data = re.search('31\.7\.0\(([0-9\.]*)\*A', data).group(1), headers = headers)
#requests.put('http://localhost:8080/rest/items/general_L2_A/state', data = re.search('51\.7\.0\(([0-9\.]*)\*A', data).group(1), headers = headers)
#requests.put('http://localhost:8080/rest/items/general_L3_A/state', data = re.search('71\.7\.0\(([0-9\.]*)\*A', data).group(1), headers = headers)

