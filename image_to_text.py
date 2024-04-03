import os
import base64
import io
from PIL import Image
import boto3
import json



bedrock_runtime = boto3.client(
    service_name="bedrock-runtime",
    region_name="us-west-2",
)


def image_base64_encoder(image_name):
    open_image = Image.open(image_name)
    image_bytes = io.BytesIO()
    open_image.save(image_bytes, format=open_image.format)
    image_bytes = image_bytes.getvalue()
    image_base64 = base64.b64encode(image_bytes).decode('utf-8')
    file_type = f"image/{open_image.format.lower()}"
    return file_type, image_base64


def image_to_text(image_name, text) -> str:
    file_type, image_base64 = image_base64_encoder(image_name)
    system_prompt = """Carefully analyze this image, take your time, be extremely thorough and detailed. Then explain configuration of this diagram step-by-step as information flows. 

    If a more specific question is presented by the user, make sure to prioritize that answer.
    """
    if text == "":
        text = "Use the system prompt"
    prompt = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 10000,
        "temperature": 0.5,
        "system": system_prompt,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": file_type,
                            "data": image_base64
                        }
                    },
                    {
                        "type": "text",
                        "text": text
                    }
                ]
            }
        ]
    }
    json_prompt = json.dumps(prompt)
    response = bedrock_runtime.invoke_model(body=json_prompt, modelId="anthropic.claude-3-sonnet-20240229-v1:0",
                                    accept="application/json", contentType="application/json")
    response_body = json.loads(response.get('body').read())
    llm_output = response_body['content'][0]['text']
    return llm_output
    
    
    
    # Replace 'path_to_your_image.jpg' with the actual path to your image file
image_path = 'image.jpeg'
text_input = "desribe this architecture diagram in details"  # You can put specific instructions here if needed

# Call the function
output_text = image_to_text(image_path, text_input)

# Print the result
print(output_text)

