import pyaudio
import wave
import os
import time

# Configuration
chunk = 1024  # Record in chunks of 1024 samples
sample_format = pyaudio.paInt16  # 16 bits per sample
channels = 2  # stereo
fs = 44100  # Record at 44100 samples per second
seconds_per_chunk = 10

# Initialize PyAudio
p = pyaudio.PyAudio()

stream = p.open(format=sample_format,
                channels=channels,
                rate=fs,
                frames_per_buffer=chunk,
                input=True)

# Record and save audio in 10-second chunks
try:
    os.mkdir('recordings')
except FileExistsError:
    pass

print("Recording started. Press Ctrl+C to stop.")

try:
    while True:
        filename = time.strftime("recordings/%Y-%m-%d_%H-%M-%S.wav")
        frames = []

        # Record data chunk
        for i in range(0, int(fs / chunk * seconds_per_chunk)):
            data = stream.read(chunk)
            frames.append(data)

        # Save the chunk to a WAV file
        wf = wave.open(filename, 'wb')
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(sample_format))
        wf.setframerate(fs)
        wf.writeframes(b''.join(frames))
        wf.close()

        print(f'Chunk saved as {filename}')

except KeyboardInterrupt:
    print("Recording stopped.")

finally:
    # Stop and close the stream 
    stream.stop_stream()
    stream.close()
    # Terminate the PortAudio interface
    p.terminate()
