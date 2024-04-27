import streamlit as st
from pages import Evaluation_Page
# from pages import Results_Page
import hydralit_components as hc
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
    #Navbar

    # define what option labels and icons to display
    option_data = [
    {'icon': "🏠", 'label':"Home"},
    {'icon':"",'label':"Evaluate"},
    ]

    # override the theme, else it will use the Streamlit applied theme
    over_theme = {'txc_inactive': 'white','menu_background':'#D6E5FA','txc_active':'white','option_active':'#749BC2'}
    font_fmt = {'font-class':'h2','font-size':'150%'}

    # display a horizontal version of the option bar
    op = hc.option_bar(option_definition=option_data,key='PrimaryOption',override_theme=over_theme,font_styling=font_fmt,horizontal_orientation=True)

    if op == 'Evaluate':
        Evaluation_Page.main()
        






    # Set the title and introduction of the Streamlit app
    #Please add a emoticon to the title
    # st.set_page_config(
    # page_title="Home page",
    # page_icon="👋",
    # layout="centered")
    #CAn you insert some other emoticon for music in the title
    
    st.markdown(
        """
        <h1 style='text-align: center; color: white;'>🎤 Song Evaluation System 🎤</h1>
        """
    , unsafe_allow_html=True)

    # Provide an overview of the evaluation process
    st.markdown(
        """
        <strong style='text-align: left; color: white;'>Welcome to the Song Evaluation System. This system allows you to evaluate songs based on various criteria.To get started, click the Evaluation Page in the sidebar.</strong>"""
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

    st.header("🎼Pitch Features Used")
    st.write("Pitch is an important aspect of music evaluation. This system utilizes the following pitch-related features:")
    st.markdown("- **Pitch Detection**: Identifies pitch values throughout the song.")
    st.markdown("- **Median Subtraction**: Subtracts median pitch value to normalize pitch fluctuations.")
    st.markdown("- **Pitch Error Calculation**: Measures discrepancies in pitch between user and original audio.")

    st.header("🔊Features")
    st.write("The evaluation includes:")
    st.markdown("- **MFCC Analysis**: Extracts Mel-frequency cepstral coefficients (MFCCs) for audio features.")
    st.markdown("- **Energy Error Calculation**: Measures discrepancies in energy between user and original audio.")
    st.markdown("- **Range of Pitch (RoP) Error**: Compares ranges of pitches across the user and original songs.")
    st.markdown("- **Singing Power Ratio**: Evaluates the balance between low and high-frequency intensities.")

    st.divider()

    st.markdown(
        """
        <h1 style='text-align: center; color: white;'>👨‍🎤About Us</h1>
        """
    , unsafe_allow_html=True)
    st.write("This project is developed as part of a mini-project. The mini-project aims to showcase the application of machine learning and audio processing techniques in music evaluation. The system is designed to provide insights into the quality and characteristics of songs as well as the proficiency of two songs.")

# Entry point to run the Streamlit app
if __name__ == "__main__":
    main()
