# This script contains all the necessary functions to control the spectrum analyzer.
# The definitions under the classes are called from the main scripts so basically all the fuctions that controls the analyzer are executed from this code.
# There are two different classes, one that is responsible for the control of the Agilent N9320B analyzer and one that controls the Rigol DSA800 device.
# In the main sripts: EMC_inpit_values.py, EMC_measurement.py, z_EMC_evaluation_after_measurement_old.py 3. Half_automated_measurement_input_values.py, Half_automated_measurement.py the user has to select
# which class shall be used (which analyzer), depending on the connected spectrum analyzer. This must be done at the beginning of each codes.
# The rigol device often gave errors, therefor the default analyzer is the Agilent.
# If you would like to connect a different analyzer, you might have to test if these commands execute the same functions and how the data comes from the device.
# In the worst case, this different analyzer might require a different Visa library for the communication and that means the possibility of a different syntax.
# As a help for setting up the new analyzer, you should take a look at the Implementation_of_different_analyzer.py document.
# The difference between the agilent and rigol analyzer is the number of data per one meeasurement (Rigol = 601, Agilent = 461) and
# the process of reading the data out of the analyzer. All the other functions are basically the same.


import visa
import sys
import numpy as np

class Agilent_N9320B():
    def number_of_data_per_measurement(self): # One reading contains 461 different dB data from the Agilent N9320B analyzer. It might be different with other devices.)
        return 461                            # If you use a different device, go to the Implementation_of_different_analyzer.py first.

    def find_ID(self):  # Select button.
        rm = visa.ResourceManager()
        k = len(rm.list_resources())  # The resource manager saves all ID numbers of different devices which were connected to the computer.
        for k in range(k):  # With the try and except function I try to connect each IDs after each other. When the device belonging to the ID is not physically connected to the PC, it gives an error.
            try:  # With the try function I try to connect all the IDs and which does not give an error will be the ID of the acually conected device and it is saved.
                rm = visa.ResourceManager()
                self.query_of_IDs = rm.list_resources()[k]
                self.try_device = rm.open_resource(self.query_of_IDs) # The wrong IDs give error in this line because the computer is not able to connect them. (except...)
                self.ID_of_analyzer = self.query_of_IDs               # Only one device is connected and it's ID is realized here.
                self.info = self.try_device.query('*IDN?')
                break

            except:
                sys.exc_info()[0]
                pass

    def getID(self):
        return self.ID_of_analyzer

    def info_on_device(self):
        return self.info

    def connect_device(self, var):
        rm = visa.ResourceManager()  # Spectrum Analyzer
        self.connected_device = rm.open_resource(str(var))  # Connecting the spectrum analyzer The data in the bracket is the specific identification number of the used spectrum analyzer.

    def start_frequency(self, var):
        self.connected_device.write("SENS:FREQ:START " + str(var))  # To set the desired start frequency.

    def stop_frequency(self, var):
        self.connected_device.write("SENS:FREQ:STOP " + str(var))  # To set the desired stop frequency.

    def bandwidth(self, var):
        self.connected_device.write("SENS:BAND:RES " + str(var))  # To set the resolution bandwidth on the spectrum analyzer.

    def auto_sweeptime(self):
        self.connected_device.write(":SENSe:SWEep:TIME:AUTO ON")  # To set the sweep time of the spectrum analyzer automatically.

    def maxhold_on(self):
        self.connected_device.write(":TRACe1:MODE MAXHold")  # I set the analyzer to max hold to see the maximum peaks of the ambient radiation

    def maxhold_off(self):
        self.connected_device.write(":TRACe1:MODE WRITe")  # To turn off the max hold on the spectrum analyzer.

    def read_sweeptime(self):
        self.connected_device.write(":SENSe:SWEep:TIME?")  # it reads the sweep time of the spectrum analyzer. It always gives the time in seconds therefor I multiply this with 10^3 to get millisecond.
        return (float(self.connected_device.read()) * 10 ** 3) # converting the second value of the sweep time to millisecond.

    def read_the_measurement(self):
        self.connected_device.write(":TRACe:DATA? TRACe1")  # tracing the analyzer's displayed image.
        measured_data = np.array(self.connected_device.read().split(",")).astype(np.float32).astype(np.int8) # reading the values out of the spectrum analyzer and processing them in a numpy array.
        return measured_data                                                                                # The coming data is a list, which has to be converted to float and then integars.

    def close_device(self):
        self.connected_device.close()

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------

