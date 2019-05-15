import network
sta_if = network.WLAN(network.STA_IF)
ssid = sta_if.scan()

for i in range(len(ssid)):
  print(str(ssid[i][0],'utf-8'))
  
html = """<!DOCTYPE html>
<html>
    <head> <title>ESP8266 Wifi SSID</title> </head>
    <body> <h1>ESP8266 wifi SSID</h1>
        <table border="1"> <tr><th>list</th><th>SSID</th></tr> %s </table>
    </body>
</html>
"""

import socket
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]

s = socket.socket()
s.bind(addr)
s.listen(1)

print('listening on', addr)

while True:
    cl, addr = s.accept()
    print('client connected from', addr)
    cl_file = cl.makefile('rwb', 0)
    while True:
        line = cl_file.readline()
        if not line or line == b'\r\n':
            break
    ssid = sta_if.scan()
    rows = ['<tr><td>%s</td><td>%s</td></tr>' % (str(p), str(ssid[p][0],'utf-8')) for p in range(0,len(ssid))]   
    response = html % '\n'.join(rows)
    cl.send(response)
    cl.close()
