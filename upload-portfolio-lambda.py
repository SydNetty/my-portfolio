import boto3
from botocore.client import Config
import io
from io import StringIO
import zipfile

def lambda_handler(event, context):
    sns = boto3.resource('sns')
    topic = sns.Topic('arn:aws:sns:us-east-1:832945555593:deployPortfolioTopic')


    location = {
        "bucketName":'portfoliobuild.sydneynettesheim.com',
        "objectKey": 'portfoliobuild.zip'
    }

    try:
        job = event.get("CodePipeline.job")

        if job:
            for artifact in job["data"]["inputArtifacts"]:
                if artifact["name"] == "BuildArtifact":
                    location = artifact["location"]["s3Location"]

        s3 = boto3.resource('s3')

        portfolio_bucket = s3.Bucket('portfolio.sydneynettesheim.com')
        build_bucket = s3.Bucket(location["bucketName"])

        portfolio_zip = io.BytesIO()
        build_bucket.download_fileobj(location["objectKey"], portfolio_zip)

        with zipfile.ZipFile(portfolio_zip) as myzip:
            for nm in myzip.namelist():
                obj = myzip.open(nm)
                portfolio_bucket.upload_fileobj(obj, nm)
                portfolio_bucket.Object(nm).Acl().put(ACL='public-read')

        topic.publish(Subject="Portfolio deploy", Message="Portfolio deployed successfully!")
        if job:
            codepipeline = boto3.client('codepipeline')
            codepipeline.put_job_success_result(jobId=job["id"])
    except:
        topic.publish(Subject="Portfolio Deply Failed", Message="The Portfolio was not deployed successfully")
        raise

    return 'Hello from Lambda'