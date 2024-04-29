import os
import subprocess
import boto3
from datetime import datetime

def lambda_handler(event, context):
    # Download file from S3
    s3 = boto3.client('s3')
    bucket_name = 'vedmich-2024-04-16'
    evaluate_folder_name = 'iac-code'
    local_dir = '/tmp/infracost-evaluate'
    # iac-cost
    # Create the local directory if it doesn't exist
    os.makedirs(local_dir, exist_ok=True)
    
    
    ## get latest created file - last modied. 
    
    # List objects in the S3 folder
    objects = s3.list_objects_v2(Bucket=bucket_name, Prefix=evaluate_folder_name)
    
    # Download each file in the folder
    for obj in objects['Contents']:
        file_key = obj['Key']
        if not file_key.endswith('/'):  # Skip folders
            local_file_path = os.path.join(local_dir, os.path.basename(file_key))
            s3.download_file(bucket_name, file_key, local_file_path)


    # Run Infracost CLI command
    infracost_cmd = f"infracost breakdown --path /tmp/infracost-evaluate > /tmp/result.txt"
    try:
        subprocess.run(infracost_cmd, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        # Read the result file even if the command returns a non-zero exit code
        with open('/tmp/result.txt', 'r') as f:
            result = f.read()
        print(f"Infracost command returned non-zero exit code: {e.returncode}")
        print(f"Result: {result}")
    else:
        with open('/tmp/result.txt', 'r') as f:
            result = f.read()
        print(f"Result: {result}")

    # Generate timestamp-based file name
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    result_file_name = f"cost-evaluation-{timestamp}.txt"
    
    # Upload result file to S3 under the "cost-result" folder
    result_bucket = 'vedmich-2024-04-16'
    result_folder = 'cost-result'
    s3_result_key = os.path.join(result_folder, result_file_name)
    s3.upload_file('/tmp/result.txt', result_bucket, s3_result_key)


    return {
        'statusCode': 200,
        'body': 'Infracost result uploaded to S3'
    }