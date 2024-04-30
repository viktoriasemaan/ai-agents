import streamlit as st
import image_to_text as tools  # This import is correct

st.title(f""":rainbow[Your Solutions Architect Assistant powered by Amazon Bedrock]""")

st.header(f""":rainbow[Explanation and Code generated using Claude 3 Sonnet]""")
with st.container():
    st.subheader('Image File Upload:')
    File = st.file_uploader('Upload an Image', type=["png", "jpg", "jpeg"], key="diag")
    if File is not None:
        st.image(File, caption='Uploaded Image', use_column_width=True)
    text = st.text_input("OPTIONAL: Do you have a question about the image? Or about anything in general?")
    result1 = st.button("Explain Diagram")
    result2 = st.button("Generate Terraform")
    
if result1:
    input_text = "You are an AWS Solutions Architect. The image you've received is an architecture diagram. Please explain the technical data flow in detail, step-by-step, and identify each AWS service used in the diagram."
elif result2:
    input_text = "Act as a DevOps Engineer. Carefully analyze the architecture in the image, identify all AWS services used, and their integration. For each service, generate Terraform code. Take your time and write the Terraform script step-by-step. Do your best and don't apologize. Provide code only, no text."
else:
    input_text = ""

# Ensure we only call the function if a file is uploaded and a button is pressed
if File is not None and (result1 or result2):
    # Use the 'tools' module to call 'image_to_text'
    # Temporarily saving the uploaded file to pass its path to your function
    with open(File.name, "wb") as f:
        f.write(File.getbuffer())
    st.write(tools.image_to_text(File.name, input_text))



