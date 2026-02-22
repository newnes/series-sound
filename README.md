# Series Sound

**Sonification of financial time series through spectral analysis and musical note mapping.**

This project transforms percentage changes in financial time series into audible frequencies using harmonic proportions and fundamental frequency detection. It generates both a CSV file with the mapped notes and a WAV audio file for auditory analysis.

> # Disclaimer:
> For research and experimental purposes only. Not intended for trading decisions.

---

# Installation

# WINDOWS:

1. Updating `pip`
   ```bash
   python.exe -m pip install --upgrade pip
   py -m pip --version
   ```
2. Installing `virtualenv`
   ```bash
   py -m pip install --user virtualenv
   ```
3. Creating a virtualenv:
   ```bash
   py -m venv env
   .\env\Scripts\activate
   ```
4. Install all dependencies:
   ```bash
   pip install -r requirements.txt
   ```

# What is Series Sound?

Series Sound is a Python-based tool that converts financial time series data into an audible representation. By analyzing percentage changes and extracting the fundamental frequency via FFT, it assigns harmonic frequencies to each data point and generates a sequence of musical notes. The result is a WAV audio file that allows traders and analysts to "hear" the market movements.

# How it works:

1. Spectral analysis: The script applies a Hann window and FFT to the time series to detect the fundamental frequency (or uses a default of 440 Hz).

2. Normalization: Percentage changes are smoothed and scaled to control the dynamic range.

3. Harmonic mapping: Frequencies are multiplied by just intonation proportions (unison, major third, fifth, etc.) to create harmonic richness.

4. MIDI conversion: Each frequency is converted to the nearest MIDI note for labeling.

5. Audio synthesis: Pure tones are generated for each data point and concatenated into a WAV file.

# Objective:

The objective is to provide an alternative sensory channel for analyzing financial time series, potentially revealing patterns or anomalies that are not easily spotted in visual charts. By sonifying the data, the user can listen to changes in volatility, trends, and price dynamics.

# Usage


