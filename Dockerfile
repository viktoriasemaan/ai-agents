FROM amazon/aws-lambda-python:3.11

# Install deps
COPY requirements.txt ${LAMBDA_TASK_ROOT}

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install -U boto3 botocore

# Copy function code
COPY index.py ${LAMBDA_TASK_ROOT}
COPY tools.py ${LAMBDA_TASK_ROOT}
COPY local_index ${LAMBDA_TASK_ROOT}/local_index

# Set the CMD to your handler
CMD [ "index.handler" ]