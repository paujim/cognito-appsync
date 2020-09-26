import os
from aws_cdk import (
    core,
    aws_appsync as appsync,
    aws_dynamodb as dynamodb,
)


class ApigatewayAppsyncStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        api = appsync.GraphqlApi(
            scope=self,
            id="Api",
            name="demo",
            schema=appsync.Schema.from_asset(
                file_path=os.path.join("graphQL", "schema.graphql")),
            authorization_config=appsync.AuthorizationConfig(
                default_authorization=appsync.AuthorizationMode(
                    authorization_type=appsync.AuthorizationType.IAM
                )
            ),
            xray_enabled=True
        )

        demo_table = dynamodb.Table(
            scope=self,
            id="DemoTable",
            partition_key=dynamodb.Attribute(
                name="id",
                type=dynamodb.AttributeType.STRING
            )
        )

        demo_dS = api.add_dynamo_db_data_source(
            id="demoDataSource",
            table=demo_table,
        )

        # Resolver for the Query "getDemos" that scans the DyanmoDb table and returns the entire list.
        demo_dS.create_resolver(
            type_name="Query",
            field_name="getDemos",
            request_mapping_template=appsync.MappingTemplate.dynamo_db_scan_table(),
            response_mapping_template=appsync.MappingTemplate.dynamo_db_result_list()
        )

        # Resolver for the Mutation "addDemo" that puts the item into the DynamoDb table.
        demo_dS.create_resolver(
            type_name="Mutation",
            field_name="addDemo",
            request_mapping_template=appsync.MappingTemplate.dynamo_db_put_item(
                key=appsync.PrimaryKey.partition("id").auto(),
                values=appsync.Values.projecting("demo"),
            ),
            response_mapping_template=appsync.MappingTemplate.dynamo_db_result_item()
        )
