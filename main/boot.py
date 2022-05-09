import time

time.sleep(1)
print("Booting...")
print("Connecting to WiFi...")
import network
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect("AIR X Pro", "55665566")

print("Boot done.")