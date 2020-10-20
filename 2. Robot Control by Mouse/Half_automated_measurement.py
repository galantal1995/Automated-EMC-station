
import matplotlib.pyplot as plt
import matplotlib.animation
import numpy as np
import serial
from PIL import Image
from matplotlib.widgets import Button
import time
import xlrd
import sys
import struct
from Spectrum_analyzer import Agilent_N9320B
from Spectrum_analyzer import Rigol_DSA800

# If you are using the Rigol analyzer, you should comment out the next line(Agilent_N9320B()) and delete the hashtag sign before the "my_instrument = Rigol_DSA800()" line.
my_instrument = Agilent_N9320B()
#my_instrument = Rigol_DSA800()

number_of_points_on_the_analyzer = my_instrument.number_of_data_per_measurement()

wb = xlrd.open_workbook('Input_Values.xlsx')
sheet = wb.sheet_by_index(0)

#--------------------------------------------------------------------------------------------------------------------------
# These are the input values. If you want to run the measurement without the GUI interface, just type your values and comment the sheet.cell_values out.
A = float(sheet.cell_value(1, 1))
B = float(sheet.cell_value(2, 1))
picture_of_the_PCB = str(sheet.cell_value(3, 1))
ID_code_of_spectrum_analyzer = str(sheet.cell_value(4, 1))
Serial_port = str(sheet.cell_value(5, 1))
start_freq_level = float(sheet.cell_value(6, 1))
stop_freq_level = float(sheet.cell_value(7, 1))
resolution_BW = float(sheet.cell_value(8, 1))
#---------------------------------------------------------------------------------------------------------------------------

#------------------------------------------------------------------------------------------------------------------------------------
# This part here is responsible for sending the necessary input values to Arduino through the Serial port.
# There are two values, which have to be given to Arduino in order to achieve the proper robot control.
# I am using the serial port communication between the two program.
# The variables to be sent: A, B.
# Through the serial port only integers that are between 0-255 can be sent, therefor I need to transform these values in order to make them sendable.
# These values then transformed back to their original shape in Arduino.

A1 = int(str(int(A))[:2])
try:
    A2 = int(str(int(A))[2])
except:
    sys.exc_info()[0]
    A2 = 10

B1 = int(str(int(B))[:2])
try:
    B2 = int(str(int(B))[2])
except:
    sys.exc_info()[0]
    B2 = 10

ser = serial.Serial(Serial_port, 11520)# Connecting to the Arduino through the serial monitor.
ser.close()
ser.open()
time.sleep(2)

ser.write(struct.pack('>BBBB',A1,A2,B1,B2)) # Sending A and B values to Arduino.
#---------------------------------------------------------------------------------------------------------------


if A > B:               # to control the size of the red dot (when clicking on the picture) in terms of the PCB size
    radius = A/60
else:
    radius = B/60

try:
    board = Image.open(picture_of_the_PCB)
except:
    sys.exc_info()[0]
    board = Image.open("tesat.jpg")

my_instrument.connect_device(ID_code_of_spectrum_analyzer)
my_instrument.start_frequency(start_freq_level) # To set the desired frequency range.
my_instrument.stop_frequency(stop_freq_level)
my_instrument.bandwidth(resolution_BW)  # To set the resolution bandwidth on the spectrum analyzer.
my_instrument.auto_sweeptime()          # To set the sweep time of the spectrum analyzer automatically.

time.sleep(0.5)

frequency = np.linspace(float(start_freq_level), float(stop_freq_level), int(number_of_points_on_the_analyzer))

amplitude = my_instrument.read_the_measurement()

fig, (ax1,ax2) = plt.subplots(1,2)      # Displayed figure. Left side is the real time image from the analyzer, right side is the picture of the board.
line1, = ax1.plot(frequency, amplitude)
ax1.set_ylim((np.amin(amplitude) - 5), 0)
ax2.imshow(board, alpha=1, extent=[0, A, B, 0])

ax1.set(xlabel="Frequency [Hz]", ylabel="Amplitude [dB]")
ax2.set(xlabel="A side of the PCB [mm]", ylabel="B side of the PCB [mm]")

def onclick(event):
    if event.xdata <= A:    # If you click on the frequency-amp map by accidentally, the robot will not move because the frequency value is bigger than A or smth...
        x = int(event.xdata)
        y = int(-event.ydata)
        ser.write(b'%d' %(x))
        ser.write(b'%d' %(y))
        ax2.clear()
        ax2.imshow(board, alpha=1, extent=[0, A, B, 0])
        ax2.add_artist(plt.Circle((event.xdata, event.ydata), radius, color='r'))
        fig.canvas.draw()


def update(amplitude):
    amplitude = my_instrument.read_the_measurement()
    line1.set_data(frequency,amplitude)

def go_to_origin(event):
    ser.write(b'0')

plt.connect('button_press_event', onclick)
ani = matplotlib.animation.FuncAnimation(fig, update, frames=60, repeat=True)

axbutton = plt.axes([0.85, 0.85, 0.1, 0.1])
button = Button(ax=axbutton, label='Starting position', hovercolor='tomato')
button.on_clicked(go_to_origin)

wm = plt.get_current_fig_manager()  # To display the figure in maximum size.
wm.window.state('zoomed')
plt.show()
my_instrument.close_device()
