# required credentials: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION
# AWS_DEFAULT_REGION should be eu-central-1
# if hosted on AWS: create new credentials as stated in the AWS console (IAM > User > Username > Create access key)

table_name = "ChatHistory"

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv(override=True)
    import boto3

    """
    Setup to create the table for the chat history, only run once
    """

    dynamodb = boto3.resource("dynamodb")

    existing_tables = boto3.client("dynamodb").list_tables()["TableNames"]

    if table_name not in existing_tables:
        table = dynamodb.create_table(
            TableName=table_name,
            # KeySchema:
            # defines primary key, AttributeName: name,
            # KeyType: indicates the partition key, partition key is used to uniquely identify each item in the table
            KeySchema=[{"AttributeName": "UserId", "KeyType": "HASH"},
                       {"AttributeName": "SessionId", "KeyType": "RANGE"}
            ],
            # AttributeDefinitions:
            # defines the data types of the key attributes in KeySchema
            # AttributeType (S, N, B): String, Number or Binary
            AttributeDefinitions=[{"AttributeName": "UserId", "AttributeType": "N"},
                                  {"AttributeName": "SessionId", "AttributeType": "S"}
            ],
            BillingMode="PAY_PER_REQUEST",
        )

        # wait until the table exists
        table.meta.client.get_waiter("table_exists").wait(TableName="SessionTable")