from __future__ import annotations

from pathlib import Path
import sys

import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from webapp.core import AudioEvaluator
from webapp.services.storage import persist_uploaded_file
from webapp.streamlit_runtime import get_cached_separator, get_database


def render_result(result) -> None:
    st.subheader(f"Latest Evaluation: Grade {result.grade}")
    st.write(f"Final score: {result.final_score:.2f}")
    st.pyplot(result.figures["audio_signal"])
    st.pyplot(result.figures["pitch_features"])
    with st.expander("Feature-level metrics"):
        st.json(result.to_record())


def main() -> None:
    st.title("Evaluation")
    st.write(
        "Upload a cover and the matching original track. The app isolates vocals, aligns the "
        "performance with DTW, computes scoring metrics, and stores the result in SQLite."
    )

    current_user = st.session_state.get("current_user", "Demo Singer")
    user_name = st.text_input("Profile name", value=current_user, help="Used for local evaluation history.")
    song_name = st.text_input("Song title", value=st.session_state.get("current_song_name", ""))
    cover_file = st.file_uploader("Cover track", type=["wav", "mp3"])
    original_file = st.file_uploader("Reference track", type=["wav", "mp3"])

    if st.button("Evaluate cover", type="primary", disabled=not (cover_file and original_file and user_name.strip())):
        st.session_state["current_user"] = user_name.strip()
        st.session_state["current_song_name"] = song_name.strip()

        with st.spinner("Saving uploads and loading the separator model..."):
            separator = get_cached_separator()
            database = get_database()
            saved_cover = persist_uploaded_file(cover_file, user_name, "cover")
            saved_original = persist_uploaded_file(original_file, user_name, "reference")

        evaluator = AudioEvaluator(separator=separator)
        resolved_song_name = song_name.strip() or Path(original_file.name).stem

        with st.spinner("Evaluating audio..."):
            result = evaluator.evaluate(
                user_audio_path=saved_cover,
                original_audio_path=saved_original,
                song_name=resolved_song_name,
            )
            database.save_evaluation(
                user_name=user_name.strip(),
                song_title=resolved_song_name,
                reference_filename=original_file.name,
                cover_filename=cover_file.name,
                cover_path=str(saved_cover),
                original_path=str(saved_original),
                result=result,
            )

        st.session_state["latest_result"] = result
        st.success("Evaluation saved. Open the Results page from the sidebar to review your history.")

    latest_result = st.session_state.get("latest_result")
    if latest_result is not None:
        st.divider()
        render_result(latest_result)


if __name__ == "__main__":
    main()
