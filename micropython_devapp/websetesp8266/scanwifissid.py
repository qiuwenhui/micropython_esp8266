import network
sta_if = network.WLAN(network.STA_IF)
ssid = sta_if.scan()

for i in range(len(ssid)):
  a=str(ssid[i][0],'utf-8')
  print(a)
 

