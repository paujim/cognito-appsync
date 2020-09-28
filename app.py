#!/usr/bin/env python3

from aws_cdk import core

from cognito_appsync.cognito_appsync_stack import CognitoAppsyncStack


app = core.App()
CognitoAppsyncStack(app, "cognito-appsync")

app.synth()
