# Use a multi-stage build to extract the infracost binary
FROM infracost/infracost:ci-latest as infracost

# Use the amazon/aws-lambda-python:3.11 as the base image
FROM amazon/aws-lambda-python:3.11

# Install the tar package (assuming it's not already installed)
RUN yum install -y tar

# Create a directory for the infracost binary
RUN mkdir /app

# Copy the infracost binary from the infracost image to the current image
COPY --from=infracost /usr/bin/infracost /app/

# Set the PATH environment variable to include the directory containing the infracost binary
ENV PATH="/app:${PATH}"

# Copy the requirements file and install dependencies
COPY requirements.txt ${LAMBDA_TASK_ROOT}

# Upgrade pip and install required Python packages
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install -U boto3 botocore

# Copy the function code
COPY index.py ${LAMBDA_TASK_ROOT}
COPY tools.py ${LAMBDA_TASK_ROOT}

# Set the CMD to the Lambda handler
CMD [ "index.handler" ]
