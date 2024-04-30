knowledge_base_id="EFSEVHIJBA"

import json
import os
import subprocess
import boto3
from datetime import datetime


bedrock_runtime = boto3.client('bedrock-runtime', 'us-west-2')
bedrock_agent_runtime = boto3.client('bedrock-agent-runtime','us-west-2')






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
    You are an AWS Solutions Architect and your responsibility is to answer user questions based on provided context
    
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
    prompt_ending = "Act as a DevOps Engineer. Carefully analyze the customer requirements provided and identify all AWS services and integrations needed for the solution. Generate the Terraform code required to provision and configure each AWS service, writing the code step-by-step. Provide only the final Terraform code, without any additional comments, explanations, markdown formatting, or special symbols. The key changes are: - Specify to only provide the final Terraform code at the end, no intermediate steps. - Explicitly state not to include any comments, explanations, markdown, or special symbols in the code.  - Remove the open-ended statements like 'take your time', 'do your best' and 'dont apologize' to keep the prompt focused."
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

def iac_estimate_tool(prompt):
    """
    Estimate the cost of an AWS infrastructure using Infracost.
    """
    prompt_ending = "Given the estimated costs for an AWS cloud infrastructure, provide a breakdown of the monthly cost for each service. For services with multiple line items (e.g. RDS), aggregate the costs into a single total for that service. Present the cost analysis as a list, with each service and its corresponding monthly cost. Finally, include the total monthly cost for the entire infrastructure. The key optimizations:	- Clarify that the input is estimated costs, not raw infrastructure details. -	Simplify language around handling multiple line items for a service. -	Specify the desired list format for the output.  - Reduce repetition and remove unnecessary instructions (e.g. 'you do not need to give all calculations'). - Double-check all mathematical calculations to ensure accuracy. - Verify that the sum of individual service costs equals the reported total cost."
    
    # Get terraform code from S3
    s3 = boto3.client('s3')
    bucket_name = "bedrock-agent-generate-iac-estimate-cost"
    prefix_code = "iac-code"
    prefix_cost = "iac-cost"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"iac_cost_{timestamp}.tf"
    local_dir = '/tmp/infracost-evaluate'
    
    # Create the local directory if it doesn't exist
    os.makedirs(local_dir, exist_ok=True)

    # List objects in the S3 folder sorted by LastModified in descending order
    objects = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix_code)
    sorted_objects = sorted(objects['Contents'], key=lambda obj: obj['LastModified'], reverse=True)
    
    # Get the latest file key
    latest_file_key = sorted_objects[0]['Key']
    
    # Download the latest file
    local_file_path = os.path.join(local_dir, os.path.basename(latest_file_key))
    s3.download_file(bucket_name, latest_file_key, local_file_path)
    
    # Generate timestamp-based file name
    cost_filename = f"cost-evaluation-{timestamp}.txt"
    cost_file_path = f"/tmp/{cost_filename}"
    
    # Run Infracost CLI command
    infracost_cmd = f"infracost breakdown --path /tmp/infracost-evaluate > {cost_file_path}"
    try:
        subprocess.run(infracost_cmd, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        # Read the result file even if the command returns a non-zero exit code
        with open(cost_file_path, 'r') as f:
            cost_file = f.read()
        print(f"Infracost command returned non-zero exit code: {e.returncode}")
        print(f"Result: {cost_file}")
    else:
        with open(cost_file_path, 'r') as f:
            cost_file = f.read()
        print(f"Result: {cost_file}")
    
    # Upload cost evaluation file to S3 under the "iac-cost" folder
    s3_cost_result = os.path.join(prefix_cost, cost_filename)
    s3.upload_file(cost_file_path, bucket_name, s3_cost_result)
    
    generated_text = call_claude_sonnet(cost_file + prompt + prompt_ending)
    return generated_text