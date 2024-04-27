import streamlit as st
from pages import home_page
from pages import evaluation_page
from pages import results_page

def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Home", "Evaluate Song", "Results"])

    if page == "Home":
        home_page.main()
    elif page == "Evaluate Song":
        evaluation_page.main()
    elif page == "Results":
        results_page.main()

if __name__ == "__main__":
    main()
