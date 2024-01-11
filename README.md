# Amazon Bedrock Agents Quickstart

Welcome to our hands-on workshop on building Generative AI Agents using Amazon Bedrock Agents. In this interactive session, you will learn how to harness the power of AI agents and tools to build an AI-powered AWS Solution Architect dubbed "Agent AWS".

![Agent Helpful Example](/images/agent_helps.png)

Over the course of this workshop, participants will construct a Bedrock Agent that can assist with querying the AWS Well-Architected Framework and generating code.

By the end of this workshop, you will have gained valuable hands-on experience in building agents.

![Agent Architecture Diagram](/images/agent_arch.png)

This is a 300-level workshop, so some familiarly with Python and using services such as Lambda and Elastic Container Registry is helpful. No AI/ML experience is necessary. This workshop is intended to be finished within 2 hours.

## Prerequisites

This workshop assumes you are working in an environment with access to [Python 3.9](https://www.python.org/getit/) or later and [Docker](https://www.docker.com/). 

## Setting up your local Environment

1. **Clone the Repository:** Start by cloning the provided repository which contains the code for our agent.

```bash
git clone https://github.com/build-on-aws/amazon-bedrock-agents-quickstart.git
cd amazon-bedrock-agents-quickstart
```

2. **Install Dependencies:** Run the appropriate pip install command to download necessary packages.

``` bash
pip install -r requirements.txt
```

3. **(Optional) Enable Amazon CodeWhisperer:** Activate Amazon's CodeWhisperer, your AI assistant that will guide you through coding. Watch this video to learn how to install it in your environment.

[![Amazon CodeWhisperer](https://img.youtube.com/vi/sFh3_cMUrMk/0.jpg)](https://www.youtube.com/watch?v=sFh3_cMUrMk)

## Create the IAM roles

1. In your console, go to your [IAM Dashboard](https://us-east-1.console.aws.amazon.com/iam/).
2. Go to Policies in the right-hand side menu.
3. Create one policie named for example Bedrock-InvokeModel-Policy
   ```json
   {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": "bedrock:InvokeModel",
            "Resource": [
                "arn:aws:bedrock:*::foundation-model/*"
                ]
            }
        ]
    }
   ```
  4. Create one policie named for example Bedrock-S3-GetObject
    ```json
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "VisualEditor0",
                "Effect": "Allow",
                "Action": "s3:GetObject",
                "Resource": "arn:aws:s3:::bedrockreinvent/agent_aws_openapi.json"
            }
        ]
    }
    ```
  5. 



## Building an Agent

To get started with the agent, open the Bedrock console, select Agents in the left navigation panel, then choose Create Agent.

![Agent Start](/images/agents-for-amazon-bedrock-1.png)

This starts the agent creation workflow.

1. Provide agent details including agent name, description, whether the agent is allowed to request additional user inputs, and choose the IAM role created earlier.

Here is what I used for this Agent
```
Agent-AWS

Agent AWS is an automated, AI-powered agent that helps customers with knowledge of AWS by querying the AWS Well-Architected Framework and writing code.
```

![Agent Start](/images/agent_details.png)

2. Select a foundation model from Bedrock that fits your use case. Here, you provide an instruction to your agent in natural language. The instruction tells the agent what task it’s supposed to perform and the persona it’s supposed to assume. For example, “You are an expert AWS Certified Solutions Architect. Your role is to help customers understand best practices on building on AWS.”

![Agent Model](/images/agent_model.png)

3. Skip the Add Action Groups and create an Agent. 

![Agent Model](/images/agent_create.png)

4. Now you can test your agent, but you won’t find it very helpful at the moment if you ask it AWS related questions such as "How can I design secure VPCs?"

![Agent Model](/images/agent_not_working.png)

This is where we have to develop "tools" for the agent which are orchestrated through the action groups.

## Building Agent Tools

Tools are self-contained functions designed to perform a specific task. In `tools.py` we have two functions we are going to provide to our agent `aws_well_arch_tool` and `code_gen_tool`.

### Querying the AWS Well-Architected Framework

The code for this tool uses [Langchain](https://python.langchain.com/docs/get_started/introduction.html) a popular framework for developing applications powered by large language models. Langchain provides an interface to use Bedrock Embeddings with a [local vector database](https://github.com/facebookresearch/faiss) to retrieve documents relevant to a user's query. Using the documents, we can then send a request to the Titan model using Bedrock to get a response back with relevant context. this is known as [Retrieval Augmented Generation (RAG)](https://docs.aws.amazon.com/sagemaker/latest/dg/jumpstart-foundation-models-customize-rag.html).

To learn more about how the data was collected and embeddings read this [blog post](https://community.aws/posts/well-arch-chatbot#data-collection)

The code used to collect the data is in `ingest.py`

### Code Generation Tool
The code for this tool, uses a call to the Claude-V2 model to generate code based on a user's request.

### Testing tools

To test the tools, you can run

```bash
python test_tools.py
```

You should get output similar to this

```
 AWS provides a set of best practices for designing secure VPCs. These best practices include creating network layers, controlling traffic at all layers, automating network protection, implementing inspection and protection, and considering whether resources need to be in public subnets.
 Here is some documentation for more details: 
https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/protecting-networks.html
https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/sec_network_protection_create_layers.html
https://docs.aws.amazon.com/wellarchitected/latest/framework/sec_network_protection_create_layers.html
https://docs.aws.amazon.com/wellarchitected/latest/framework/sec_network_protection_create_layers.html
```

```python
import boto3

def upload_file_to_s3(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket
    
    Args:
        file_name (str): File to upload
        bucket (str): Bucket to upload to
        object_name (str): S3 object name. If not specified then file_name is used
    """
    
    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name

    # Upload the file    
    s3_client = boto3.client('s3')
    s3_client.upload_file(file_name, bucket, object_name)
...    
```
Feel free to play around with the prompts by editing `test_tools.py`

## Building the Lambda Function

For our Agent to use our tools, we must encapsulate the logic into a lambda function. `index.py` has the logic to parse a request from the agent, and then pick the correct tool to use. The function will then format the response and send it back to the agent.

### Push Docker Image to ECR

We will package this Lambda function as a container, so create a new ECR following these [instructions](https://docs.aws.amazon.com/AmazonECR/latest/userguide/repository-create.html). I called mine `bedrock_sa_tools`

![ECR Repo](/images/ecr_repo.png)

Once the repo is created, follow the instructions in the `View push commands` button to upload the Docker Image to ECR.

### Create the Lambda Function

1. Navigate to the [Lambda Console](https://us-east-1.console.aws.amazon.com/lambda/home?region=us-east-1#/functions) and click on `Create function` button.

2. Chose Container image then provide the `Function name` (berdock_sa_tools) and for the `Container image URI` select the container you uploaded.

3. Click on Create function button in the bottom of the page 

### Update Lambda Permissions

1. Once the function is created, click on the Configuration Tab in the same page and `Choose Permissions` from the left side panel

2. Click on Add permissions button in Resource-based policy statement section to provide the permission to invoke lambda functions from bedrock

![Lambda Permissions](/images/lambda_perms.png)

3. Provide Statement Id as `agent` , Principal as `bedrock.amazonaws.com` and Action as `lambda:InvokeFunction`. Click Save after adding all the above three information.

![Lambda Permissions](/images/lambda_perms_2.png)

4. Add the following Policy Statement to your Execution role, so Lambda can call Bedrock. (Details [here](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_manage-attach-detach.html#add-policies-console))
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": "bedrock:InvokeModel",
            "Resource": "*"
        }
    ]
}
```

### Testing Lambda Function

To test your Lambda function:

1. Click on the "Test" tab near the top of the page.

2. Configure a test event that matches how the Agent will send a request:

```
{
  "agent": {
    "alias": "TSTALIASID",
    "name": "Agent-AWS",
    "version": "DRAFT",
    "id": "KQI6ICMKZZ"
  },
  "sessionId": "975786472213626",
  "httpMethod": "GET",
  "sessionAttributes": {},
  "inputText": "How can I create secure VPCs?",
  "promptSessionAttributes": {},
  "apiPath": "/query_well_arch_framework",
  "messageVersion": "1.0",
  "actionGroup": "agent_action_group",
  "parameters": [
    {
      "name": "query",
      "type": "string",
      "value": "How can I create secure VPCs?"
    }
  ]
}
```

3. Click on "Test" to execute the Lambda function. You should see the results of the function invocation, which will be a response from the Titan Model.

![Lambda Results](/images/lambda_results.png)

## Upload OpenAPI Spec

The [OpenAPI Specification (OAS)](https://swagger.io/specification/) defines a standard, language-agnostic interface to HTTP APIs which allows both humans and computers to discover and understand the capabilities of the service without access to source code.

Our agent will be able to understand what tool to use based on the request given to the user and then call the correct endpoint due to the OpenAPI spec.

You will need to upload the `agent_aws_openapi.json` [file to an S3 bucket](https://docs.aws.amazon.com/AmazonS3/latest/userguide/upload-objects.html).

## Create Action Group

An action is a task that the agent can perform automatically by making API calls to your company systems. A set of actions is defined in an action group. The OpenAPI schema defines the API for all the actions in the group. The agent will invoke our Lambda function based on request, that will invoke the tools we built.

1. To begin go to the Agents List Page and search for the Agent created earlier and click the Agent Name to load the agent details.

2. Click on the `Working draft` link to go into the Agent and add the agent action.

3. Click on the `Add` button in Action groups section to create a new Action Group for the agent.

4. Provide the Action Group Name and Description (Optional). Choose the Lambda function and the S3 object for the API spec uploaded earlier.

![Action Group](/images/action_group.png)

5. Click on `Save and exit` button in the right bottom of the page.

6. Once the Agent Status is in `Ready` state in Agent home page. You can start the testing.

## Play Time

Now the agent will be much more helpful than it was prior to adding an action group

![Action Group](/images/working_agent.png)

Try out some different prompts, and test the limits of the agent. Happy building!


## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.

