import os
from dotenv import load_dotenv
import boto3
import json
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
import pandas as pd
from fastapi import FastAPI
import concurrent.futures
from tqdm import tqdm

app = FastAPI()

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
AWS_PROFILE_NAME = "nlightnlabs" # Needed for local dev only.
AWS_REGION = "us-west-2" # Bedkrock is only available in certain regions.  This is one of them.

def start_bedrock_session(profile_name: str = "", region_name: str = AWS_REGION):
    """Return an S3 client for a given AWS profile."""
    
    print("Environment:", ENVIRONMENT)
    
    if ENVIRONMENT == "production":
        session = boto3.Session(region_name=region_name)
    else:
        session = boto3.Session(profile_name=profile_name, region_name=region_name)
    return session.client("bedrock-runtime")

# -------------------------
# Pydantic Models
# -------------------------
class GeneralQueryModel(BaseModel):
    prompt: str
    data: Optional[List[Dict[str, Any]]] = None
    model: str = "sonnet_3_5_v2"
    temperature: float = 0.0
    max_tokens: int = 16000


class ClassifyModel(BaseModel):
    data: List[Dict[str, Any]]
    context_columns: List[str]
    taxonomy: List[Dict[str, Any]]
    prompt: Optional[str] = None
    model: str = "sonnet_3_5_v2"
    temperature: float = 0.0
    max_tokens: int = 16000


class FieldMappingModel(BaseModel):
    data: List[Dict[str, Any]]
    standard_schema: List[Dict[str, Any]]
    batch_size: int = 100  # Number of rows per batch
    max_batches: int = 5   # Maximum number of batches to process
    model: str = "sonnet_3_5_v2"
    temperature: float = 0.0
    max_tokens: int = 16000


# -------------------------
# Model Registry
# -------------------------
models = {
    "opus": "us.anthropic.claude-3-opus-20240229-v1:0",
    "sonnet": "us.anthropic.claude-3-sonnet-20240229-v1:0",
    "haiku": "us.anthropic.claude-3-haiku-20240307-v1:0",
    "sonnet_3_5": "us.anthropic.claude-3-5-sonnet-20240620-v1:0",
    "sonnet_3_5_v2": "us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    "sonnet_3_7": "us.anthropic.claude-3-7-sonnet-20250219-v1:0",
}


# -------------------------
# General question
# -------------------------
import os
import boto3
import json
from datetime import datetime
from pydantic import BaseModel

class GeneralQueryModel(BaseModel):
    model: str = "haiku"
    prompt: str = None
    max_tokens: int = 16000
    temperature: float = 0.0


def ask(request: GeneralQueryModel):
    model_id = models.get(request.model)

    if not request.prompt:
        raise ValueError(f"Missing prompt")


    if not model_id:
        raise ValueError(f"Unsupported model: {request.model}")

    bedrock = start_bedrock_session(profile_name=AWS_PROFILE_NAME, region_name=AWS_REGION)

    payload = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": request.max_tokens,
        "temperature": request.temperature,
        "messages": [{"role": "user", "content": [{"type": "text", "text": request.prompt}]}],
    }

    start = datetime.now()
    response = bedrock.invoke_model(modelId=model_id, body=json.dumps(payload))
    result = json.loads(response["body"].read().decode("utf-8"))
    text = result["content"][0]["text"]
    print(f"Claude response time: {(datetime.now() - start).total_seconds():.2f}s")

    return text


# -------------------------
# Classify Data
# -------------------------
def classify(request: ClassifyModel):
    df = pd.DataFrame(request.data)
    taxonomy = pd.DataFrame(request.taxonomy)
    context_columns = request.context_columns
    results = []

    bedrock = start_bedrock_session(profile_name=AWS_PROFILE_NAME, region_name=AWS_REGION)

    model_id = models.get(request.model)

    for _, row in df.iterrows():
        context_text = " | ".join(
            [f"{col}: {row[col]}" for col in context_columns if pd.notna(row[col])]
        )

        message = f"""
        You are an expert classifier. 
        Assign one category from the taxonomy below that best fits this record.
        Taxonomy:
        {taxonomy.to_json(orient='records')}
        
        Record context:
        {context_text}
        """

        payload = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": request.max_tokens,
            "temperature": request.temperature,
            "messages": [{"role": "user", "content": [{"type": "text", "text": message}]}],
        }

        if request.prompt:
            payload["system"] = [{"type": "text", "text": request.prompt}]

        try:
            response = bedrock.invoke_model(modelId=model_id, body=json.dumps(payload))
            response_body = json.loads(response["body"].read().decode("utf-8"))
            category = response_body["content"][0]["text"].strip()
            results.append(category)
        except Exception as e:
            print(f"Error in row {_}: {e}")
            results.append("Error")

    df["category"] = results
    return df.to_dict(orient="records")




