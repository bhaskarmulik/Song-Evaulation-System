import streamlit as st
import eval_code

def main():
    st.title("Song Evaluation System")
    st.write("This is a system to evaluate songs.")
    st.write("Click the button below to evaluate a song.")
    # Get current query parameters
    query_params = st.experimental_get_query_params()
    current_page = query_params.get("page", ["main"])[0]

    # Render page based on query parameter
    if current_page == "eval_page":
        eval_code()

    # Button to navigate to evaluation page
    if st.button("Go to Evaluation Page"):
        # Set query parameter to navigate to eval_page
        st.query_params(page="eval_page")

    # if st.button("Evaluate Song"):
    #     # Redirect to the evaluation page
    #     st.experimental_rerun()

if __name__ == "__main__":
    main()
