import streamlit as st

# Import your evaluation and results pages (assuming they're separate Python files)
import evaluation_page
import results_page

# Function to switch between different pages in the Streamlit app
def switch_page(page_name: str):
    from streamlit.runtime.scriptrunner import RerunData, RerunException
    from streamlit.source_util import get_pages

    def standardize_name(name: str) -> str:
        return name.lower().replace("_", " ")

    page_name = standardize_name(page_name)

    # Get all pages registered in Streamlit
    pages = get_pages("home_page.py")  # Specify the name of your main page here

    # Check if the requested page exists and rerun Streamlit to navigate to it
    for page_hash, config in pages.items():
        if standardize_name(config["page_name"]) == page_name:
            raise RerunException(
                RerunData(
                    page_script_hash=page_hash,
                    page_name=page_name,
                )
            )

    # If the page doesn't exist, display an error message
    page_names = [standardize_name(config["page_name"]) for config in pages.values()]
    raise ValueError(f"Could not find page {page_name}. Must be one of {page_names}")

def main():
    # Set a background image using HTML
    st.set_page_config(
        page_title="Song Evaluation System",
        page_icon="",  # Optional: Add a music note icon
        layout="wide",  # Wide layout for better aesthetics
    )

    background_image = """
    <style>
        body {
            background-image: url("path/to/your/background_image.jpg");
            background-size: cover;
        }
    </style>
    """
    st.sidebar.markdown(background_image, unsafe_allow_html=True)

    # Title and Introduction with centered text
    st.markdown("""
    <h1 style="text-align: center; color: white;">Song Evaluation System</h1>
    <p style="text-align: center; color: white;">Welcome to the professional song evaluation platform.</p>
    """, unsafe_allow_html=True)

    # Button to trigger evaluation process and redirect to evaluation page
    if st.button("Evaluate Your Song", class_="custom-btn"):  # Add custom button class
        switch_page('evaluation_page.py')

    # Information section with columns for better layout
    col1, col2 = st.columns(2)
    with col1:
        st.header("How It Works")
        st.write(
            "This system employs advanced audio processing techniques to analyze songs. After uploading a song, it undergoes various evaluations including feature extraction, error calculation, and analysis."
        )
    with col2:
        st.header("Key Features")
        st.write(
            """
            - Advanced Pitch Analysis
            - Mel-frequency cepstral coefficients (MFCCs) extraction
            - Detailed Error Calculation
            - Singing Power Ratio Evaluation
            """
        )

    # View Results section with a disabled button (to be enabled later)
    st.write("**View Results of Previous Evaluations**")
    view_results_button = st.button("View Results", disabled=True)

    # About section
    st.header("About")
    st.write("This project is developed as part of a mini-project. For more information, contact the developer.")

    # Handle button clicks for future result viewing functionality
    if view_results_button:
        switch_page('results_page.py')  # Enable results page button later

if __name__ == "__main__":
    main()
