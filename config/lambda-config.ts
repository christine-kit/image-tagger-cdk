import * as apigatewayv2 from 'aws-cdk-lib/aws-apigatewayv2';

export interface LambdaConfig {
    name: string;
    perms: string; // dynamodb permissions
    method?: apigatewayv2.HttpMethod;
}

// lambda-stack.ts will look for a python file in lib/lambda/functionName/functionName.py
export const lambdaConfig: LambdaConfig[] = [
    {
        name: "addNewImage",
        perms: "WRITE",
        method: apigatewayv2.HttpMethod.PUT,
    },
    {
        name: "addNewTag",
        perms: "WRITE",
        method: apigatewayv2.HttpMethod.PUT,
    },
    {
        name: "addTagToImage",
        perms: "READWRITE",
        method: apigatewayv2.HttpMethod.PUT,
    },
    {
        name: "deleteImage",
        perms: "READWRITE",
        method: apigatewayv2.HttpMethod.DELETE,
    },
    {
        name: "deleteTag",
        perms: "READWRITE",
        method: apigatewayv2.HttpMethod.DELETE,
    },
    {
        name: "getImage",
        perms: "READ",
        method: apigatewayv2.HttpMethod.GET,
    },
    {
        name: "getTag",
        perms: "READ",
        method: apigatewayv2.HttpMethod.GET,
    },
    {
        name: "getAllTags",
        perms: "READ",
        method: apigatewayv2.HttpMethod.GET,
    },
    {
        name: "queryImagesByTag",
        perms: "READ",
        method: apigatewayv2.HttpMethod.GET,
    },
    {
        name: "queryTagsByImage",
        perms: "READ",
        method: apigatewayv2.HttpMethod.GET,
    },
    {
        name: "removeTagFromImage",
        perms: "WRITE",
        method: apigatewayv2.HttpMethod.DELETE,
    },
    {
        name: "getUntaggedImages",
        perms: "READ",
        method: apigatewayv2.HttpMethod.GET,
    },
    {
        name: "updateUntaggedCount",
        perms: "READWRITE",
    },
    {
        name: "getUntaggedCount",
        perms: "READ",
        method: apigatewayv2.HttpMethod.GET,
    },
]