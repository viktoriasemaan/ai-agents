import base64
import io
import json
import os
import subprocess
import re
from typing import Type, Union, Dict, Any, List
import logging

import boto3
from langchain_community.embeddings import BedrockEmbeddings
from langchain_community.vectorstores import FAISS
from PIL import Image


bedrock_runtime = boto3.client(
    service_name="bedrock-runtime",
    region_name="us-east-1",
)


def load_json(path_to_json: str) -> Dict[str, Any]:
    """
    Purpose:
        Load json files
    Args:
        path_to_json (String): Path to  json file
    Returns:
        Conf: JSON file if loaded, else None
    """
    try:
        with open(path_to_json, "r") as config_file:
            conf = json.load(config_file)
            return conf

    except Exception as error:
        logging.error(error)
        raise TypeError("Invalid JSON file")


# function to convert a PIL image to a base64 string
def pil_to_base64(image, format="png"):
    with io.BytesIO() as buffer:
        image.save(buffer, format)
        return base64.b64encode(buffer.getvalue()).decode()


aws_service_to_module_mapping = load_json("diag_mapping.json")


def call_claude_3(
    system_prompt: str,
    prompt: str,
    model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0",
):

    prompt_config = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 4096,
        "system": system_prompt,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                ],
            }
        ],
    }

    body = json.dumps(prompt_config)

    modelId = model_id
    accept = "application/json"
    contentType = "application/json"

    response = bedrock_runtime.invoke_model(
        body=body, modelId=modelId, accept=accept, contentType=contentType
    )
    response_body = json.loads(response.get("body").read())

    results = response_body.get("content")[0].get("text")
    return results


def call_claude_3(
    system_prompt: str,
    prompt: str,
    model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0",
):

    prompt_config = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 4096,
        "system": system_prompt,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                ],
            }
        ],
    }

    body = json.dumps(prompt_config)

    modelId = model_id
    accept = "application/json"
    contentType = "application/json"

    response = bedrock_runtime.invoke_model(
        body=body, modelId=modelId, accept=accept, contentType=contentType
    )
    response_body = json.loads(response.get("body").read())

    results = response_body.get("content")[0].get("text")
    return results


def call_claude_3_code(
    system_prompt: str,
    prompt: str,
    model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0",
):

    prompt_config = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 4096,
        "stop_sequences": ["```"],
        "system": system_prompt,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                ],
            },
            {"role": "assistant", "content": "```"},
        ],
    }

    body = json.dumps(prompt_config)

    modelId = model_id
    accept = "application/json"
    contentType = "application/json"

    response = bedrock_runtime.invoke_model(
        body=body, modelId=modelId, accept=accept, contentType=contentType
    )
    response_body = json.loads(response.get("body").read())

    results = response_body.get("content")[0].get("text")
    return results


def gen_image_caption(base64_string):

    system_prompt = """

    You are an experienced AWS Solutions Architect with deep knowledge of AWS services and best practices for designing and implementing cloud architectures. Maintain a professional and consultative tone, providing clear and detailed explanations tailored for technical audiences. Your task is to describe and explain AWS architecture diagrams presented by users. Your descriptions should cover the purpose and functionality of the included AWS services, their interactions, data flows, and any relevant design patterns or best practices.
    """

    prompt_config = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 4096,
        "system": system_prompt,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": base64_string,
                        },
                    },
                    {
                        "type": "text",
                        "text": "Please describe the following AWS architecture diagram, explaining the purpose of each service, their interactions, and any relevant design considerations or best practices.",
                    },
                ],
            }
        ],
    }

    body = json.dumps(prompt_config)

    modelId = "anthropic.claude-3-sonnet-20240229-v1:0"
    accept = "application/json"
    contentType = "application/json"

    response = bedrock_runtime.invoke_model(
        body=body, modelId=modelId, accept=accept, contentType=contentType
    )
    response_body = json.loads(response.get("body").read())

    results = response_body.get("content")[0].get("text")
    return results


def call_claude_3_fill(
    system_prompt: str,
    prompt: str,
    model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0",
):

    prompt_config = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 4096,
        "system": system_prompt,
        "stop_sequences": ["```"],
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                ],
            },
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "text",
                        "text": "Here is the code with no explanation ```python",
                    },
                ],
            },
        ],
    }

    body = json.dumps(prompt_config)

    modelId = model_id
    accept = "application/json"
    contentType = "application/json"

    response = bedrock_runtime.invoke_model(
        body=body, modelId=modelId, accept=accept, contentType=contentType
    )
    response_body = json.loads(response.get("body").read())

    results = response_body.get("content")[0].get("text")
    return results


def aws_well_arch_tool(query):
    """
    Use this tool for any AWS related question to help customers understand best practices on building on AWS. It will use the relevant context from the AWS Well-Architected Framework to answer the customer's query. The input is the customer's question. The tool returns an answer for the customer using the relevant context.
    """

    # Find docs
    embeddings = BedrockEmbeddings()
    vectorstore = FAISS.load_local(
        "local_index", embeddings, allow_dangerous_deserialization=True
    )
    docs = vectorstore.similarity_search(query)
    context = ""

    doc_sources_string = ""
    for doc in docs:
        doc_sources_string += doc.metadata["source"] + "\n" + doc.page_content
        context += doc.page_content

    prompt = f"""Use the following pieces of context to answer the question at the end.

    {context}

    Question: {query}
    Answer:"""

    system_prompt = """
    You are an expert certfied AWS solutions architect professional, skilled at helping customers solve thier problems. You are able to reference context from the AWS Well-Architected Framework to help customers solve their problem.
    """

    generated_text = call_claude_3(system_prompt, prompt)
    print(generated_text)

    resp_json = {"ans": str(generated_text), "docs": doc_sources_string}

    return resp_json


