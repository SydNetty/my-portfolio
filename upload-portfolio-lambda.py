import boto3
from botocore.client import Config
import io
from io import StringIO
import zipfile

def lambda_handler(event, context):
    sns = boto3.resource('sns')
    topic = sns.Topic('arn:aws:sns:us-east-1:832945555593:deployPortfolioTopic')

    try:
        s3 = boto3.resource('s3') # , config=Config(signature_version='s4v4'))

        portfolio_bucket = s3.Bucket('portfolio.sydneynettesheim.com')
        build_bucket = s3.Bucket('portfoliobuild.sydneynettesheim.com')

        portfolio_zip = io.BytesIO()
        build_bucket.download_fileobj('portfoliobuild.zip', portfolio_zip)

        with zipfile.ZipFile(portfolio_zip) as myzip:
            for nm in myzip.namelist():
                obj = myzip.open(nm)
                portfolio_bucket.upload_fileobj(obj, nm)
                portfolio_bucket.Object(nm).Acl().put(ACL='public-read')

        topic.publish(Subject="Portfolio deploy", Message="Portfolio deployed successfully!")
    except:
        topic.publish(Subject="Portfolio Deply Failed", Message="The Portfolio was not deployed successfully")
        raise

    return 'Hello from Lambda'