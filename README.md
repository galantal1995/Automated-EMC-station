# Automated-EMC-station

This document introduces the automatic measuring station for radiated emission EMC pre-compliance measurements.
A magnetic field (H) probe is attached to an XY plotter robot that moves above the tested PCB to locate and identify potential sources of interference within the building blocks of electronic assemblies.

The purpose of this system is to identify locations that emit electromagnetic radiation with the automatic scanning of the probe over the surface of a PCB assembly or housing.
This automated system includes an Arduino based robot coordination, which cooperates with a python script. Python controls a Spectrum Analyzer, which conveys the data, measured through the near-field probe. This data is then processed and the measurement is eventually evaluated in the form of a colormap that shows the hotspots of magnetic radiation of the tested electronic circuit.

Two types of measurements were implemented:
1. Full Automated Measurement
  - GUI (Tkinter) collects the input values from the user (size of the tested PCB, picture, ambient radiation test etc.). 
  - Python commands Arduino to start moving the robot in steps.
  - Simultaniously, Python collects the measurements from the Spectrum Analyzer in a 3D array.
  - At the end, the robot moves back to the origin.
  - With using MatplotLib, a colormap is plotted that represents the results (RESULTS.png).
 
 2. Robot Control by Mouse
  - GUI (Tkinter) collects the input values from the user (size of the tested PCB, picture, ambient radiation test etc.).
  - The image of the tested board comes up.
  - Wherby clicking on a point of the board, the robot moves there and the real-time image from the Spectrum Analyzer is shown on the computer.
  - This spectrum can be saved with the location of the hotspot.
