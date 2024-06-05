import streamlit as st
import image_to_text as tools  # This import is correct

# Set the title of the Streamlit app
st.title(":rainbow[Your Solutions Architect Assistant powered by Amazon Bedrock]")

# Set the header of the Streamlit app
st.header(":rainbow[Explanation and Code generated using Claude 3 Sonnet]")

# Create a container for file upload and user input
with st.container():
    st.subheader('Image File Upload:')
    file = st.file_uploader('Upload an Image', type=["png", "jpg", "jpeg"], key="diag")
    
    # Display the uploaded image if there is one
    if file is not None:
        st.image(file, caption='Uploaded Image', use_column_width=True)
    
    # Input field for an optional question
    text = st.text_input("OPTIONAL: Do you have a question about the image? Or about anything in general?")
    
    # Buttons to trigger actions
    result1 = st.button("Explain Diagram")
    result2 = st.button("Generate Terraform")

# Set the input text based on the button pressed
if result1:
    input_text = "You are an AWS Solutions Architect. The image you've received is an architecture diagram. Please explain the technical data flow in detail, step-by-step, and identify each AWS service used in the diagram."
elif result2:
    input_text = "Act as a DevOps Engineer. Carefully analyze the architecture in the image, identify all AWS services used, and their integration. For each service, generate Terraform code. Take your time and write the Terraform script step-by-step. Do your best and don't apologize. Provide code only, no text."
else:
    input_text = ""

# Ensure the function is called only if a file is uploaded and a button is pressed
if file is not None and (result1 or result2):
    # Use the 'tools' module to call 'image_to_text'
    # Temporarily save the uploaded file to pass its path to the function
    with open(file.name, "wb") as f:
        f.write(file.getbuffer())
    # Call the image_to_text function with the file path and input text
    st.write(tools.image_to_text(file.name, input_text))
