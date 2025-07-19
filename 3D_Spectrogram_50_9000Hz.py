import sys
import numpy as np
import sounddevice as sd
from PyQt5 import QtWidgets
import pyqtgraph as pg
import pyqtgraph.opengl as gl
from scipy.signal import butter, lfilter


fs = 44100
chunk_size = 1024
nfft = 2048
buffer_chunks = 120
freqs = np.fft.rfftfreq(nfft, 1 / fs)
freq_mask = (freqs >= 50) & (freqs <= 9000)
freqs = freqs[freq_mask]
freq_bins = len(freqs)

def hz_to_mel(f):
    return 2595 * np.log10(1 + f / 700)

def butter_highpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='high', analog=False)
    return b, a

def highpass_filter(data, cutoff=30, fs=44100, order=4):
    b, a = butter_highpass(cutoff, fs, order=order)
    y = lfilter(b, a, data)
    return y


mel_freqs = hz_to_mel(freqs)
x_mel = (mel_freqs - mel_freqs.min()) / (mel_freqs.max() - mel_freqs.min())

y = np.arange(buffer_chunks)
y_norm = (y - y.min()) / (y.max() - y.min())
waterfall = np.zeros((buffer_chunks, freq_bins), dtype=np.float32)

app = QtWidgets.QApplication([])
view = gl.GLViewWidget()
view.resize(1600, 1000)
view.setWindowTitle('3D Audio Waterfall Spectrogram')
view.setCameraPosition(distance=5, elevation=30, azimuth=-90)  # Tighter zoom, overhead angle
view.setBackgroundColor('black')
view.opts['center'] = pg.Vector(0.5, 0.5, 0)  # Center on normalized data
view.show()

x_tick_freqs = [50, 100, 200, 300, 400, 500, 750, 1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000]

for f in x_tick_freqs:
    mel = hz_to_mel(f)
    x_tick = (mel - mel_freqs.min()) / (mel_freqs.max() - mel_freqs.min())
    label = QtWidgets.QLabel(f"{f//1000 if f>=1000 else f}{'k' if f>=1000 else ''}")
    label.setStyleSheet("background: rgba(0,0,0,220); color: red; font-size: 22px;")
    label.setParent(view)
    px = int(x_tick * (view.width() - 210) + 90)
    py = view.height() - 180
    label.move(px, py)
    label.show()
    

surface = gl.GLSurfacePlotItem(
    x=x_mel,
    y=y_norm,
    z=waterfall.T,
    shader='heightColor',
    computeNormals=False,
    smooth=False
)

surface.scale(3.7, 3.8, 1)
surface.translate(-1.35, -1.0, 0)
view.addItem(surface)

norm_max = 1.5e-2 

def audio_callback(indata, frames, time, status):
    global waterfall, norm_max
    if status:
        print(status)
    samples = indata[:, 0]
    samples = samples - np.mean(samples)
    samples = highpass_filter(samples, cutoff=55, fs=fs, order=2)
    samples = samples * np.hanning(len(samples))
    S = np.abs(np.fft.rfft(samples, n=nfft))[freq_mask]
    # min_bin = np.where(freqs >= 40)[0][0]
    # S[:min_bin] = 0
    peak = S.max()
    norm_max = max(0.99 * norm_max, peak)  # Decay slowly, rise instantly
    norm_max = max(norm_max, 1e-2)         # Prevent collapse to zero
    S /= (norm_max + 1e-6)
    S[S < 0.015] = 0

    if np.sqrt(np.mean(samples**2)) < 1.1e-3:
        S[:] = 0

    waterfall = np.roll(waterfall, 1, axis=0)
    waterfall[0, :] = S

stream = sd.InputStream(
    channels=1,
    samplerate=fs,
    blocksize=chunk_size,
    callback=audio_callback
)
stream.start()

def update():
    surface.setData(z=waterfall.T)

timer = pg.QtCore.QTimer()
timer.timeout.connect(update)
timer.start(33)  # ~30 FPS

if __name__ == '__main__':
    sys.exit(app.exec_())

