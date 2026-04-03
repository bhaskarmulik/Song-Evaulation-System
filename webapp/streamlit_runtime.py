from __future__ import annotations

import streamlit as st

from webapp.services.database import Database
from webapp.services.model_loader import load_separator_model


@st.cache_resource(show_spinner=False)
def get_cached_separator():
    return load_separator_model()


@st.cache_resource(show_spinner=False)
def get_database() -> Database:
    database = Database()
    database.initialize()
    return database
