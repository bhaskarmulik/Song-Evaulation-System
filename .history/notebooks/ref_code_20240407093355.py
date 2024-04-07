############Code 1#######################
import numpy as np

# Assuming 'data' is your speech signal array and 'fs' is the sampling frequency
frame_size = 0.32  # 320 ms
overlap = 0.5
frame_samples = int(frame_size * fs)
step_size = int(frame_samples * (1 - overlap))

# Function to compute the Lp norm
def lp_norm(data, p):
    return (np.sum(np.abs(data)**p))**(1/p)

# Compute the L6 norm over split-second intervals
l6_norms = []
for i in range(0, len(data) - frame_samples + 1, step_size):
    frame = data[i:i+frame_samples]
    l6_norm = lp_norm(frame, 6)
    l6_norms.append(l6_norm)

# Compute the L2 norm over all split-second L6 norms
l2_norm_over_l6 = lp_norm(np.array(l6_norms), 2)

print(f'L6 norms over split-second intervals: {l6_norms}')
print(f'L2 norm over all split-second L6 norms: {l2_norm_over_l6}')


##############Code 2###########################

#Trimming the audios to the same length
def trim_audio(audio1, audio2):
    min_length = min(len(audio1), len(audio2))
    return audio1[:min_length], audio2[:min_length]

#Filling out the NaN values with the average of the previous and the next values
def fill_nan_with_avg(arr):
    mask = np.where(np.isnan(arr))[0]
    for i in mask:
        if i!=0 and i!=len(arr)-1:
            arr[i] = np.mean(arr[i-1], arr[i+1])
        elif i==0:
            arr[i] = arr[i+1]+0.0000001
        else:
            arr[i] = arr[i-1]+0.0000001
    return mask

# print(fill_nan_with_avg(user_audio))

#Extracting the fundamental frqeuency using librosa
def extract_f0(audio):
    f0, voiced_flag, voiced_probs = librosa.pyin(audio, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7'))
    f0 = fill_nan_with_avg(f0)
    return f0, voiced_flag, voiced_probs

#Detecting pitches
def detect_pitch(y, sr):
    pitches, magnitudes = librosa.core.piptrack(y=y, sr=sr, fmin=75, fmax=1600)
    # get indexes of the maximum value in each time slice
    max_indexes = np.argmax(magnitudes, axis=0)
    # get the pitches of the max indexes per time slice
    pitches = pitches[max_indexes, range(magnitudes.shape[1])]
    return pitches

#Using the librosa library to extract MFCCs
def extract_mfccs(audio, sr):
    mfccs = librosa.feature.mfcc(audio, sr=sr, n_mfcc=13)
    return mfccs

#DWT algorithm
def dtw(audio1, audio2):
    result = librosa.sequence.dtw(audio1.T, audio2.T, backtrack=True)
    return result[1]

def plot_signal(audio):
    plt.plot(audio)
    plt.show()

#################Code 3######################
# #We divide the audio file into segments of 32ms each
# #We find how we first divide the song into frames

audio_file = og_audio.copy()
sample_rate = sr2

windowsize = 0.32
no_of_samples_per_frame = windowsize*sample_rate
overlap = 0.5
start = audio_file[0]
end = audio_file[len(audio_file)-1]
step = no_of_samples_per_frame * (1-overlap)
# audio_file.reshape(-1,1).shape
for i in range(start, end, step):