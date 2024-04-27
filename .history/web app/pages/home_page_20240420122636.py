import streamlit as st
from pages import evaluation_page

def main():
    st.title("Song Evaluation System")
    st.write("This is a system to evaluate songs.")
    st.write("Click the button below to evaluate a song.")
    

    if st.button("Evaluate Song"):
        # Redirect to the evaluation page
        st.page_link('pages/evaluation_page.py')

if __name__ == "__main__":
    main()
