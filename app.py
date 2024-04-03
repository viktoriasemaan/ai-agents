import streamlit as st
import image_to_text as tools  # This import is correct

st.title(f""":rainbow[Your Solutions Architect Assistant powered by Amazon Bedrock]""")

st.header(":rainbow: Diagram Analysis provided by Claude 3")
with st.container():
    st.subheader('Image File Upload:')
    File = st.file_uploader('Upload an Image', type=["png", "jpg", "jpeg"], key="diag")
    text = st.text_input("OPTIONAL: Do you have a question about the image? Or about anything in general?")
    result1 = st.button("Explain Diagram")
    result2 = st.button("Generate CloudFormation")
    
if result1:
    input_text = "You are a AWS solution architect. The image provided is an architecture diagram. Explain the technical data flow in detail."
elif result2:
    input_text = "You are a AWS solution architect. The image provided is an architecture diagram. Provide cloudformation code to implement this diagram to help me get started"
else:
    input_text = ""

# Ensure we only call the function if a file is uploaded and a button is pressed
if File is not None and (result1 or result2):
    # Use the 'tools' module to call 'image_to_text'
    # Temporarily saving the uploaded file to pass its path to your function
    with open(File.name, "wb") as f:
        f.write(File.getbuffer())
    st.write(tools.image_to_text(File.name, input_text))


