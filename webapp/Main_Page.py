import streamlit as st


def main():
    st.set_page_config(page_title="Song Evaluation System", page_icon="🎤", layout="wide")

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
        power features. Use the Streamlit sidebar to move between evaluation and results.
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
        "This system isolates vocals with OpenUnmix, aligns cover and reference features "
        "with Dynamic Time Warping, and stores every evaluation in SQLite so progress is visible over time."
    )

    col1, col2 = st.columns(2)
    with col1:
        st.header("Evaluation Engine")
        st.markdown("- **OpenUnmix vocal separation** isolates the singing voice.")
        st.markdown("- **DTW alignment** reduces penalties from small timing differences.")
        st.markdown("- **Weighted scoring** combines MFCC, pitch, energy, range, and power metrics.")
    with col2:
        st.header("Workflow")
        st.markdown("- **Evaluation page** uploads files and runs analysis.")
        st.markdown("- **Session state** keeps the latest result available across pages.")
        st.markdown("- **Results page** charts the last 10 attempts for each local profile.")


if __name__ == "__main__":
    main()
