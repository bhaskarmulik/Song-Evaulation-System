from __future__ import annotations

from pathlib import Path
import sys

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from webapp.streamlit_runtime import get_database


def build_trend_figure(history: pd.DataFrame):
    figure, axes = plt.subplots(1, 2, figsize=(14, 4))
    axes[0].plot(history["attempt"], history["delta_pitch_error"], marker="o", label="Delta pitch error")
    axes[0].plot(history["attempt"], history["median_pitch_error"], marker="o", label="Median pitch error")
    axes[0].set_title("Pitch error trend")
    axes[0].set_xlabel("Attempt")
    axes[0].legend()

    axes[1].plot(history["attempt"], history["energy_error"], marker="o", color="#163172")
    axes[1].set_title("Energy error trend")
    axes[1].set_xlabel("Attempt")
    figure.tight_layout()
    return figure


def main() -> None:
    st.title("Results")
    database = get_database()
    users = database.list_user_names()
    default_user = st.session_state.get("current_user", users[0] if users else "Demo Singer")
    default_index = users.index(default_user) if users and default_user in users else 0
    profile = st.selectbox("Profile", options=users or [default_user], index=default_index)

    latest_result = st.session_state.get("latest_result")
    if latest_result is not None and latest_result.song_name:
        st.subheader("Current session")
        st.write(f"{latest_result.song_name}: grade {latest_result.grade}, score {latest_result.final_score:.2f}")
        with st.expander("Latest metrics"):
            st.json(latest_result.to_record())

    history = database.fetch_recent_evaluations(profile, limit=10)
    if not history:
        st.info("No evaluations stored for this profile yet. Run an evaluation first.")
        return

    history_df = pd.DataFrame(history)
    history_df = history_df.sort_values("created_at").reset_index(drop=True)
    history_df["attempt"] = history_df.index + 1

    st.subheader("Recent attempts")
    st.pyplot(build_trend_figure(history_df))
    st.dataframe(
        history_df[
            [
                "created_at",
                "song_title",
                "grade",
                "final_score",
                "delta_pitch_error",
                "median_pitch_error",
                "energy_error",
            ]
        ],
        use_container_width=True,
    )


if __name__ == "__main__":
    main()
