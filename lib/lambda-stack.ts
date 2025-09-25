import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import { lambdaConfig } from '../config/lambda-config';

import * as apigatewayv2 from 'aws-cdk-lib/aws-apigatewayv2';
import * as integrations from 'aws-cdk-lib/aws-apigatewayv2-integrations';
import * as events from "aws-cdk-lib/aws-events";
import * as targets from "aws-cdk-lib/aws-events-targets";

interface LambdaStackProps extends cdk.StackProps {
  table: dynamodb.Table;
  httpAPI: apigatewayv2.HttpApi;
}

// receives referene to DB and API gateway from parent stack
// generates lambda functions from config and assigns api route to each function
export class LambdaStack extends cdk.Stack {
  public readonly lambdas: Record<string, lambda.Function> = {};

  constructor(scope: Construct, id: string, props: LambdaStackProps) {
    super(scope, id, props);

    this.loadLambdasFromConfig(props.table, props.httpAPI);

    // add daily job for untagged count repair
    new events.Rule(this, 'DailyUntaggedCountRepairJob', {
      schedule: events.Schedule.cron({
        minute: '0',
        hour: '10'
      }),
      targets: [new targets.LambdaFunction(this.lambdas['updateUntaggedCount'])],
    });
  }

  private loadLambdasFromConfig(table: dynamodb.Table, httpAPI: apigatewayv2.HttpApi) {
    for (const configVal of lambdaConfig) {
      // create lambda function from file specified in config
      const perms = configVal.perms
      const name = configVal.name
      const lambdaFn = new lambda.Function(this, name, {
        runtime: lambda.Runtime.PYTHON_3_13,
        handler: `${name}.lambda_handler`,
        code: lambda.Code.fromAsset(`lib/lambda/${name}`),
        environment: {
          TABLE_NAME: table.tableName,
        },
      });
      this.lambdas[name] = lambdaFn;
      
      // grant perms for lambda to access DynamoDB
      if (perms === 'READ') {
        table.grantReadData(lambdaFn);
      }
      if (perms === 'WRITE') {
        table.grantWriteData(lambdaFn);
      }
      if (perms === 'READWRITE') {
        table.grantReadWriteData(lambdaFn);
      }

      // add route for lambda if method is defined
      // if method is undefined, the lambda will not be able to be called publicly by the api
      if (configVal.method === undefined) {
        continue;
      }
      httpAPI.addRoutes({
        path: `/${name}`,
        methods: [configVal.method],
        integration: new integrations.HttpLambdaIntegration(
          `${name}Integration`, lambdaFn
        )
      });
    }
  }
}
