import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as apigatewayv2 from 'aws-cdk-lib/aws-apigatewayv2';

import { LambdaStack } from './lambda-stack';
import { ImageTaggerDBStack} from '../lib/image-tagger-db-stack';

export class ImageTaggerAppStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: cdk.StackProps) {
    super(scope, id, props);
    const dbStack = new ImageTaggerDBStack(this, 'ImageTaggerDBStack', {
      env: props.env,
    })
    const httpAPI = new apigatewayv2.HttpApi(this, 'ImageTaggerAPI', {
      apiName: "ImageTaggerAPI",
      createDefaultStage: true,
    });

    new LambdaStack(this, 'ImageTaggerLambdaStack', {
      table: dbStack.table,
         env: props.env,
         httpAPI: httpAPI,
    })
  }
}
