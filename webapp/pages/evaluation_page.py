from pathlib import Path
import sys

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from eval_code import AudioEval


audio_eval = AudioEval()


def _grade_from_score(score: float) -> str:
    if score < 2000:
        return "A"
    if 2000 <= score < 6000:
        return "B"
    if 6000 <= score < 12000:
        return "C"
    if 12000 <= score < 17000:
        return "D"
    return "F"


def main():
    st.markdown(
        """
        <h1 style='text-align: center; color: white;'>🎙️ Evaluation Page 🎙️</h1>
        """,
        unsafe_allow_html=True,
    )
    st.divider()
    st.write(
        "Upload your singing audio (WAV) and the matching original track (WAV). "
        "The app then runs vocal extraction and computes comparison features."
    )
    st.divider()

    uploaded_file = st.file_uploader("👨 User Song", type=["wav"])
    st.divider()
    original_file = st.file_uploader("👨‍🎤 Original Song", type=["wav"])

    if uploaded_file is not None and original_file is not None:
        results = audio_eval.final_merge(uploaded_file, original_file)
        score = results["final_error"]
        grade = _grade_from_score(score)

        st.subheader(f"Evaluation Results: Grade {grade}")
        st.write(f"Final error score: {score:.2f}")
        st.pyplot(results["figure_audio"])
        st.pyplot(results["figure_pitch"])

        with st.expander("Show feature-level metrics"):
            st.json(results["metrics"])


if __name__ == "__main__":
    main()
