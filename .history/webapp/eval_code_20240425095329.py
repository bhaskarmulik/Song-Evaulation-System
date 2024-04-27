
import openunmix.predict
import torch
import torchaudio
import torchaudio.transforms
import torch.nn as nn
import librosa
from openunmix import predict
import numpy as np
import os
import soundfile as sf
from openunmix.utils import load_separator
import scipy
from scipy.io.wavfile import read as read_wav
import pandas as pd
import statsmodels.api as sm


class Audio_eval:
    def __init__(self):
        self.use_cuda = torch.cuda.is_available()
        self.device = torch.device("cuda" if self.use_cuda else "cpu")
        self.separator = load_separator('D:/Yash Mulik Study/Mini-Project/github_codespace/Song-Evaulation-System/model', targets=['vocals'], device=self.device, residual=True)
        pass

    def trim_audio(self,audio):
        return librosa.effects.trim(audio)[0]

    #Resampling the audio signals
    def resample_audio(self,audio, sr, target_sr):
        return librosa.resample(y=audio, orig_sr=sr, target_sr=target_sr)

    #Extracting a subset of the audio signals for faster computation
    def subset_audio(self,audio, sr):
        return audio[0: round(3.5*sr)]

    #Dividing the song into frames 
    def frames(self,audio):
        frame_length = 2205
        frames = librosa.util.frame(audio, frame_length=frame_length, hop_length=512)
        return np.transpose(frames)

    #Windowing a frame
    def windowing(self, frame):
        #Using the hamm window
        return scipy.signal.get_window('hamming', frame.shape[0])

    #L2 norm
    def l2_norm(self,vector):
        return np.linalg.norm(vector, ord=2)

    #L6 norm
    def l6_norm(self,vector):
        return np.linalg.norm(vector, ord=6)

    def pitch_detection(self,y, sr):
        pitches, magnitudes = librosa.core.piptrack(y=y, sr=sr)
        # get indexes of the maximum value in each time slice
        max_indexes = np.argmax(magnitudes, axis=0)
        # get the pitches of the max indexes per time slice
        pitches = pitches[max_indexes, range(magnitudes.shape[1])]
        return pitches

    def med_sub_p(self,pitch_vector):
        median = np.median(pitch_vector)
        return pitch_vector - median

    def pitch_features(self,frames, sr):
        l2n = []
        pmed=[]
        for frame in frames:
            pitch_vector = self.pitch_detection(frame, sr)
            # print(frame.shape, pitch_vector.shape)
            l2n.append(self.l2_norm(pitch_vector))
            medsubp = self.med_sub_p(pitch_vector)
            pmed.append(self.l2_norm(medsubp))
        l2n = pd.Series(l2n)
        pitch_der = l2n.diff()
        return np.array(pitch_der).reshape(-1,1), np.array(pmed).reshape(-1,1)

    def mfcc_features(self,frames,sr):
        mfccs = []
        for frame in frames:
            # print(frame.reshape(-1,1).shape)
            mfcc = librosa.feature.mfcc(y=frame, sr=sr, n_mfcc=13, hop_length=220, n_fft=2048)
            mfccs.append(mfcc)
        return np.array(mfccs)


    def mfcc_err(self,user_mfccs, og_mfccs):
        errors = []
        print(user_mfccs.shape)
        print(og_mfccs.shape)
        for i in range(user_mfccs.shape[0]):
            #Separate the errors for each of the 13 mfcc features
            errors.append(user_mfccs[i] - og_mfccs[i])
        error = np.array(errors)
        print(error.shape)

        for i in range(0,13,1):
            errors_mag = self.l2_norm(error[i])
        #mse
        error = np.sum(np.mean(errors_mag**2))
        return error

    def rop(self,user_frames, sr):
        l2n = []
        for frame in user_frames:
            pitch_vector = self.pitch_detection(frame, sr)
            # print(frame.shape, pitch_vector.shape)
            l2n.append(self.l2_norm(pitch_vector))
        l2n = np.array(l2n)
        return l2n.max() - l2n.min()

    def short_term_log_energy(self,frames):
        energy = []
        for frame in frames:
            energy.append(np.log(np.sum(frame**2)))
        return np.array(energy)

    def energy_err(self,user_frames, og_frames):
        user_energy = self.short_term_log_energy(user_frames)
        # print(user_energy.shape)
        og_energy = self.short_term_log_energy(og_frames)
        return (user_energy - og_energy).sum()

    def calculate_intensity(self,audio_data, sample_rate, window_func='hann'):

        audio_data = librosa.util.normalize(audio_data)  # Normalize audio
        stft = librosa.stft(audio_data, window=window_func)
        intensity_db = librosa.power_to_db(np.abs(stft) ** 2, ref=np.max(np.abs(stft)))
        return intensity_db

    def find_peak_intensity(self,intensity_db, lower_freq, higher_freq, sample_rate):
    
        nyquist = sample_rate / 2
        min_idx = int(lower_freq / nyquist * len(intensity_db))
        max_idx = int(higher_freq / nyquist * len(intensity_db))
        return np.max(intensity_db[min_idx:max_idx])

    def singing_power_ratio(self,audio_data, sample_rate):

        intensity_db = self.calculate_intensity(audio_data, sample_rate)
        lower_freq1 = 0
        lower_freq2 = 2000
        higher_freq1 = 2000
        higher_freq2 = 4000
        # higher_freq = (2000,4000)
        low_intensity_db = self.find_peak_intensity(intensity_db, lower_freq1, higher_freq1, sample_rate)
        high_intensity_db = self.find_peak_intensity(intensity_db, lower_freq2, higher_freq2, sample_rate)
        
        
        if high_intensity_db == np.inf: 
            return float('inf')
        else:
            return 10 * np.log10(np.exp(low_intensity_db / 10) / np.exp(high_intensity_db / 10))  
        
    def pitch_err(self, user_pitch_f, og_pitch_f):
        vec1 = user_pitch_f[~np.isnan(user_pitch_f)]
        vec2 = og_pitch_f[~np.isnan(og_pitch_f)]
        return np.abs(vec1 - vec2).mean()

    def final_merge(self,uploaded_file, original_file):
        user_song, sr1 = torchaudio.load(uploaded_file)
        original_song, sr2 = torchaudio.load(original_file)

        user_audio = openunmix.utils.preprocess(user_song, rate = sr1, model_rate=sr1)
        og_audio = openunmix.utils.preprocess(original_song, rate = sr2, model_rate=sr2)

        user_audio = self.separator(user_audio)[0][0][0].reshape(-1,1).T
        og_audio = self.separator(og_audio)[0][0][0].reshape(-1,1).T

        user_audio = user_audio.detach().cpu().numpy()[0]
        og_audio = og_audio.detach().cpu().numpy()[0]

        # user_audio = user_audio[0][0]
        # og_audio = og_audio[0][0]

        user_audio = self.trim_audio(user_audio)
        og_audio = self.trim_audio(og_audio)


        user_audio = self.resample_audio(user_audio, sr1, 22050)
        sr1 = 22050

        og_audio = self.resample_audio(og_audio, sr2, 22050)
        sr2 = 22050

        user_audio = self.subset_audio(user_audio, 22050)
        og_audio = self.subset_audio(og_audio, 22050)
        
        user_frames = self.frames(user_audio)
        og_frames = self.frames(og_audio)

        user_mfccs = self.mfcc_features(user_frames, sr1)
        og_mfccs = self.mfcc_features(og_frames, sr2)
        
        self.mfcc_errors = self.mfcc_err(user_mfccs, og_mfccs)    #MFCC error
        
        rop_user = self.rop(user_frames, sr1)
        rop_og = self.rop(og_frames, sr2)
        self.rop_err = rop_og - rop_user     #ROp error

        self.energy_errors = self.energy_err(user_frames, og_frames)  #Energy error

        self.ratio = self.singing_power_ratio(og_audio, sr1)

        self.user_delta_p, self.user_pmed = self.pitch_features(user_frames, sr1)
        self.og_delta_p, self.og_pmed = self.pitch_features
        self.pitch_error1 = self.pitch_err(self.user_delta_p, self.og_delta_p)
        self.pitch_error2 = self.pitch_err(self.user_pmed, self.og_pmed)

        w1 = 1
        w2 = 2
        w3 = 3
        w4 = 4
        w5 = 5
        w6 = 1

        self.final_err =  w1*self.mfcc_errors + w2*self.energy_errors + w3*self.rop_err +  w4*self.ratio + w5*self.pitch_error1 + w6*self.pitch_error2
        return self.final_err