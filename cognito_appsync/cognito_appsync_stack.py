import os
from aws_cdk import (
    core,
    aws_appsync as appsync,
    aws_dynamodb as dynamodb,
    aws_cognito as cognito,
    aws_iam as iam,
)


class CognitoAppsyncStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        pool = cognito.UserPool(
            scope=self,
            id="user-pool",
            mfa=cognito.Mfa.OPTIONAL,
            mfa_second_factor=cognito.MfaSecondFactor(otp=True, sms=True),
            password_policy=cognito.PasswordPolicy(
                min_length=12,
                require_lowercase=True,
                require_uppercase=False,
                require_digits=False,
                require_symbols=False,
            )
        )

        client = pool.add_client(
            id="customer-app-client",
            auth_flows=cognito.AuthFlow(
                user_password=True,
                refresh_token=True,
                user_srp=True,
            ),
        )

        graphql_api = appsync.GraphqlApi(
            scope=self,
            id="graphql-api",
            name="todo-api",
            schema=appsync.Schema.from_asset(
                file_path=os.path.join("graphQL", "schema.graphql")),
            authorization_config=appsync.AuthorizationConfig(
                default_authorization=appsync.AuthorizationMode(
                    authorization_type=appsync.AuthorizationType.USER_POOL,
                    user_pool_config=appsync.UserPoolConfig(
                        user_pool=pool,
                    )
                )
            ),
            xray_enabled=True
        )

        todo_table = dynamodb.Table(
            scope=self,
            id="todo-table",
            removal_policy=core.RemovalPolicy.DESTROY,
            partition_key=dynamodb.Attribute(
                name="id",
                type=dynamodb.AttributeType.STRING
            ),
        )
        commnet_table = dynamodb.Table(
            scope=self,
            id="comment-table",
            removal_policy=core.RemovalPolicy.DESTROY,
            partition_key=dynamodb.Attribute(
                name="commentid",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="todoid",
                type=dynamodb.AttributeType.STRING
            ),
        )
        commnet_table.add_global_secondary_index(
            partition_key=dynamodb.Attribute(
                name="todoid",
                type=dynamodb.AttributeType.STRING
            ),
            index_name="todoid-index"
        )

        todo_dS = graphql_api.add_dynamo_db_data_source(
            id="todoDS",
            table=todo_table,
        )

        todo_dS.create_resolver(
            type_name="Query",
            field_name="getTodos",
            request_mapping_template=appsync.MappingTemplate.from_file(
                os.path.join("graphQL", "getItemsRequest.vtl")),
            response_mapping_template=appsync.MappingTemplate.from_file(
                os.path.join("graphQL", "getItemsResponse.vtl")),
        )

        todo_dS.create_resolver(
            type_name="Mutation",
            field_name="addTodo",
            request_mapping_template=appsync.MappingTemplate.from_file(
                os.path.join("graphQL", "addTodoRequest.vtl")),
            response_mapping_template=appsync.MappingTemplate.from_file(
                os.path.join("graphQL", "addTodoResponse.vtl")),
        )

        comment_dS = graphql_api.add_dynamo_db_data_source(
            id="commentDS",
            table=commnet_table,
        )

        comment_dS.create_resolver(
            type_name="Todo",
            field_name="contents",
            request_mapping_template=appsync.MappingTemplate.from_file(
                os.path.join("graphQL", "getCommentsRequest.vtl")),
            response_mapping_template=appsync.MappingTemplate.from_file(
                os.path.join("graphQL", "getCommentsResponse.vtl")),
        )

        comment_dS.create_resolver(
            type_name="Mutation",
            field_name="addComment",
            request_mapping_template=appsync.MappingTemplate.from_file(
                os.path.join("graphQL", "addCommentRequest.vtl")),
            response_mapping_template=appsync.MappingTemplate.from_file(
                os.path.join("graphQL", "addCommentResponse.vtl")),
        )
