import streamlit as st
import sys
import os
import time
import hydralit_components as hc
sys.path.insert(0, os.path.abspath('D:\Yash Mulik Study\Mini-Project\github_codespace\Song-Evaulation-System\webapp'))
from eval_code import Audio_eval


audio_eval = Audio_eval()

def main():
    st.title("Evaluation Page")
    st.write("Upload an audio file for evaluation.")

    uploaded_file = st.file_uploader("Upload Audio File", type=["wav"])
    
    original_file = st.file_uploader("Upload original song", type=['wav'])
    with uploaded_file and original_file is not None and hc.HyLoader('Now doing loading',hc.Loaders.pulse_bars,):
        time.sleep(5)        
            

        # evaluation_results = audio_eval.final_merge(uploaded_file, original_file)
        # st.write("Evaluation Results: ", evaluation_results)
        # # st.experimental_rerun()

if __name__ == '__main__':
    main()
