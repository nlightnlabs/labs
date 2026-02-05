
from dotenv import load_dotenv
import importlib
import pandas as pd
from typing import Dict, Any
import asyncio
from pydantic import BaseModel


# Define request model for validation
class RunAppRequest(BaseModel):
    app_name: str  # Python file/app name without .py
    main_function: str  # Function to call within the module
    parameters: Dict[str, Any] = {}  # Parameters to pass to the function


# Function to dynamically import and run an app function (Synchronous)
def import_app(filepath: str, app_name: str, function: str, parameters: Dict[str, Any]):
    try:
        # Import the module dynamically
        module = importlib.import_module(f"{filepath}.{app_name}")

        # Get the function dynamically
        func = getattr(module, function)

        # Call the function with parameters
        return func(**parameters) if parameters else func()

    except Exception as e:
        raise RuntimeError(f"Error importing or executing {app_name}.{function}: {str(e)}")


async def run_app(request: RunAppRequest):
    filepath = "apps"  # Directory where your apps are stored

    if not request.app_name or not request.main_function:
        raise Exception(status_code=400, detail="Module name and function name are required")

    try:
        # Run import_app asynchronously using asyncio.to_thread (non-blocking)
        result = await asyncio.to_thread(import_app, filepath, request.app_name, request.main_function, request.parameters)
        print(f"Result from app: {result}")

        # Handle different response types
        if result is not None:
            if isinstance(result, (dict, list)):
                return result  # FastAPI automatically converts JSON-serializable data
            elif isinstance(result, pd.DataFrame):
                return result.to_dict(orient="records")  # Convert DataFrame to JSON
            else:
                return {"result": str(result)}  # Convert other types to string
        else:
            raise Exception(status_code=404, detail="No data found")

    except Exception as e:
        raise Exception(status_code=500, detail=f"Error executing app function: {str(e)}")