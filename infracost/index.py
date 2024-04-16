import tools


def handler(event, context):
    # Print the received event to the logs
    print("Received event: ")
    print(event)

    # Initialize response code to None
    response_code = None

    # Extract the action group, api path, and parameters from the prediction
    action = event["actionGroup"]
    api_path = event["apiPath"]
    parameters = event["parameters"]
    inputText = event["inputText"]
    httpMethod = event["httpMethod"]

    print(f"inputText: {inputText}")

    # Get the query value from the parameters
    query = parameters[0]["value"]
    print(f"Query: {query}")

    # Check the api path to determine which tool function to call
    if api_path == "/query_well_arch_framework":
        # Call the aws_well_arch_tool from the tools module with the query
        body = tools.aws_well_arch_tool(query)
        # Create a response body with the result
        response_body = {"application/json": {"body": str(body)}}
        response_code = 200
    elif api_path == "/gen_code":
        # Call the code_gen_tool from the tools module with the query
        body = tools.code_gen_tool(query)
        # Create a response body with the result
        response_body = {"application/json": {"body": str(body)}}
        response_code = 200
    else:
        # If the api path is not recognized, return an error message
        body = {"{}::{} is not a valid api, try another one.".format(action, api_path)}
        response_code = 400
        response_body = {"application/json": {"body": str(body)}}

    # Print the response body to the logs
    print(f"Response body: {response_body}")

    # Create a dictionary containing the response details
    action_response = {
        "actionGroup": action,
        "apiPath": api_path,
        "httpMethod": httpMethod,
        "httpStatusCode": response_code,
        "responseBody": response_body,
    }

    # Return the list of responses as a dictionary
    api_response = {"messageVersion": "1.0", "response": action_response}

    return api_response
