# Use a multi-stage build to extract the infracost binary
FROM infracost/infracost:ci-latest AS infracost

# Use the amazon/aws-lambda-python:3.11 as the base image
FROM amazon/aws-lambda-python:3.11

# Install tar package (assuming it's not already installed)
RUN yum install -y tar

# Create a directory for the infracost binary
RUN mkdir /app

# Copy the infracost binary from the infracost image to the current image
COPY --from=infracost /usr/bin/infracost /app/

# Set the PATH environment variable to include the directory containing the infracost binary
ENV PATH="/app:${PATH}"

# Install dependencies
COPY requirements.txt ${LAMBDA_TASK_ROOT}

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -U boto3 botocore

# Set the API key as an environment variable
ENV INFRACOST_API_KEY=YOURKEY

# Copy function code
COPY infracost.py ${LAMBDA_TASK_ROOT}

# Adjust file permissions
RUN chmod -R 777 ${LAMBDA_TASK_ROOT} && \
    chmod 755 ${LAMBDA_TASK_ROOT}/infracost.py

# Set the CMD to your handler
CMD [ "infracost.lambda_handler" ]