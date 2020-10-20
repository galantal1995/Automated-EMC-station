# This code works on the same idea as the fully automated measurement. An excel sheet is created which contains the input values which are given by the user in a gui input window.
# This values are read by the Half_automated_measurement.py code which starts the process.
# The main idea of this code is to give a real time image from the analyzer with the access of moving the probe with mouse clicks.

import tkinter as tk
import tkinter.filedialog
import tkinter.messagebox
import xlsxwriter
import sys
from PIL import Image, ImageTk
import serial.tools.list_ports
from Spectrum_analyzer_control import Agilent_N9320B
from Spectrum_analyzer_control import Rigol_DSA800

# If you are using the Rigol analyzer, you should comment out the next line(Agilent_N9320B()) and delete the hashtag sign befor the "my_instrument = Rigol_DSA800()" line.
my_instrument = Agilent_N9320B()
#my_instrument = Rigol_DSA800()

workbook = xlsxwriter.Workbook('Input_Values.xlsx')
worksheet = workbook.add_worksheet()
bold = workbook.add_format({'bold': True})
worksheet.write('A1', 'Name', bold)
worksheet.write('B1', 'Value', bold)

worksheet.write(1, 0, "A side of the PCB: ")
worksheet.write(2, 0, "B side of the PCB: ")
worksheet.write(3, 0, "Picture of the PCB board: ")
worksheet.write(4, 0, "Identification number of the Spectrum Analyzer: ")
worksheet.write(5, 0, "Serial Port of the plotter: ")
worksheet.write(6, 0, "Desired start frequency of the analyzer: ")
worksheet.write(7, 0, "Desired stop frequency of the analyzer: ")
worksheet.write(8, 0, "Resolution bandwidth: ")

def connected_board(): # Automaticly defines the usb port to which the MeOrion plotter control board is connected.
    usb_devices = serial.tools.list_ports.comports(include_links=True)
    for i in range(len(usb_devices)):
        if usb_devices[i][1][:16] == "USB-SERIAL CH340":
            return(usb_devices[i][0])

def print_path():
    f = tk.filedialog.askopenfilename(parent=my_window, initialdir='C:/Tutorial',title='Choose file',filetypes=[('All Files', '.*'),('png images', '.png'),('gif images', '.gif'), ('jpg images', '.jpg')])
    e3.delete(0, tk.END)
    e3.insert(0, f)

def ID_of_analyzer():   # Select button.
    try:
        my_instrument.find_ID()
        e4.delete(0, tk.END)
        e4.insert(0, my_instrument.getID())
        tkinter.messagebox.showinfo("Spectrum Analyzer","The following measuring device is connected to the computer:\n\n" + (str(my_instrument.info_on_device())))
        my_instrument.connect_device(e4.get())
    except:
        sys.exc_info()[0]
        print("Please, check the connection of the spectrum analyzer because there is no detected device.")
        pass

def continue_button():
    worksheet.write(1, 1, e1.get())
    worksheet.write(2, 1, e2.get())
    worksheet.write(3, 1, e3.get())
    worksheet.write(4, 1, e4.get())
    worksheet.write(5, 1, connected_board())
    worksheet.write(6, 1, e5.get())
    worksheet.write(7, 1, e6.get())
    worksheet.write(8, 1, e7.get())
    workbook.close()
    response = tk.messagebox.askquestion("Simple Question", "Please open the Half-automated_measurement.ino arduino file, connect it to the appropriate Serial port and run the code.\n\n"
                                                            "Do you want to start the measurement?" )
    if 'yes' in response:
        my_window.destroy()
        import Half_automated_measurement

def exit_now():
    my_window.quit()

my_window = tk.Tk()
my_window.title("Half-automated measurement system")
my_window.state('zoomed')
tk.Label(my_window, text="1. A side of the PCB [mm]: ", font=2).grid(row=2, column=1)
tk.Label(my_window, text="2. B side of the PCB [mm]: ", font=2).grid(row=3, column=1)
tk.Label(my_window, text="3. Picture of the PCB board: ", font=2).grid(row=4, column=1)
tk.Label(my_window, text="4. Identification number of the Spectrum Analyzer: ", font=2).grid(row=5, column=1)
tk.Label(my_window, text="5. Desired start frequency of the analyzer [Hz]: ", font=2).grid(row=6, column=1)
tk.Label(my_window, text="6. Desired stop frequency of the analyzer [Hz]: ", font=2).grid(row=7, column=1)
tk.Label(my_window, text="7. Resolution bandwidth [Hz]: ", font=2).grid(row=8, column=1)
tk.Label(my_window, text="").grid(row=9, column=1)
tk.Label(my_window, text="").grid(row=10, column=1)

e1 = tk.Entry(my_window)
e2 = tk.Entry(my_window)
e3 = tk.Entry(my_window)
e4 = tk.Entry(my_window)
e5 = tk.Entry(my_window)
e6 = tk.Entry(my_window)
e7 = tk.Entry(my_window)

e1.grid(row=2, column=2)
e2.grid(row=3, column=2)
e3.grid(row=4, column=2)
e4.grid(row=5, column=2)
e5.grid(row=6, column=2)
e6.grid(row=7, column=2)
e7.grid(row=8, column=2)

tk.Button(my_window, text='Print path', font=2, command=print_path, width=8).grid(row=4, column=3)
tk.Button(my_window, text='Select', font=2, command=ID_of_analyzer, width=8).grid(row=5, column=3)
tk.Button(my_window, text='Quit', font=2, command=exit_now, width=8).grid(row=11, column=1)
tk.Button(my_window, text='Continue', font=2, command=continue_button, width=8).grid(row=11, column=3)

tesat = ImageTk.PhotoImage(Image.open("tesat.jpg"))
tk.Label(my_window, image=tesat).grid(row=1, column=5) # Tesat image on the right side.

my_window.grid_rowconfigure(0, weight=1)   # arranging the the content of the window in the center
my_window.grid_rowconfigure(12, weight=1)
my_window.grid_columnconfigure(0, weight=1)
my_window.grid_columnconfigure(6, weight=1)

my_window.mainloop()


