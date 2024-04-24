import streamlit as st
import home_page
import evaluation_page
import results_page

# def switch_page(page_name: str):
#     from streamlit.runtime.scriptrunner import RerunData, RerunException
#     from streamlit.source_util import get_pages

#     def standardize_name(name: str) -> str:
#         return name.lower().replace("_", " ")

#     page_name = standardize_name(page_name)

#     pages = get_pages("home_page.py")  # OR whatever your main page is called

#     for page_hash, config in pages.items():
#         if standardize_name(config["page_name"]) == page_name:
#             raise RerunException(
#                 RerunData(
#                     page_script_hash=page_hash,
#                     page_name=page_name,
#                 )
#             )

#     page_names = [standardize_name(config["page_name"]) for config in pages.values()]

#     raise ValueError(f"Could not find page {page_name}. Must be one of {page_names}")

def main():
    st.title("Song Evaluation System")
    st.write("This is a system to evaluate songs.")
    st.write("Click the button below to evaluate a song.")
    

    if st.button("Evaluate Song"):
        # Redirect to the evaluation page
        st.switch_page('evaluation_page.py'
        )

if __name__ == "__main__":
    main()
