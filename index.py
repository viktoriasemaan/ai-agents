import tools

def handler(event, context):
    """
    Lambda function handler to process API requests and route them to the appropriate tool functions.

    Args:
        event (dict): The event data containing API request details.
        context (object): The context object providing runtime information.

    Returns:
        dict: The response dictionary containing the API response details.
    """
    # Print the received event to the logs
    print("Received event: ", event)

    # Initialize response code to None
    response_code = None

    # Extract the action group, API path, and parameters from the event
    action = event["actionGroup"]
    api_path = event["apiPath"]
    parameters = event["parameters"]
    input_text = event["inputText"]
    http_method = event["httpMethod"]

    print(f"Input Text: {input_text}")

    # Get the query value from the parameters
    query = parameters[0]["value"]
    print(f"Query: {query}")

    # Check the API path to determine which tool function to call
    if api_path == "/answer_query":
        # Call the answer_query function from the tools module with the query
        body = tools.answer_query(query)
        # Create a response body with the result
        response_body = {"application/json": {"body": str(body)}}
        response_code = 200
    elif api_path == "/iac_gen":
        # Call the iac_gen_tool function from the tools module with the query
        body = tools.iac_gen_tool(query)
        # Create a response body with the result
        response_body = {"application/json": {"body": str(body)}}
        response_code = 200
    elif api_path == "/iac_estimate_tool":
        # Call the iac_estimate_tool function from the tools module with the query
        body = tools.iac_estimate_tool(query)
        # Create a response body with the result
        response_body = {"application/json": {"body": str(body)}}
        response_code = 200
    else:
        # If the API path is not recognized, return an error message
        body = f"{action}::{api_path} is not a valid API, try another one."
        response_code = 400
        response_body = {"application/json": {"body": str(body)}}

    # Print the response body to the logs
    print(f"Response body: {response_body}")

    # Create a dictionary containing the response details
    action_response = {
        "actionGroup": action,
        "apiPath": api_path,
        "httpMethod": http_method,
        "httpStatusCode": response_code,
        "responseBody": response_body,
    }

    # Return the list of responses as a dictionary
    api_response = {"messageVersion": "1.0", "response": action_response}

    return api_response

# Example usage
if __name__ == "__main__":
    # Example event data
    event = {
        "actionGroup": "exampleGroup",
        "apiPath": "/answer_query",
        "parameters": [{"value": "exampleQuery"}],
        "inputText": "exampleInput",
        "httpMethod": "GET"
    }
    # Example context data
    context = {}

    # Call the handler function
    response = handler(event, context)

    # Print the response
    print(response)
