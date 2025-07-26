import os
import uuid
import zipfile
from pathlib import Path

from flask import Flask, render_template, request, send_from_directory, redirect, url_for

from spleeter.separator import Separator
import librosa
import pretty_midi

UPLOAD_FOLDER = 'uploads'
RESULTS_FOLDER = 'results'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files.get('file')
    if not file:
        return redirect(url_for('index'))
    file_id = str(uuid.uuid4())
    audio_path = os.path.join(UPLOAD_FOLDER, f"{file_id}_{file.filename}")
    file.save(audio_path)
    result_dir = os.path.join(RESULTS_FOLDER, file_id)
    os.makedirs(result_dir, exist_ok=True)
    separate_and_convert(audio_path, result_dir)
    zip_path = os.path.join(RESULTS_FOLDER, f"{file_id}.zip")
    with zipfile.ZipFile(zip_path, 'w') as zf:
        for root, _, files in os.walk(result_dir):
            for fname in files:
                full = os.path.join(root, fname)
                zf.write(full, arcname=fname)
    return render_template('download.html', zip_file=f"{file_id}.zip")

@app.route('/download/<path:filename>')
def download(filename):
    return send_from_directory(RESULTS_FOLDER, filename, as_attachment=True)

def separate_and_convert(audio_path: str, output_dir: str):
    separator = Separator('spleeter:2stems')
    separator.separate_to_file(audio_path, output_dir)
    stems_subdir = os.path.join(output_dir, Path(audio_path).stem)
    for fname in os.listdir(stems_subdir):
        if fname.endswith('.wav'):
            wav_path = os.path.join(stems_subdir, fname)
            midi_path = os.path.join(stems_subdir, Path(fname).stem + '.mid')
            audio_to_midi(wav_path, midi_path)

def audio_to_midi(wav_path: str, midi_path: str, sr: int = 22050):
    y, sr = librosa.load(wav_path, sr=sr)
    f0, voiced_flag, _ = librosa.pyin(y, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7'))
    times = librosa.times_like(f0, sr=sr)
    midi = pretty_midi.PrettyMIDI()
    instrument = pretty_midi.Instrument(program=0)
    note_start = None
    note_pitch = None
    for t, freq, voiced in zip(times, f0, voiced_flag):
        if voiced:
            pitch = int(librosa.hz_to_midi(freq))
            if note_start is None:
                note_start = t
                note_pitch = pitch
            elif pitch != note_pitch:
                instrument.notes.append(pretty_midi.Note(velocity=100, pitch=note_pitch, start=note_start, end=t))
                note_start = t
                note_pitch = pitch
        else:
            if note_start is not None:
                instrument.notes.append(pretty_midi.Note(velocity=100, pitch=note_pitch, start=note_start, end=t))
                note_start = None
                note_pitch = None
    if note_start is not None:
        instrument.notes.append(pretty_midi.Note(velocity=100, pitch=note_pitch, start=note_start, end=times[-1]))
    midi.instruments.append(instrument)
    midi.write(midi_path)

if __name__ == '__main__':
    app.run(debug=True)
