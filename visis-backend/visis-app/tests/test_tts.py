import boto3

polly_client = boto3.client('polly')
methods = dir(polly_client)
print(methods)