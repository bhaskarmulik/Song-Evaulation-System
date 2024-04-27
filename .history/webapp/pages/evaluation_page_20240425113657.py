import streamlit as st
import sys
import os
sys.path.insert(0, os.path.abspath('D:\Yash Mulik Study\Mini-Project\github_codespace\Song-Evaulation-System\webapp'))
from eval_code import Audio_eval


audio_eval = Audio_eval()

def main():
    st.markdown(
        """
        <h1 style='text-align: center; color: white;'>🎙️Evaluation Page🎙️</h1>
        """
    , unsafe_allow_html=True)
    st.divider()
    st.write("To evaluate your singing proficiency, please upload your audio file as well as the original song. The evaluation process begins as soon as the two files are uploaded")

    st.divider()

    uploaded_file = st.file_uploader("👨User Song👩", type=["wav"])

    st.divider()
    
    original_file = st.file_uploader("👨‍🎤Original Song👩‍🎤", type=['wav'])

    if uploaded_file and original_file is not None:
        # Process the uploaded file
        evaluation_results = audio_eval.final_merge(uploaded_file, original_file)
        grade = None
        if evaluation_results < 2000:
            grade = 'A'
        elif evaluation_results >= 200 and evaluation_results < 6000:
            grade = 'B'
        elif evaluation_results >=6000 and evaluation_results < 12000:
            grade = 'C'
        elif evaluation_results >=12000 and evaluation_results < 17000:
            grade = 'D'
        elif evaluation_results >= 17000:
            grade = 'F'
        st.write("Evaluation Results: You have recieved GRADE : ", grade)
        # st.experimental_rerun()

if __name__ == "__main__":
    main()
