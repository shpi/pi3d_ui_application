import subprocess

def scan():
    proc = subprocess.Popen(["iwlist", "wlan0", "scan"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    content = proc.stdout.read().decode('utf-8')
    cells = []
    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        if line.startswith('Cell'):
            cells.append(dict())
            cells[-1]['mac'] = line[-17:]
        elif line.startswith('ESSID'):
            cells[-1]['essid'] = line[7:-1]
        elif line.startswith('Encryption'):
            cells[-1]['enc'] = line[15:]
        elif line.startswith('IE: IEEE 802.11i/WPA2'):
            cells[-1]['enc'] = 'WPA2'
        elif line.startswith('IE: WPA Version 1'):
            cells[-1]['enc'] = 'WPA'
        elif line.startswith('Channel'):
            cells[-1]['ch'] = line[8:]
        elif line.startswith('Quality'):
            cells[-1]['quality'] = line[8:line.find(' ')]
            i = line.find('Signal level=')
            if i != -1:
                line = line[(i+13):]
                cells[-1]['dbm'] = line[:line.find(' ')]
        elif line.startswith('Signal level'):
            cells[-1]['quality'] = line[13:line.find(' ')]

    return cells


