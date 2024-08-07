import streamlit as st
from pages import Evaluation_Page
from pages import Results_Page

# Function to switch between different pages in the Streamlit app
# def switch_page(page_name: str):
#     from streamlit.runtime.scriptrunner import RerunData, RerunException
#     from streamlit.source_util import get_pages

#     def standardize_name(name: str) -> str:
#         return name.lower().replace("_", " ")

#     page_name = standardize_name(page_name)

#     # Get all pages registered in Streamlit
#     pages = get_pages("home_page.py")  # Specify the name of your main page here

#     # Check if the requested page exists and rerun Streamlit to navigate to it
#     for page_hash, config in pages.items():
#         if standardize_name(config["page_name"]) == page_name:
#             raise RerunException(
#                 RerunData(
#                     page_script_hash=page_hash,
#                     page_name=page_name,
#                 )
#             )

#     # If the page doesn't exist, display an error message
#     page_names = [standardize_name(config["page_name"]) for config in pages.values()]
#     raise ValueError(f"Could not find page {page_name}. Must be one of {page_names}")

# Main function to define the Streamlit app
def main():
    

    # Set the title and introduction of the Streamlit app
    #Please add a emoticon to the title
    st.set_page_config(
    page_title="Home page",
    page_icon="👋",
    layout="centered")
    #CAn you insert some other emoticon for music in the title
    st.title("🎤 Song Evaluation System 🎤")
    st.write("Welcome to the Song Evaluation System. This system allows you to evaluate songs based on various criteria.")

    # Provide an overview of the evaluation process
    st.markdown(
        """
        <h3 style='text-align: left; color: white;'>To get started, click the Evaluation Page in the sidebar.</h3>"""
    , unsafe_allow_html=True)
    st.divider()

    # Button to trigger evaluation process and redirect to evaluation page
    # if st.button("Evaluate Song"):
    #     # Use the custom function to switch to the evaluation page
    #     st.page_link('\webapp\pages\evaluation_page.py', label='Evaluation Page')

    # Display additional information about the system
    st.markdown(
        """
        <h1 style='text-align: center; color: white;'>🚀How it works</h1>
        """
    , unsafe_allow_html=True)
    st.write("This system employs advanced audio processing techniques to analyze songs. After uploading a song, it undergoes various evaluations including feature extraction, error calculation, and analysis.")

    st.header("Pitch Features Used")
    st.write("Pitch is an important aspect of music evaluation. This system utilizes the following pitch-related features:")
    st.markdown("- **Pitch Detection**: Identifies pitch values throughout the song.")
    st.markdown("- **Median Subtraction**: Subtracts median pitch value to normalize pitch fluctuations.")
    st.markdown("- **Pitch Error Calculation**: Measures discrepancies in pitch between user and original audio.")

    st.header("Features")
    st.write("The evaluation includes:")
    st.markdown("- **MFCC Analysis**: Extracts Mel-frequency cepstral coefficients (MFCCs) for audio features.")
    st.markdown("- **Energy Error Calculation**: Measures discrepancies in energy between user and original audio.")
    st.markdown("- **Rate of Perceived Pitch (RoP) Error**: Compares perceived pitch rates.")
    st.markdown("- **Singing Power Ratio**: Evaluates the balance between low and high-frequency intensities.")

    st.divider()

    st.markdown(
        """
        <h1 style='text-align: center; color: white;'>About Us</h1>
        """
    , unsafe_allow_html=True)
    st.write("This project is developed as part of a mini-project. The mini-project aims to showcase the application of machine learning and audio processing techniques in music evaluation. The system is designed to provide insights into the quality and characteristics of songs as well as the proficiency of two songs.")

# Entry point to run the Streamlit app
if __name__ == "__main__":
    main()