# helper functions
def save_and_run_python_code(code: str, file_name: str = "/tmp/test_diag.py"):
    # Save the code to a file
    with open(file_name, "w") as file:
        file.write(code)

    # Run the code using a subprocess
    try:
        os.chdir("/tmp")
        result = subprocess.run(
            ["python", file_name], capture_output=True, text=True, check=True
        )
        # go back...
    except subprocess.CalledProcessError as e:
        print("Error occurred while running the code:")
        print(e.stdout)
        print(e.stderr)


def process_code(code):
    # Split the code into lines
    lines = code.split("\n")

    # Initialize variables to store the updated code and diagram filename
    updated_lines = []
    diagram_filename = None
    inside_diagram_block = False

    for line in lines:
        if line == ".":
            line = line.replace(".", "")
        if "endoftext" in line:
            line = ""
        if "# In[" in line:
            line = ""
        if line == "```":
            line = ""

        # Check if the line contains "with Diagram("
        if "with Diagram(" in line:
            # replace / in the line with _
            line = line.replace("/", "_")

            # Extract the diagram name between "with Diagram('NAME',"
            diagram_name = (
                line.split("with Diagram(")[1].split(",")[0].strip("'").strip('"')
            )

            # Convert the diagram name to lowercase, replace spaces with underscores, and add ".png" extension
            diagram_filename = (
                diagram_name.lower()
                .replace(" ", "_")
                .replace(")", "")
                .replace('"', "")
                .replace("/", "_")
                .replace(":", "")
                + ".png"
            )

            # Check if the line contains "filename="
            if "filename=" in line:
                # Extract the filename from the "filename=" parameter
                diagram_filename = (
                    line.split("filename=")[1].split(")")[0].strip("'").strip('"')
                    + ".png"
                )

            inside_diagram_block = True

        # Check if the line contains the end of the "with Diagram:" block
        if inside_diagram_block and line.strip() == "":
            inside_diagram_block = False

        # TODO: not sure if it handles all edge cases...
        # Only include lines that are inside the "with Diagram:" block or not related to the diagram
        if inside_diagram_block or not line.strip().startswith("diag."):
            updated_lines.append(line)

    # Join the updated lines to create the updated code
    updated_code = "\n".join(updated_lines)

    return updated_code, diagram_filename


def correct_imports(code):
    # Detect all AWS services mentioned in the code
    detected_services = [
        service for service in aws_service_to_module_mapping if service in code
    ]

    # Determine the correct imports based on the detected services
    module_to_services = {}
    for service in detected_services:
        module = aws_service_to_module_mapping[service]
        if module not in module_to_services:
            module_to_services[module] = []
        module_to_services[module].append(service)

    # Construct the corrected import lines
    corrected_imports = []
    for module, services in module_to_services.items():
        services_str = ", ".join(services)
        corrected_imports.append(f"from diagrams.aws.{module} import {services_str}")

    # Replace the original import lines in the code with the corrected ones
    code_without_imports = re.sub(r"from diagrams.aws.* import .*", "", code)
    corrected_code = "\n".join(corrected_imports) + "\n" + code_without_imports

    return corrected_code.strip()


def diagram_tool(query):
    """
    This is a tool that generates diagrams based on a customers's request.
    """

    system_prompt = f"""
    You are an expert python programmer that has mastered the Diagrams library. You are able to write code to generate AWS diagrams based on what the user asks. Only return the code as it will be run through a program to generate the diagram for the user. Here is the full list of services supported along with the correct import from the library: {aws_service_to_module_mapping}
    """

    code = call_claude_3_fill(system_prompt, query)
    print("Base code:")
    print(code)

    # Clean up hallucinated code
    code, file_name = process_code(code)
    code = code.replace("```python", "").replace("```", "").replace('"""', "")
    # code = correct_imports(code)

    print("Cleaned code:")
    print(code)

    try:
        # Code to run
        save_and_run_python_code(code)
    except Exception as e:
        print(e)
        return
    # Open in tmp
    img = Image.open(f"/tmp/{file_name}")
    return img


def remove_first_line(text):
    lines = text.split("\n")
    if len(lines) > 1:
        lines = lines[1:]
    return "\n".join(lines)

def code_gen_tool(prompt):
    """
    Use this tool only when you need to generate code based on a customers's request. The input is the customer's question. The tool returns code that the customer can use.
    """
    system_prompt = """
    You are an expert programmer with extensive knowledge of various programming languages and frameworks. Maintain a professional and efficient tone, focusing on providing concise and accurate code solutions. Your task is to provide code solutions to programming problems or requirements posed by users. The code should be well-commented, efficient, and follow best practices. You should not provide any explanations or additional context unless explicitly requested. The code should be formatted correctly and ready to be copied and pasted into an editor.
    """

    generated_text = call_claude_3_code(system_prompt, prompt)
    # remove first line
    generated_text = remove_first_line(generated_text)

    return generated_text
