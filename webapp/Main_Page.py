import streamlit as st


def main():
    st.set_page_config(page_title="Song Evaluation System", page_icon="🎤", layout="centered")

    st.markdown(
        """
        <h1 style='text-align: center; color: white;'>🎤 Song Evaluation System 🎤</h1>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <strong style='text-align: left; color: white;'>
        Welcome to the Song Evaluation System. This app evaluates a cover performance by
        comparing uploaded user and original tracks with MFCC, pitch, energy, and singing
        power features. Use the Streamlit Pages navigation to open the Evaluation page.
        </strong>
        """,
        unsafe_allow_html=True,
    )
    st.divider()

    st.markdown(
        """
        <h2 style='text-align: center; color: white;'>🚀 How it works</h2>
        """,
        unsafe_allow_html=True,
    )
    st.write(
        "This system isolates vocals with OpenUnmix before extracting and comparing "
        "acoustic features from both songs."
    )

    st.header("🎼 Pitch Features Used")
    st.markdown("- **Pitch Detection**: Identifies pitch values throughout the song.")
    st.markdown("- **Median Subtraction**: Normalizes pitch fluctuations.")
    st.markdown("- **Pitch Error Calculation**: Compares user and original pitch behavior.")

    st.header("🔊 Features")
    st.markdown("- **MFCC Analysis** for timbral/phonetic information.")
    st.markdown("- **Energy Error Calculation** for loudness contour differences.")
    st.markdown("- **Range of Pitch (RoP) Error** for vocal range differences.")
    st.markdown("- **Singing Power Ratio** for vocal projection characteristics.")


if __name__ == "__main__":
    main()
