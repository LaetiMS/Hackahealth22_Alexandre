
#!/usr/bin/python
import RPi.GPIO as GPIO
import time
from datetime import datetime
import os

# GPIO setup
GPIO.setmode (GPIO.BCM)
GPIO.setwarnings(False)

# setup gpio for echo & trig 
TRIG_LEFT       = 22
TRIG_RIGHT      = 23
ECHO_LEFT       = 27
ECHO_RIGHT      = 17
LEFT            = 0
RIGHT           = 1

WAIT_TIME       = 0.5
THRESHOLD       = 80 
MIN_PERCENTAGE  = 0.2

trigpin = [TRIG_LEFT, TRIG_RIGHT] 
echopin = [ECHO_LEFT, ECHO_RIGHT]

for j in range(2):
    GPIO.setup(trigpin[j], GPIO.OUT)
    GPIO.setup(echopin[j], GPIO.IN)
    print (j, echopin[j], trigpin[j])
    print (" ")



     

# Get reading from HC-SR04
def ping(echo, trig):
    
    GPIO.output(trig, False)
    # Allow module to settle
    time.sleep(0.2)
    # Send 10us pulse to trigger
    GPIO.output(trig, True)
    time.sleep(0.00005)
    GPIO.output(trig, False)
    pulse_start = time.time()
    
    pulse_waiting = pulse_start
    # save StartTime
    
    while GPIO.input(echo) == 0 and (pulse_waiting-pulse_start) < WAIT_TIME :
        pulse_waiting = time.time()
    if (pulse_waiting-pulse_start) >= WAIT_TIME :
        print("Limit time elapsed!")
    pulse_end = pulse_waiting
    # save time of arrival
    while GPIO.input(echo) == 1:
        pulse_end = time.time()

    # time difference between start and arrival
    pulse_duration = pulse_end - pulse_start
    # mutiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = pulse_duration * 17150

    distance = round(distance, 2)

    return distance

print (" press Ctrl+c to stop program ")

    # main loop
def print_results ():
    
    results_left = str(datetime.now()) + ","
    distance_left = ping(echopin[LEFT], trigpin[LEFT])
    print ("left sensor", distance_left)
    results_left = results_left + str(distance_left) + "," + "\n"
    
    results_right = str(datetime.now()) + ","
    distance_right = ping(echopin[RIGHT], trigpin[RIGHT])
    print ("right sensor", distance_right)
    results_right = results_right + str(distance_right) + "," + "\n"

    print ("wait")
    time.sleep (0.8)   
 
 
def collision_alarm ():
    distance_right = ping(echopin[RIGHT], trigpin[RIGHT])
    distance_left = ping(echopin[LEFT], trigpin[LEFT])
    min_dist = THRESHOLD  * MIN_PERCENTAGE
    if ( distance_right >= min_dist and  distance_right <= THRESHOLD) or (distance_left  >= min_dist and distance_left  <= THRESHOLD ) :
        print("obstacle")
        return True
    return False
    

while True :
    # get distances and assemble data line for writing
    collision_alarm()
    print_results()


