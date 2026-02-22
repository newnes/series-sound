> # Disclaimer:
> For research and experimental purposes only. Not intended for trading decisions.

## Registered Idea Work (2016)

[View the copyright registration of "LA FRECUENCIA ARMÓNICA EN EL ANÁLISIS DE VALORES DE LOS MERCADOS BURSÁTILES" (PDF)](https://github.com/newnes/Time-Series-Sound/raw/main/Cert_Author.pdf)

# Series Sound

**Sonification of financial time series through spectral analysis and musical note mapping.**

This project transforms percentage changes in financial time series into audible frequencies using harmonic proportions and fundamental frequency detection. It generates both a CSV file with the mapped notes and a WAV audio file for auditory analysis.

## What is Series Sound?

Series Sound is a Python-based tool that converts financial time series data into an audible representation. By analyzing percentage changes and extracting the fundamental frequency via FFT, it assigns harmonic frequencies to each data point and generates a sequence of musical notes. The result is a WAV audio file that allows traders and analysts to "hear" the market movements.

---

## How it works:

1. Spectral analysis: The script applies a Hann window and FFT to the time series to detect the fundamental frequency (or uses a default of 440 Hz).

2. Normalization: Percentage changes are smoothed and scaled to control the dynamic range.

3. Harmonic mapping: Frequencies are multiplied by just intonation proportions (unison, major third, fifth, etc.) to create harmonic richness.

4. MIDI conversion: Each frequency is converted to the nearest MIDI note for labeling.

5. Audio synthesis: Pure tones are generated for each data point and concatenated into a WAV file.

---
## Objective:

The objective is to provide an alternative sensory channel for analyzing financial time series, potentially revealing patterns or anomalies that are not easily spotted in visual charts. By sonifying the data, the user can listen to changes in volatility, trends, and price dynamics.

---

## Listen to the result:

You can hear the sonification of financial time series in action.  
This audio example was generated with this project:

[![NOVA - The Symphony of the Bullish and Bearish](https://img.youtube.com/vi/k4zKi3tx3fU/0.jpg)](https://www.youtube.com/watch?v=k4zKi3tx3fU)

Click the image or [watch on YouTube](https://www.youtube.com/watch?v=k4zKi3tx3fU)

---

## Curious Note:

As an interesting parallel, modern Large Language Models (LLMs) can also process and generate information through audio representations.  

When LLM-based systems interact with speech models, communication may involve acoustic signal processing, waveform encoding, spectral decomposition, and frequency-domain transformations — conceptually similar to how this project converts financial time series into sound.

While LLMs do not "think in audio" by default, multimodal AI systems frequently rely on spectral analysis and waveform modeling when handling speech-to-text and text-to-speech tasks.

This project explores a similar idea from a quantitative finance perspective:  
transforming abstract numerical structures into audible signals to reveal hidden patterns through an alternative sensory channel.

---

## Installation

### WINDOWS:

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
---


---
## Usage:

**Show help:**
  
   ```bash
   python Spectral_Analysis.py --help
   ```

**Run the script:**

   ```bash
   python Spectral_Analysis.py
   ```
---

## Expected interactive output:

Available dates:
  1. 2022-05-12
  2. 2022-05-13
  3. 2022-05-14

Enter the number of the date you want to analyze (or 'q' to quit): 1

Processing date: 2022-05-12
----------
Generating notes: 100%|██████████| 1440/1440 [00:02<00:00, 500.00it/s]
----------
Generating audio: 100%|██████████| 1440/1440 [00:05<00:00, 250.00it/s]
----------
## Output files: 
****************************************************************
1. Audio generated: MUSIC/audio_2022-05-12.wav
2. CSV saved: MUSIC/output_2022-05-12.csv

****************************************************************
---
## Dependencies
**All required packages are listed in requirements.txt:**
```bash
numpy
pandas
librosa
soundfile
scipy
tqdm
```
---
## License
**This project is licensed under the MIT License. See the LICENSE file for details.**

**MIT License**

**Copyright (c) 2025 Nestor Mendez / FiboQuant_MX**

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Author
**Nestor Mendez / FiboQuant_MX / GitHub: @newnes**

## Contributing
Contributions, issues, and feature requests are welcome. Feel free to open an issue or submit a pull request.

## Show your support
If you find this project interesting, please give it a star on GitHub.

