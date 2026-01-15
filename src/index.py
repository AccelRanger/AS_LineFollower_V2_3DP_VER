# ================== PIN CONFIG ================== #

# QTRX
QTRX_PINS = [
    2, 3, 4, 5, 6, 7, 8,
    9, 10, 11, 12, 13, 14
]

# Motor Driver
MOTOR_LEFT_A  = 16
MOTOR_LEFT_B  = 17
MOTOR_RIGHT_A = 18
MOTOR_RIGHT_B = 19

# HCSR04
ULTRASONIC_TRIGGER = 20
ULTRASONIC_ECHO    = 21
STOP_DISTANCE_CM = 40

from machine import Pin, time_pulse_us
import time

# Line sensor setup

sensors = [Pin(pin, Pin.IN) for pin in QTRX_PINS]

def read_qtrx():
    return [sensor.value() for sensor in sensors]

# Motor setup

ml_a = Pin(MOTOR_LEFT_A, Pin.OUT)
ml_b = Pin(MOTOR_LEFT_B, Pin.OUT)
mr_a = Pin(MOTOR_RIGHT_A, Pin.OUT)
mr_b = Pin(MOTOR_RIGHT_B, Pin.OUT)

def stop_motors():
    ml_a.value(0)
    ml_b.value(0)
    mr_a.value(0)
    mr_b.value(0)

def forward():
    ml_a.value(1)
    ml_b.value(0)
    mr_a.value(1)
    mr_b.value(0)

def turn_left():
    ml_a.value(0)
    ml_b.value(1)
    mr_a.value(1)
    mr_b.value(0)

def turn_right():
    ml_a.value(1)
    ml_b.value(0)
    mr_a.value(0)
    mr_b.value(1)

# Distance

trig = Pin(ULTRASONIC_TRIGGER, Pin.OUT)
echo = Pin(ULTRASONIC_ECHO, Pin.IN)

def get_distance_cm():
    trig.value(0)
    time.sleep_us(2)
    trig.value(1)
    time.sleep_us(10)
    trig.value(0)

    try:
        duration = time_pulse_us(echo, 1, 30000)
        return (duration * 0.0343) / 2
    except OSError:
        return 999  # No echo

# Main Logic

CENTER_INDEX = len(QTRX_PINS) // 2

def follow_line(sensor_values):
    left_sum  = sum(sensor_values[:CENTER_INDEX])
    right_sum = sum(sensor_values[CENTER_INDEX + 1:])

    if sensor_values[CENTER_INDEX]:
        forward()
    elif left_sum > right_sum:
        turn_left()
    elif right_sum > left_sum:
        turn_right()
    else:
        stop_motors()

# Main loop

print("AccelSystems >> LNF > STATE RUN <")

while True:
    distance = get_distance_cm()

    if distance < STOP_DISTANCE_CM:
        stop_motors()
        print("STOP – object at", distance, "cm")
        time.sleep(0.05)
        continue

    qtrx_values = read_qtrx()
    follow_line(qtrx_values)

#    print("QTRX:", qtrx_values, "Dist:", distance)
    time.sleep(0.01)
