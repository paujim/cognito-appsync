#!/usr/bin/env python3

from aws_cdk import core

from apigateway_appsync.apigateway_appsync_stack import ApigatewayAppsyncStack


app = core.App()
ApigatewayAppsyncStack(app, "apigateway-appsync")

app.synth()
