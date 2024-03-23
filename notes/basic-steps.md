Creating a machine learning model to isolate vocals from a mixed audio track (like music) is indeed a challenging task, but it's not impossible. Here are a few methods you could explore:

1. **Source Separation Techniques**: There are algorithms and models designed specifically for source separation, such as blind source separation (BSS) and independent component analysis (ICA). These methods aim to separate different sources from a mixed signal. However, separating vocals from music can be particularly challenging due to the overlapping frequency ranges and the complex nature of music.

2. **Deep Learning Models**: Deep learning models, particularly convolutional neural networks (CNNs) and recurrent neural networks (RNNs), have been used for audio source separation tasks. Models like U-Net, Wave-U-Net, and variants of recurrent neural networks have shown promise in separating vocals from music. These models are trained on large datasets of mixed audio and their corresponding isolated sources (in this case, vocals).

3. **Pre-trained Models and Transfer Learning**: You can leverage pre-trained models for audio processing tasks. Models like WaveNet or WaveGAN can be fine-tuned for source separation tasks. Transfer learning techniques can also be applied, where you take a pre-trained model on a related task (e.g., audio classification) and fine-tune it on your specific task of isolating vocals.

4. **Data Augmentation and Preprocessing**: Augmenting your dataset with various transformations like time stretching, pitch shifting, and adding noise can help improve the robustness of your model. Proper preprocessing techniques such as spectrogram computation and normalization are also crucial.

5. **Evaluation Metrics**: It's essential to define appropriate evaluation metrics for your model, such as signal-to-distortion ratio (SDR), signal-to-interference ratio (SIR), and signal-to-artifact ratio (SAR), to assess the quality of vocal separation accurately.

Keep in mind that while these methods can provide good results, complete isolation of vocals from music in all scenarios is extremely challenging and may not always yield perfect results. However, with careful experimentation and optimization, you can develop a model that performs reasonably well for many audio tracks.