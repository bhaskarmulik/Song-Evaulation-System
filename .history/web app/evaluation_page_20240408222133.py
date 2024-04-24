import streamlit as st

import torch
import torchaudio
import torchaudio.transforms
import torch.nn as nn
import librosa
from openunmix import predict
import numpy as np
import os
import soundfile as sf
import openunmix
from scipy.io.wavfile import read as read_wav
import pandas as pd

use_cuda = torch.cuda.is_available()
device = torch.device("cuda" if use_cuda else "cpu")

def trim_audio(audio):
    return librosa.effects.trim(audio)[0]

#Resampling the audio signals
def resample_audio(audio, sr, target_sr):
    return librosa.resample(y=audio, orig_sr=sr, target_sr=target_sr)

#Extracting a subset of the audio signals for faster computation
def subset_audio(audio, sr):
    return audio[0: round(3.5*sr)]

#Dividing the song into frames 
def frames(audio):
    frame_length = 2205
    frames = librosa.util.frame(audio, frame_length=frame_length, hop_length=512)
    return np.transpose(frames)

#Windowing a frame
def windowing(frame):
    #Using the hamm window
    return scipy.signal.get_window('hamming', frame.shape[0])

#L2 norm
def l2_norm(vector):
    return np.linalg.norm(vector, ord=2)

#L6 norm
def l6_norm(vector):
    return np.linalg.norm(vector, ord=6)

def pitch_detection(y, sr):
    pitches, magnitudes = librosa.core.piptrack(y=y, sr=sr)
    # get indexes of the maximum value in each time slice
    max_indexes = np.argmax(magnitudes, axis=0)
    # get the pitches of the max indexes per time slice
    pitches = pitches[max_indexes, range(magnitudes.shape[1])]
    return pitches

def med_sub_p(pitch_vector):
    median = np.median(pitch_vector)
    return pitch_vector - median

def pitch_features(frames, sr):
    l2n = []
    pmed=[]
    for frame in frames:
        pitch_vector = pitch_detection(frame, sr)
        # print(frame.shape, pitch_vector.shape)
        l2n.append(l2_norm(pitch_vector))
        medsubp = med_sub_p(pitch_vector)
        pmed.append(l2_norm(medsubp))
    l2n = pd.Series(l2n)
    pitch_der = l2n.diff()
    return np.array(pitch_der), np.array(pmed)

def mfcc_features(frames, sr):
    mfccs = []
    for frame in frames:
        # print(frame.reshape(-1,1).shape)
        mfcc = librosa.feature.mfcc(y=frame, sr=sr, n_mfcc=13, hop_length=220, n_fft=2048)
        mfccs.append(mfcc)
    return np.array(mfccs)


def mfcc_err(user_mfccs, og_mfccs):
    errors = []
    print(user_mfccs.shape)
    print(og_mfccs.shape)
    for i in range(user_mfccs.shape[0]):
        #Separate the errors for each of the 13 mfcc features
        errors.append(user_mfccs[i] - og_mfccs[i])
    error = np.array(errors)
    print(error.shape)

    for i in range(0,13,1):
        errors_mag = l2_norm(error[i])
    #mse
    error = np.sum(np.mean(errors_mag**2, axis=0))
    return error

def rop(user_frames, sr):
    l2n = []
    for frame in user_frames:
        pitch_vector = pitch_detection(frame, sr)
        # print(frame.shape, pitch_vector.shape)
        l2n.append(l2_norm(pitch_vector))
    l2n = np.array(l2n)
    return l2n.max() - l2n.min()

def short_term_log_energy(frames):
    energy = []
    for frame in frames:
        energy.append(np.log(np.sum(frame**2)))
    return np.array(energy)

def energy_err(user_frames, og_frames):
    user_energy = short_term_log_energy(user_frames)
    print(user_energy.shape)
    og_energy = short_term_log_energy(og_frames)
    return (user_energy - og_energy).sum()

def calculate_intensity(audio_data, sample_rate, window_func='hann'):

  audio_data = librosa.util.normalize(audio_data)  # Normalize audio
  stft = librosa.stft(audio_data, window=window_func)
  intensity_db = librosa.power_to_db(np.abs(stft) ** 2, ref=np.max(np.abs(stft)))
  return intensity_db

def find_peak_intensity(intensity_db, freq_range, sample_rate):
 
  nyquist = sample_rate / 2
  min_idx = int(freq_range[0] / nyquist * len(intensity_db))
  max_idx = int(freq_range[1] / nyquist * len(intensity_db))
  return np.max(intensity_db[min_idx:max_idx])

def singing_power_ratio(audio_data, sample_rate):

  intensity_db = calculate_intensity(audio_data, sample_rate)
  low_intensity_db = find_peak_intensity(intensity_db, (0, 2000), sample_rate)
  high_intensity_db = find_peak_intensity(intensity_db, (2000, 4000), sample_rate)
  
  
  if high_intensity_db == np.inf: 
    return float('inf')
  else:
    return 10 * np.log10(np.exp(low_intensity_db / 10) / np.exp(high_intensity_db / 10))  
  
def pitch_err():
    return 0

def final_merge(uploaded_file, original_file):
    user_song, sr1 = librosa.load(uploaded_file)
    original_song, sr2 = librosa.load(original_file)

    user_audio = predict.separate(openunmix.utils.preprocess(torch.as_tensor(user_song).float()),
                                          targets=['vocals'],
                                          residual=True,
                                          rate = sr1,
                                          device=device,
                                          model_str_or_path='umxhq')
    og_audio = predict.separate(openunmix.utils.preprocess(torch.as_tensor(original_song).float()),
                                          targets=['vocals'],
                                          residual=True,
                                          rate = sr2,
                                          device=device,
                                          model_str_or_path='umxhq')

    user_audio = user_audio[0][0]
    og_audio = og_audio[0][0]

    user_audio = trim_audio(user_audio)
    og_audio = trim_audio(og_audio)

    user_audio = resample_audio(user_audio, sr1, 22050)
    sr1 = 22050
    og_audio = resample_audio(og_audio, sr2, 22050)
    sr2 = 22050

    user_audio = subset_audio(user_audio, 22050)
    og_audio = subset_audio(og_audio, 22050)
    
    user_frames = frames(user_audio)
    og_frames = frames(og_audio)

    user_mfccs = mfcc_features(user_frames, sr1)
    og_mfccs = mfcc_features(og_frames, sr2)
    
    mfcc_errors = mfcc_err(user_mfccs, og_mfccs)    #MFCC error
    
    rop_user = rop(user_frames, sr1)
    rop_og = rop(og_frames, sr2)
    rop_err = rop_og - rop_user     #ROp error

    energy_errors = energy_err(user_frames, og_frames)  #Energy error

    ratio = singing_power_ratio(og_audio, sr1)

    pitch_err = pitch_err()

    w1 = 1
    w2 = 2
    w3 = 3
    w4 = 4
    w5 = 5

    return w1*mfcc_errors + w2*energy_errors + w3*rop_err +  w4*ratio + w5*pitch_err


def main():
    st.title("Evaluation Page")
    st.write("Upload an audio file for evaluation.")

    uploaded_file = st.file_uploader("Upload Audio File", type=["wav"])
    
    original_song = st.file_uploader("Upload original song", type=['wav'])

    if uploaded_file and original_song is not None:
        # Process the uploaded file
        evaluation_results = final_merge(uploaded_file, original_song)
        st.experimental_rerun()
        st.write("Evaluation Results: ", evaluation_results)

if __name__ == "__main__":
    main()
