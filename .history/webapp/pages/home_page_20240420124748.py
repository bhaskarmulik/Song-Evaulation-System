import streamlit as st
import home_page
import evaluation_page
import results_page
import apputils as vutils

def main():
    st.title("Song Evaluation System")
    st.write("This is a system to evaluate songs.")
    st.write("Click the button below to evaluate a song.")
    

    if st.button("Evaluate Song"):
        # Redirect to the evaluation page
        apputils.switch_page("evaluation_page")

if __name__ == "__main__":
    main()
