import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as apigatewayv2 from 'aws-cdk-lib/aws-apigatewayv2';

import { LambdaStack } from './lambda-stack';
import { ImageTaggerDBStack} from '../lib/image-tagger-db-stack';

interface AppStackProps extends cdk.StackProps {
    stage: string;
}

export class ImageTaggerAppStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: AppStackProps) {
    super(scope, id, props);
    const dbStack = new ImageTaggerDBStack(this, 'ImageTaggerDBStack', {
      env: props.env,
    })
    const httpAPI = new apigatewayv2.HttpApi(this, `ImageTaggerAPI-${props.stage}`, {
      apiName: `ImageTaggerAPI-${props.stage}`,
      createDefaultStage: true,
    });

    new cdk.CfnOutput(this, `${id} API endpoint`, {
      value: httpAPI.apiEndpoint,
    });

    new LambdaStack(this, 'ImageTaggerLambdaStack', {
      table: dbStack.table,
         env: props.env,
         httpAPI: httpAPI,
    })
  }
}
