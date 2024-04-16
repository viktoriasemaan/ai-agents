import json

import boto3
from langchain_community.embeddings import BedrockEmbeddings
from langchain_community.vectorstores import FAISS



bedrock_runtime = boto3.client(
    service_name="bedrock-runtime",
    region_name="us-west-2",
)

def call_claude_sonnet(prompt):

    prompt_config = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 4096,
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

    modelId = "anthropic.claude-3-sonnet-20240229-v1:0"
    accept = "application/json"
    contentType = "application/json"

    response = bedrock_runtime.invoke_model(
        body=body, modelId=modelId, accept=accept, contentType=contentType
    )
    response_body = json.loads(response.get("body").read())

    results = response_body.get("content")[0].get("text")
    return results

def claude_prompt_format(prompt: str) -> str:
    # Add headers to start and end of prompt
    return "\n\nHuman: " + prompt + "\n\nAssistant:"

def call_claude(prompt):
    prompt_config = {
        "prompt": claude_prompt_format(prompt),
        "max_tokens_to_sample": 4096,
        "temperature": 0.7,
        "top_k": 250,
        "top_p": 0.5,
        "stop_sequences": [],
    }

    body = json.dumps(prompt_config)

    modelId = "anthropic.claude-v2"
    accept = "application/json"
    contentType = "application/json"

    response = bedrock_runtime.invoke_model(
        body=body, modelId=modelId, accept=accept, contentType=contentType
    )
    response_body = json.loads(response.get("body").read())

    results = response_body.get("completion")
    return results


# Call Titan model
def call_titan(prompt):
    prompt_config = {
        "inputText": prompt,
        "textGenerationConfig": {
            "maxTokenCount": 4096,
            "stopSequences": [],
            "temperature": 0.7,
            "topP": 1,
        },
    }

    body = json.dumps(prompt_config)

    modelId = "amazon.titan-text-lite-v1"
    accept = "application/json"
    contentType = "application/json"

    response = bedrock_runtime.invoke_model(
        body=body, modelId=modelId, accept=accept, contentType=contentType
    )
    response_body = json.loads(response.get("body").read())

    print(response_body)

    results = response_body.get("results")[0].get("outputText")
    return results


def aws_well_arch_tool(query):
    """
    Use this tool for any AWS related question to help customers understand best practices on building on AWS. It will use the relevant context from the AWS Well-Architected Framework to answer the customer's query. The input is the customer's question. The tool returns an answer for the customer using the relevant context.
    """

    # Find docs
    embeddings = BedrockEmbeddings()
    vectorstore = FAISS.load_local("local_index", embeddings, allow_dangerous_deserialization=True)
    docs = vectorstore.similarity_search(query)
    context = ""

    doc_sources_string = ""
    for doc in docs:
        doc_sources_string += doc.metadata["source"] + "\n"
        context += doc.page_content

    prompt = f"""Use the following pieces of context to answer the question at the end.

    {context}

    Question: {query}
    Answer:"""

    generated_text = call_claude_sonnet(prompt)
    print(generated_text)

    resp_string = (
        generated_text
        + "\n Here is some documentation for more details: \n"
        + doc_sources_string
    )
    return resp_string


def code_gen_tool(prompt):
    """
    Use this tool only when you need to generate code based on a customers's request. The input is the customer's question. The tool returns code that the customer can use.
    """
    prompt_ending = " Just return the code, do not provide an explanation."
    generated_text = call_claude_sonnet(prompt + prompt_ending)
    return generated_text

def estimate_chost(prompt):
    """
    Use this tool only when you need to say how much will be cost infrastucture on AWS, split on areas based on type services provide. The tool returns price per AWS service, and total summ of the whole infrastucture.
    """
    prompt_ending = "Above is an estimation on the cost of infrastructure in AWS cloud, analyze and give the result - how much each service will cost. For example, if there will be several items of RDS costs, you should specify the total amount, you do not need to give all calculations, just the name of the service and its cost per month. This should be done for all services. And also in the end to present the total cost for the whole infrastructure. "
    generated_text = call_claude_sonnet(prompt + prompt_ending)
    return generated_text
