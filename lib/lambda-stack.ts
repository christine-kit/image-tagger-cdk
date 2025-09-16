import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import { lambdaConfig } from '../config/lambda-config';

import * as apigatewayv2 from 'aws-cdk-lib/aws-apigatewayv2';
import * as integrations from 'aws-cdk-lib/aws-apigatewayv2-integrations';

interface LambdaStackProps extends cdk.StackProps {
  table: dynamodb.Table;
  httpAPI: apigatewayv2.HttpApi;
}

// receives referene to DB and API gateway from parent stack
// generates lambda functions from config and assigns api route to each function
export class LambdaStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: LambdaStackProps) {
    super(scope, id, props);

    for (const configVal of lambdaConfig) {
      // create lambda function from file specified in config
      const perms = configVal.perms
      const name = configVal.name
      const lambdaFn = new lambda.Function(this, name, {
        runtime: lambda.Runtime.PYTHON_3_13,
        handler: `${name}.lambda_handler`,
        code: lambda.Code.fromAsset(`lib/lambda/${name}`),
        environment: {
          TABLE_NAME: props.table.tableName,
        },
      });
      
      // grant perms for lambda to access DynamoDB
      if (perms === 'READ') {
        props.table.grantReadData(lambdaFn);
      }
      if (perms === 'WRITE') {
        props.table.grantWriteData(lambdaFn);
      }
      if (perms === 'READWRITE') {
        props.table.grantReadWriteData(lambdaFn);
      }

      props.httpAPI.addRoutes({
        path: `/${name}`,
        methods: [configVal.method],
        integration: new integrations.HttpLambdaIntegration(
          `${configVal.name}Integration`, lambdaFn
        )
      })
    }
  }
}
