import utime
import _thread
from machine import Pin, UART
from dfplayer import Player
from neopixel import Neopixel

# DFR0299 Mini MP3 Player, playing status on GP28
pico_uart0 = UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1), bits=8, parity=None, stop=1)
pico_busy = Pin(28)
player = Player(uart=pico_uart0, busy_pin = pico_busy, volume=1.0)
player.awaitconfig()
player.awaitvolume()

# State variables
global distance
global playing

distance = 9999
playing = False
led_showing = False

# WS2813 LED Strip (HC-F5V-30L-30LED-W-WS2813)
numpix = 60
pixels = Neopixel(numpix, 0, 4, "GRB")
red = (255, 0, 0)
black = (0, 0, 0)
pixels.brightness(255)
pixels.fill(black)
pixels.show()

# HC-SR04P Ultrasonic sensor: a separate thread updates the distance
def ultra_thread():
    global distance
    
    trigger = Pin(3, Pin.OUT)
    echo = Pin(2, Pin.IN)
    
    while True:
        trigger.low()
        utime.sleep_us(2)
        trigger.high()
        utime.sleep_us(5)
        trigger.low()
        while echo.value() == 0:
            signaloff = utime.ticks_us()
           
        while echo.value() == 1:
           signalon = utime.ticks_us()
           
        timepassed = signalon - signaloff
        distance = (timepassed * 0.0343) / 2
        
        utime.sleep_ms(100)
        
_thread.start_new_thread(ultra_thread, ())
   
# PIN Interrupt handler for DFR0299's BUSY pin. Updates the playing status when changed to HIGH or LOW
def busy_handler(pin):
    global playing
    playing = pin.value() == 0
    print("Player status changed! {}".format(playing))

pico_busy.irq(trigger=machine.Pin.IRQ_RISING |machine.Pin.IRQ_FALLING , handler=busy_handler)


while True:
    # Play sound (01/001.mp3) when distance is less than a meter
    if distance < 100.0 and not playing:
       playing = True       
       player.play(1,1)
    
    # Turn LEDs on or off according to playing status
    if playing and not led_showing:
        led_showing = True
        pixels.fill(red)
        pixels.show()
        
    if not playing and led_showing:
        led_showing = False
        pixels.fill(black)
        pixels.show()
       
    utime.sleep_ms(100)
