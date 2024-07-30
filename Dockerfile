# Use a multi-stage build to extract the infracost binary
FROM infracost/infracost:ci-latest AS infracost

# Use the amazon/aws-lambda-python:3.11 as the base image
FROM amazon/aws-lambda-python:3.11

# Install the tar package (assuming it's not already installed), and clean up to reduce image size
RUN yum install -y tar && \
    yum clean all && \
    rm -rf /var/cache/yum

# Create a directory for the infracost binary
RUN mkdir /app

# Copy the infracost binary from the infracost image to the current image
COPY --from=infracost /usr/bin/infracost /app/

# Set the PATH environment variable to include the directory containing the infracost binary
ENV PATH="/app:${PATH}"

# Copy the requirements file and function code
COPY requirements.txt ${LAMBDA_TASK_ROOT}
COPY index.py ${LAMBDA_TASK_ROOT}
COPY tools.py ${LAMBDA_TASK_ROOT}

# Upgrade pip and install required Python packages in a single RUN command
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -U boto3 botocore

# Set the CMD to the Lambda handler
CMD [ "index.handler" ]
