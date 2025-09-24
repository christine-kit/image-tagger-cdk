#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import { ImageTaggerAppStack } from '../lib/image-tagger-app-stack';
import { FrontendStack } from '../lib/frontend-stack';
import { stageConfig } from '../config/config'

const app = new cdk.App();

for (const stageData of stageConfig) {
  new ImageTaggerAppStack(app, `ImageTaggerAppStack-${stageData.stage}`, {
    stage: stageData.stage,
    env: {
      account: stageData.account,
      region: stageData.region,
    },
  });

  if (!stageData.frontend) {
    continue;
  }
  new FrontendStack(app, `ImageTaggerFrontendStack-${stageData.stage}`, {
    stage: stageData.stage,
    env: {
      account: stageData.account,
      region: stageData.region,
    },
    domain: stageData.domain,
    certARN: stageData.certARN,
  });
}
