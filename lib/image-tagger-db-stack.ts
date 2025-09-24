import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';

export class ImageTaggerDBStack extends cdk.Stack {
    public readonly table: dynamodb.Table;

    constructor(scope: Construct, id: string, props?: cdk.StackProps) {
        super(scope, id, props);

        this.table = new dynamodb.Table(this, 'image_tag_db', {
            partitionKey: { name: 'primary_id', type: dynamodb.AttributeType.STRING },
            sortKey: { name: 'secondary_id', type: dynamodb.AttributeType.STRING },
            billingMode: dynamodb.BillingMode.PROVISIONED,
            readCapacity: 2,   // provisioned read capacity units
            writeCapacity: 2,  // provisioned write capacity units
        });

        // GSI for reverse lookups
        this.table.addGlobalSecondaryIndex({
            indexName: 'secondary_id_index',
            partitionKey: { name: 'secondary_id', type: dynamodb.AttributeType.STRING },
            sortKey: { name: 'primary_id', type: dynamodb.AttributeType.STRING },
            projectionType: dynamodb.ProjectionType.KEYS_ONLY, 
            readCapacity: 2,   
            writeCapacity: 2,
        });

        // GSI for time based lookups and other scans/filters on item type
        this.table.addGlobalSecondaryIndex({
            indexName: 'item_type_index',
            partitionKey: { name: 'item_type', type: dynamodb.AttributeType.STRING },
            sortKey: { name: 'created_at', type: dynamodb.AttributeType.STRING },
            projectionType: dynamodb.ProjectionType.INCLUDE, 
            nonKeyAttributes: ['primary_id', 'tag_count'],
            readCapacity: 2,   
            writeCapacity: 2,
        });
    }
}