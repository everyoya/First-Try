import streamlit as st

st.title('First Try')

st.write('Hello world!')
st.write('Hello world!!!!!!!!')
st.write('Hello world!!!!!!!!')

a=st.text_area('Type in the text_area and click copy')

if st.button('Copy'):
    pyperclip.copy(a)
    st.success('Text copied successfully!')
