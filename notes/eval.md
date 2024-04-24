Evaluation Metrics Used

- **Frequency Intonation (Pitch Accuracy):**
  - Fundamental frequency used for the waveform
  - Increase the range of search for the fundamental frequency
  - To avoid key transposition:
    - Taking derivatives of pitch contours: \( \delta p = p_A - p_B \) where \( p_A \) is the current pitch vector and \( p_B \) is the pitch vector lagged by certain frames
    - Median subtracted pitch: \( p_{\text{medsub}} = p - \text{median}\{p\} \)

- **Rhythm Consistency:**
  - DTW = \( |A_i - B_i| \) and then choosing the minimum path from the cost matrix
  - It calculates the change between the two time frames and adds to them the previous frame DTW value
  - Instead of performing DTW over pitch for rhythm consistency, we do it over MFCCs.

- **Volume:**
  - Use short-term log energy and compute DTW dist over ref and test features

- **Pitch Dynamic Range:**
  - Difference between the highest and lowest pitch possible

- **PESQ Principle:**
  - Penalize larger errors over smaller errors (For that, we can use the root mean square or just square the DTW dist)

- **Internal Deviation Criterion**

- **Tonality Modulation**

- **SPR:**
  - \( Pv_{\text{mod}}(t) = \int_{-\infty}^{\infty} FL \times X(ft) \, df \times X(ft) \, df \)