class Rigol_DSA800():
    def number_of_data_per_measurement(self): # One reading contains 601 different dB data from the Agilent N9320B analyzer. It might be different with other devices.
        return 601                            # If you use a different device, go to the Implementation_of_different_analyzer.py first.

    def find_ID(self):  # Select button.
        rm = visa.ResourceManager()
        k = len(rm.list_resources())  # The resource manager saves all ID numbers of different devices which were connected to the computer.
        for k in range(k):  # With the try and except function I try to connect each IDs after each other. When the device belonging to the ID is not connected to the PC, it gives an error.
            try:  # With the try function I try to connect all the IDs and which does not give an error will be the ID of the acually conected device and it is saved, typed in the typing field.
                rm = visa.ResourceManager()
                self.query_of_IDs = rm.list_resources()[k]
                self.try_device = rm.open_resource(self.query_of_IDs) # The wrong IDs give error in this line because the computer is not able to connect them. (except...)
                self.ID_of_analyzer = self.query_of_IDs                     # Only one device is connected and it's ID is realized here.
                self.info = self.try_device.query('*IDN?')
                break

            except:
                sys.exc_info()[0]
                pass

    def getID(self):
        return self.ID_of_analyzer

    def info_on_device(self):
        return self.info

    def connect_device(self, var):
        rm = visa.ResourceManager()  # Spectrum Analyzer
        self.connected_device = rm.open_resource(str(var))  # Connecting the spectrum analyzer The data in the bracket is the specific identification number of the used spectrum analyzer.

    def start_frequency(self, var):
        self.connected_device.write("SENS:FREQ:START " + str(var))  # To set the desired start frequency.

    def stop_frequency(self, var):
        self.connected_device.write("SENS:FREQ:STOP " + str(var))  # To set the desired stop frequency.

    def bandwidth(self, var):
        self.connected_device.write("SENS:BAND:RES " + str(var))  # To set the resolution bandwidth on the spectrum analyzer.

    def auto_sweeptime(self):
        self.connected_device.write(":SENSe:SWEep:TIME:AUTO ON")  # To set the sweep time of the spectrum analyzer automatically.

    def maxhold_on(self):
        self.connected_device.write(":TRACe1:MODE MAXHold")  # I set the analyzer to max hold for 60 seconds to see the maximum peaks of the ambient radiation

    def maxhold_off(self):
        self.connected_device.write(":TRACe1:MODE WRITe")  # To turn off the max hold on the spectrum analyzer.

    def read_sweeptime(self):
        self.connected_device.write(":SENSe:SWEep:TIME?")  # it reads the sweep time of the spectrum analyzer. It always gives the time in seconds therefor I multiply this with 10^3 to get millisecond.
        return (float(self.connected_device.read()) * 10 ** 3) # converting the second value of the sweep time to millisecond.

    def read_the_measurement(self):
        self.connected_device.write(":TRACe:DATA? TRACe1")  # tracing the analyzer's displayed image after the max hold.
        measured_data = np.array(self.connected_device.read()[11:].split(",")).astype(np.float32).astype(np.int8) # reading the values out of the spectrum analyzer and processing them in a numpy array.
        return measured_data                            # the first 11 value from the Rigol analyzer is always just an ID code, therefore it has to be deleted. # The coming data is a list, which has to be converted to float and then integars.

    def close_device(self):
        self.connected_device.close()