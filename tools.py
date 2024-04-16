import json
import boto3
from datetime import datetime





bedrock_runtime = boto3.client('bedrock-runtime', 'us-west-2')
bedrock_agent_runtime = boto3.client('bedrock-agent-runtime','us-west-2')


knowledge_base_id="JLSE7CCLNC"



def get_contexts(query, kbId, numberOfResults=5):
    """
    This function takes a query, knowledge base id, and number of results as input, and returns the contexts for the query.
    :param query: This is the natural language query that is passed in through the app.py file.
    :param kbId: This is the knowledge base id that is gathered from the .env file.
    :param numberOfResults: This is the number of results that are returned from the knowledge base.
    :return: The contexts for the query.
    """
    # getting the contexts for the query from the knowledge base
    results = bedrock_agent_runtime.retrieve(
        retrievalQuery= {
            'text': query
        },
        knowledgeBaseId=kbId,
        retrievalConfiguration= {
            'vectorSearchConfiguration': {
                'numberOfResults': numberOfResults
            }
        }
    )
    #  creating a list to store the contexts
    contexts = []
    #   adding the contexts to the list
    for retrievedResult in results['retrievalResults']: 
        contexts.append(retrievedResult['content']['text'])
    #  returning the contexts
    return contexts


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


def answer_query(user_input):
    """
    This function takes the user question, queries Amazon Bedrock KnowledgeBases for that question,
    and gets context for the question.
    Once it has the context, it calls the LLM for the response
    :param user_input: This is the natural language question that is passed in through the app.py file.
    :return: The answer to your question from the LLM based on the context from the Knowledge Bases.
    """
    # Setting primary variables, of the user input
    userQuery = user_input
    # getting the contexts for the user input from Bedrock knowledge bases
    userContexts = get_contexts(userQuery, knowledge_base_id)

    # Configuring the Prompt for the LLM
    # TODO: EDIT THIS PROMPT TO OPTIMIZE FOR YOUR USE CASE
    prompt_data = """
    You are a Question and answering assistant and your responsibility is to answer user questions based on provided context
    
    Here is the context to reference:
    <context>
    {context_str}
    </context>

    Referencing the context, answer the user question
    <question>
    {query_str}
    </question>
    """

    # formatting the prompt template to add context and user query
    formatted_prompt_data = prompt_data.format(context_str=userContexts, query_str=userQuery)

    # Configuring the model parameters, preparing for inference
    # TODO: TUNE THESE PARAMETERS TO OPTIMIZE FOR YOUR USE CASE
    prompt = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 4096,
        "temperature": 0.5,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": formatted_prompt_data
                    }
                ]
            }
        ]
    }
    
    # formatting the prompt as a json string
    json_prompt = json.dumps(prompt)    

    # invoking Claude3, passing in our prompt
    response = bedrock_runtime.invoke_model(body=json_prompt, modelId="anthropic.claude-3-sonnet-20240229-v1:0",
                                    accept="application/json", contentType="application/json")
    # getting the response from Claude3 and parsing it to return to the end user
    response_body = json.loads(response.get('body').read())
    # the final string returned to the end user
    answer = response_body['content'][0]['text']
    # returning the final string to the end user
    return answer


def iac_gen_tool(prompt):
    """
    Use this tool only when you need to generate Infrastructure such as Terraform, CloudFormation scripts based on a customer's request.
    The input is the customer's question. The tool returns Terraform code that the customer can use.
    """
    prompt_ending = "Act as you as DevOps Engineer. Carefully analyze customer requirements, identify all AWS services used and integration required for a solution. For each service generate Terraform code, take your time and write Terraform script step-by-step. Do your best and don't apologize. Provide code only, no text."
    generated_text = call_claude_sonnet(prompt + prompt_ending)
    
    # Save to S3
    s3 = boto3.client('s3')
    bucket_name = "bedrock-agent-generate-iac-estimate-cost"
    prefix = "iac-code/"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"iac_{timestamp}.tf"
    s3_path = f"{prefix}{filename}"
    
    # Write the Terraform code to a stringio object and upload it to S3
    from io import BytesIO
    file_buffer = BytesIO(generated_text.encode('utf-8'))
    s3.upload_fileobj(file_buffer, bucket_name, s3_path)
    
    return f"File saved to S3 bucket {bucket_name} at {s3_path}"


