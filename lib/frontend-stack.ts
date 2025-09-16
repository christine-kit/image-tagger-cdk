import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as iam from "aws-cdk-lib/aws-iam";
import { frontendConfig } from '../config/config';
import * as cloudfront from "aws-cdk-lib/aws-cloudfront"
import * as origins from 'aws-cdk-lib/aws-cloudfront-origins'
import { Certificate } from 'aws-cdk-lib/aws-certificatemanager';
interface FrontendProps extends cdk.StackProps {
    stage: string;
    domain?: string;
    certARN?: string;
}
export class FrontendStack extends cdk.Stack {
    constructor(scope: Construct, id: string, props: FrontendProps) {
        super(scope, id, props);
        const bucketId = `imageTagger-frontend-${props.env?.account}-${props.stage}`;
        const siteBucket = new s3.Bucket(this, bucketId, {
            blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
            websiteIndexDocument: 'index.html',
            websiteErrorDocument: 'index.html',
            removalPolicy: cdk.RemovalPolicy.DESTROY, 
            autoDeleteObjects: true, // destroy and autodelete ok since this bucket only hosts frontend app
        });

        // OIDC provider for GitHub Actions
        const provider = new iam.OpenIdConnectProvider(this, 'GitHubProvider', {
            url: 'https://token.actions.githubusercontent.com',
            clientIds: ['sts.amazonaws.com'],
        });

        // IAM role for GitHub Actions
        const githubActionsRole = new iam.Role(this, 'GitHubActionsDeployRole', {
            assumedBy: new iam.WebIdentityPrincipal(
                provider.openIdConnectProviderArn,
                {
                StringLike: {
                    'token.actions.githubusercontent.com:sub': `repo:${frontendConfig.owner}/${frontendConfig.repo}:ref:refs/heads/main`,
                },
                }
            ),
            description: 'Role assumed by GitHub Actions for S3 deployment',
        });

        siteBucket.grantReadWrite(githubActionsRole);

        // put s3 behind cloudfront
        const oac = new cloudfront.S3OriginAccessControl(this, 'ImageTaggerFrontendOAC', {
            signing: cloudfront.Signing.SIGV4_ALWAYS
        });
        const s3Origin = origins.S3BucketOrigin.withOriginAccessControl(siteBucket, {
            originAccessControl: oac,
        });
        // route errors to index.html for vue SPA routing
        const errorResponses: cloudfront.ErrorResponse[] = [
            {
                httpStatus: 403,
                responseHttpStatus: 200,
                responsePagePath: '/index.html',
            },
            {
                httpStatus: 404,
                responseHttpStatus: 200,
                responsePagePath: '/index.html',
            },
        ];
        // if cert is defined in config, pass cert and custom domain to distribution.
        // otherwise create distribution without cert initially to bootstrap, then add cert + domain later
        const cert = props.certARN ? Certificate.fromCertificateArn(this, 'domainCert', props.certARN) : undefined;
        const distribution = new cloudfront.Distribution(this, 'ImageTaggerSiteDistribution', {
            defaultBehavior: {
                origin: s3Origin,
                viewerProtocolPolicy: cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
            },
            defaultRootObject: 'index.html',
            errorResponses: errorResponses,
            domainNames: props.domain ? [props.domain] : undefined,
            certificate: cert
        });
        // allow cloudfront to access bucket
        siteBucket.addToResourcePolicy(new iam.PolicyStatement({
            effect: iam.Effect.ALLOW,
            principals: [new iam.ServicePrincipal('cloudfront.amazonaws.com')],
            actions: ['s3:GetObject'],
            resources: [`${siteBucket.bucketArn}/*`],
            conditions: {
                StringEquals: {
                    "AWS:SourceArn": distribution.distributionArn,
                },
            },
        }));


        new cdk.CfnOutput(this, 'CloudFrontURL', {
            value: distribution.domainName,
        });

        new cdk.CfnOutput(this, 'GithubRoleArn', {
            value: githubActionsRole.roleArn,
        });
    }
}