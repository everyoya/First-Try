import streamlit as st

# Initialize session state to hold user input and navigation
if 'page' not in st.session_state:
    st.session_state.page = 'intro'

if st.session_state.page == 'intro':
    st.title("👋 Welcome to My First Streamlit App")

    st.write("""
    This simple app demonstrates basic navigation between pages using Streamlit.
    
    You’ll enter your name below and get a personalized welcome message on the next page!
    """)

    first_name = st.text_input("First Name")
    last_name = st.text_input("Last Name")

    if st.button("Continue"):
      if first_name and last_name:
        st.session_state.first_name = first_name
        st.session_state.last_name = last_name
        st.session_state.page = 'welcome'
        st.rerun()  # <-- the updated method!
    else:
        st.warning("Please enter both your first and last name.")

elif st.session_state.page == 'welcome':
    st.title(f"🎉 Welcome, {st.session_state.first_name} {st.session_state.last_name}!")
    st.write("You're now on the second page of the app. Glad to have you here!")

