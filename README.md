<img width="548" height="526" alt="image" src="https://github.com/user-attachments/assets/338e2c96-1546-4a4c-bfd5-1ff7fe768605" />

# PCM Audio Power Meter
**A numerical power meter tool for PCM audio.**

---

## Overview
The **PCM Audio Power Meter** is a lightweight, high-performance Python tool designed for radio amateurs and RF enthusiasts. It transforms your computer's audio input—from an SDR, virtual audio cable, or receiver—into a high-resolution digital bolometer. 

Designed for tasks like **QO-100 dish alignment**, using the CW, mid, or multimedia beacons.

## Key Features
* **Numerical Focus:** Large, high-visibility **Blue** primary display for precision delta tracking.
* **Live Statistics:** Dedicated tracking for **Max Power (Green)** and **Min Power (Yellow)**.
* **Vectorized Performance:** Uses **NumPy** for optimized "Sum of Squares" mathematical operations.
* **Dual Mode UI:** Includes **Dark** and **Light** themes for high visibility.
* **Ergonomic Controls:** Mobile-optimized layout with "Reset Stats" and "Toggle Theme" buttons placed for easy thumb access.
* **Network-Ready:** Runs a local web server (Port 8080) allowing for remote monitoring on a smartphone or tablet at the antenna.

## Technical Theory

### The Digital Bolometer Principle
Unlike standard VU meters or "loudness" indicators that use arbitrary weighting or RC-style smoothing constants, this meter operates as a **Digital Bolometer**. It treats the incoming PCM stream as a series of voltage samples and calculates the true energy content of the waveform by computing the **Mean Square Power**.

### Mathematical Foundation
For a discrete buffer of $N$ samples, the power is calculated as:

$$P_{dB} = 10 \cdot \log_{10} \left( \frac{1}{N} \sum_{i=1}^{N} s_i^2 \right)$$

Where:
* $s_i$ is the individual 16-bit signed PCM sample.
* $s_i^2$ represents the instantaneous power of that sample.
* $\frac{1}{N} \sum s_i^2$ is the average power (Mean Square) over the window $N$.

## Implementation Strategy
* **Chunk Integration ($N=8192$):** At a sample rate of 48 kHz, each numerical update represents an integration of ~170ms of audio. This window is specifically chosen to be long enough to provide numerical stability (averaging out atmospheric flicker) but short enough to provide "instant" feedback during physical dish movement.
* **Vectorized Processing:** The script uses **NumPy's `np.mean(arr**2)`** logic.
* **Logarithmic Scaling:** The results are mapped to a decibel (dB) scale. This allows the user to see tiny linear changes (0.1 dB) in signal-to-noise ratio that would be invisible on a standard linear scale.
* **Numerical Clamping:** To prevent mathematical domain errors (log of zero) during periods of absolute silence, the algorithm applies a floor clamp, ensuring the display remains at a stable 0.0 dB.

## Dependencies
This project requires **Python 3.7+** and the following libraries:

* **NumPy:** For high-speed vectorized mathematical operations.
* **PyAudio:** For accessing the system's real-time audio stream.

## Installation
Install the necessary dependencies using pip:

```
pip install numpy pyaudio
```

## Usage
#### 1. Identifying the Correct Audio Device
PyAudio interacts with your system's hardware abstraction layer. Because device indices can change when you plug or unplug USB devices, it is best to verify the index every time you change your hardware setup.

Run the discovery command:

```
python pcm_power_meter.py
```

What to look for:

SDR Users: Look for "CABLE Output" or "Virtual Audio Cable."

Hardware Users: Look for "USB Audio Device" or "Built-in Microphone."

>Note: Ensure the device you select is set to a 48000 Hz sample rate in your OS Sound Settings to match the script's configuration for the best accuracy.

#### 2. Accessing the Web Interface
The script hosts a local "Micro-Server." Once started, the meter can be viewed on any device connected to the same local network (Wi-Fi or LAN).

Local Access (Same Computer): Simply open your browser and type: http://localhost:8080

Remote Access (Smartphone/Tablet at the Antenna): To monitor the signal while physically adjusting your dish, you need your computer's local IP address:

Find your IP: Run ipconfig (Windows) or ip addr (Linux/Mac).

On your phone's browser, enter the IP followed by the port (e.g., http://192.168.1.50:8080).

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