# -------------------------
# Field Mapping
# -------------------------


def process_batch(batch_data: List[Dict], column: str, standard_schema: List[Dict], 
                 model_id: str, temperature: float, max_tokens: int) -> str:
    """
    Process a single batch of data for a specific column
    """

    bedrock = start_bedrock_session(profile_name=AWS_PROFILE_NAME, region_name=AWS_REGION)
    
    # Prepare sample values from the batch
    sample_values = [str(row[column]) for row in batch_data if column in row]
    
    message = f"""
    You are an expert in data mapping. Based on the standard_schema definition and sample data provided,
    determine which standard field best matches the source column '{column}'.
    
    Schema:
    {json.dumps(standard_schema, indent=2)}
    
    Sample data for column '{column}' ({len(sample_values)} records):
    {sample_values}
    
    Return only the matching field_name from the standard_schema. If no suitable match is found, return "NO_MATCH".
    Explain your reasoning in a few sentences after your answer.
    """

    payload = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": [{"role": "user", "content": [{"type": "text", "text": message}]}],
    }

    try:
        response = bedrock.invoke_model(modelId=model_id, body=json.dumps(payload))
        result = json.loads(response["body"].read().decode("utf-8"))
        response_text = result["content"][0]["text"].strip()
        # Extract just the field name (first line of response)
        matched_field = response_text.split('\n')[0].strip()
        return matched_field
    except Exception as e:
        print(f"Error processing batch for column {column}: {e}")
        return "ERROR"
    


def map_fields(request: FieldMappingModel):
    """
    Maps source dataset columns to standard standard_schema fields using both exact matching
    and AI-assisted matching with batch processing.
    """
    # Convert inputs to DataFrames
    df = pd.DataFrame(request.data)
    standard_schema_df = pd.DataFrame(request.standard_schema)
    
    # Initialize results dictionary
    field_mappings = {}
    unmapped_columns = set(df.columns)
    
    # Step 1: Direct matching using aliases
    for standard_schema_field in request.standard_schema:
        field_name = standard_schema_field['field_name']
        aliases = standard_schema_field['example_field_aliases']
        
        # Check for exact matches in column names (case-insensitive)
        for alias in aliases:
            matching_cols = [col for col in unmapped_columns 
                           if col.lower() == alias.lower()]
            if matching_cols:
                field_mappings[matching_cols[0]] = field_name
                unmapped_columns.remove(matching_cols[0])
                break
    
    # Step 2: AI-assisted matching for remaining columns with batch processing
    if unmapped_columns:
        model_id = models[request.model]
        
        # Split data into batches
        total_rows = len(df)
        batch_size = min(request.batch_size, total_rows)
        num_batches = min(request.max_batches, (total_rows + batch_size - 1) // batch_size)
        
        batches = [
            request.data[i:i + batch_size] 
            for i in range(0, min(total_rows, num_batches * batch_size), batch_size)
        ]
        
        # Process each unmapped column
        for column in unmapped_columns:
            print(f"\nProcessing column: {column}")
            field_votes = {}  # Store votes from each batch
            
            # Process each batch for the current column
            for batch_idx, batch in enumerate(tqdm(batches)):
                print(f"Process batch {batch_idx} of {len(batches)}")
                matched_field = process_batch(
                    batch_data=batch,
                    column=column,
                    standard_schema=request.standard_schema,
                    model_id=model_id,
                    temperature=request.temperature,
                    max_tokens=request.max_tokens
                )
                
                # Count votes for each matched field
                if matched_field not in field_votes:
                    field_votes[matched_field] = 0
                field_votes[matched_field] += 1
            
            # Select the field with the most votes
            if field_votes:
                most_common_field = max(field_votes.items(), key=lambda x: x[1])[0]
                # Validate the matched field exists in standard_schema
                if most_common_field in standard_schema_df['field_name'].values:
                    field_mappings[column] = most_common_field
                else:
                    field_mappings[column] = "NO_MATCH"
                
                # Print voting results for transparency
                print(f"\nVoting results for {column}:")
                for field, votes in field_votes.items():
                    print(f"{field}: {votes} votes")
            else:
                field_mappings[column] = "ERROR"

            print(f"Processed {batch_size*(batch_idx+1)} row of {total_rows} rows")

    # Prepare detailed results
    results = {
        "mappings": field_mappings,
        "statistics": {
            "total_columns": len(df.columns),
            "mapped_columns": len([v for v in field_mappings.values() if v != "NO_MATCH" and v != "ERROR"]),
            "unmapped_columns": len([v for v in field_mappings.values() if v == "NO_MATCH"]),
            "error_columns": len([v for v in field_mappings.values() if v == "ERROR"])
        },
        "processing_details": {
            "total_rows": total_rows,
            "batch_size": batch_size,
            "batches_processed": len(batches)
        }
    }
    
    return results



