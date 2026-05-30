import pandas as pd
import matplotlib
matplotlib.use("Agg")   # avoid GUI from plt.show when running in terminal
import matplotlib.pylab as plt
import os
import random
import sys

# Debug pydub import so you see exact failure early and provide guidance
try:
    from pydub import AudioSegment
    print("Imported pydub:", AudioSegment)
except ModuleNotFoundError as e:
    print("pydub import failed:", repr(e))
    # common cause: Python build missing the audioop C extension
    try:
        import audioop  # type: ignore
        print("audioop is available")
    except Exception as e2:
        print("audioop import failed:", repr(e2))
        print()
        print("Fixes:")
        print("  - Recreate your venv using a Python build that includes audioop (Homebrew / python.org / conda).")
        print("  - On macOS (Homebrew) example:")
        print("      brew install python")
        print("      /opt/homebrew/bin/python3 -m venv .venv")
        print("      source .venv/bin/activate")
        print("      pip install --upgrade pip")
        print("      pip install pydub numpy simpleaudio")
        print("      brew install ffmpeg")
    sys.exit(1)
except Exception as e:
    print("pydub import failed (other):", repr(e))
    sys.exit(1)

filename = 'src/data_center_post-merged/Geospatial_Data_Centers_2026'

df = pd.read_csv(filename + '.csv')

coords = df[['lat', 'lng']].apply(pd.to_numeric, errors='coerce').dropna()

lat = coords['lat'].values
lon = coords['lng'].values

lat_shift = -lat.min() if lat.min() < 0 else 0.0
lon_shift = -lon.min() if lon.min() < 0 else 0.0
lat = lat + lat_shift
lon = lon + lon_shift

sizes = (lon - lon.min()) + 1.0

plt.scatter(lon, lat, s=sizes)
plt.xlabel('Longitude')
plt.ylabel('Latitude')
# plt.show()  # not usable with Agg backend
plt.savefig('map.png', dpi=150, bbox_inches='tight')
plt.close()

def map_value(value, min_value, max_value, min_result, max_result):
    denom = max_value - min_value
    if denom == 0:
        return min_result
    return min_result + (value - min_value)/denom*(max_result - min_result)

# set total length to 3 minutes
duration_sec = 180.0  # 180 seconds = 2 minutes
bpm = 60

# milliseconds per beat (keeps compatibility with earlier beat-based code)
beat_duration_ms = (60 / bpm) * 1000
duration_beats = duration_sec / (60 / bpm)  # number of beats in duration_sec

# map lon -> beat index
t_data = map_value(lon, lon.min(), lon.max(), 0, duration_beats)
y_data = map_value(lat, lat.min(), lat.max(), 0, 1)

print("Duration:", duration_sec, "seconds")

total_duration_ms = int(duration_sec * 1000) + 3000

# create silent canvas
audio_canvas = AudioSegment.silent(duration=total_duration_ms, frame_rate=44100)
print("Created a blank audio canvas. Total length (s):", total_duration_ms/1000)


# sounds are located at src/sounds relative to this file
sounds_dir = os.path.join(os.path.dirname(__file__), 'src', 'sounds')

if not os.path.isdir(sounds_dir):
    print("Sounds directory not found:", sounds_dir)
    print("Current working directory:", os.getcwd())
    raise SystemExit(1)

print("Using sounds directory:", sounds_dir)

# automatically discover supported audio files
supported_ext = ('.wav', '.mp3', '.flac', '.ogg', '.m4a', '.mp4', '.aac')
sample_files = [f for f in sorted(os.listdir(sounds_dir)) if f.lower().endswith(supported_ext)]
print("Found sound files:", sample_files)

if not sample_files:
    print("No sound files found in", sounds_dir, "- skipping audio export")
else:
    try:
        samples = [AudioSegment.from_file(os.path.join(sounds_dir, f)).set_frame_rate(44100) for f in sample_files]
    except Exception as e:
        print("Failed to load sample files:", repr(e))
        raise

    # simple pitch shift by changing frame_rate (cheap but easy)
    def pitch_shift_by_rate(seg: AudioSegment, semitones: float, target_sr=44100) -> AudioSegment:
        if semitones == 0:
            return seg.set_frame_rate(target_sr)
        new_rate = int(seg.frame_rate * (2 ** (semitones / 12.0)))
        shifted = seg._spawn(seg.raw_data, overrides={"frame_rate": new_rate})
        return shifted.set_frame_rate(target_sr)

    # map lat -> semitones (e.g. -12 .. +12), lon -> ms position across canvas
    semitone_values = map_value(lat, lat.min(), lat.max(), -12.0, 12.0)
    start_ms = map_value(lon, lon.min(), lon.max(), 0, total_duration_ms - 100)  # leave small tail

    output = audio_canvas
    for i in range(len(lat)):
        seg = random.choice(samples)
        semis = float(semitone_values[i]) if hasattr(semitone_values, '__len__') else float(semitone_values)
        shifted = pitch_shift_by_rate(seg, semis)

        # optional: map latitude-normalized amplitude (y_data 0..1) to dB gain (-12..0)
        gain_db = map_value(y_data[i], 0.0, 1.0, -12.0, 0.0) if hasattr(y_data, '__len__') else 0.0
        shifted = shifted + gain_db

        pos = int(start_ms[i]) if hasattr(start_ms, '__len__') else int(start_ms)
        output = output.overlay(shifted, position=max(0, pos))

    out_path = 'sonification_output.wav'
    output.export(out_path, format='wav')
    print("Exported sonification:", out_path)