import streamlit as st
from eval_code import Audio_eval

audio_eval = Audio_eval()

def main():
    st.title("Evaluation Page")
    st.write("Upload an audio file for evaluation.")

    uploaded_file = st.file_uploader("Upload Audio File", type=["wav"])
    
    original_song = st.file_uploader("Upload original song", type=['wav'])

    if uploaded_file and original_song is not None:
        # Process the uploaded file
        evaluation_results = Audio_eval.final_merge(uploaded_file, original_song)
        
        st.write("Evaluation Results: ", evaluation_results)
        st.experimental_rerun()

if __name__ == "__main__":
    main()
