from machine import Pin, time_pulse_us
import time

# Define the GPIO pin for DHT11
DHT_PIN = 0											# pin0 is defined as DTH pin to communicate with sensor
data_pin = Pin(DHT_PIN, Pin.OUT)					# create an object, define DHT pin as output

# Define threshold for pulse duration
THRESHOLD = 100  									#  used as the value to determine if received pulse is 0 or 1

def read_dht11():
    # Step 1: Pull the pin low for 18 ms to initiate communication with DTH11
    data_pin.value(0)
    time.sleep_ms(18)

    # Step 2: Release the pin to allow it to be pulled high by the resistor
    data_pin.init(Pin.IN, Pin.PULL_UP)				# initaite the data pin to become an input to receive data from DTH11

    result = 0										# variable to store final result
    for i in range(41):  # Read 40 bits
        # Measure low and high pulse durations
        low_duration = time_pulse_us(data_pin, 0)	# measures the low time of pin and store 
        high_duration = time_pulse_us(data_pin, 1)	# measure the high duration of the pin and store

        # Calculate the total duration
        total_duration = low_duration + high_duration
        #print(f"Low duration: {low_duration} µs, High duration: {high_duration} µs, Total: {total_duration} µs")

        # Determine bit based on the total duration
        if i > 0:  # Skip the first measurement , is the response for start sent by host controller
            if total_duration < THRESHOLD:      # 0bit for DTH11 is 50+27 micros and 1bit is 50+70 micros, so if below 100 =0 above 100=1
                data_bit = 0					# if total duration of a pulse is less than 100us data_bit is 0
            else:
                data_bit = 1					# if total duration of a pulse is more than 100us data_bit is 1

            result = (result << 1) | data_bit  	# Shift and store the bit in result, all 40 bits are stored 1 by 1
    #print(f"Current Result: {result:040b}")  	# Print result in binary format

    # Extract temperature and humidity			# result is 40bit value
    humidity = (result >>32)					# humidity is the msb, bit 31:24 of result, right shift result 32 bits to extract MSB
    temperature = (result >> 16) & 0xFF			# temprature is bit 23:16 of result
    checksum = result >> 16 & 0xFF				# lsb of result. shift 16bits right then AND with 0xff to extract lower 8 bits

    # Reset pin to output mode
    print(f"Temperature: {temperature}°C, Humidity: {humidity}%") # print temprature and humidity in the shell. if oled , need additional code
    data_pin.init(Pin.OUT)						# change data pin to output again for transmitting 18ms start signal in next call
    data_pin.value(1)  							# Set the pin back to output mode

# Main loop
while True:
    read_dht11()								# read data from DTH11
    time.sleep(2)  								# Wait before the next read