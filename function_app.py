import logging
import json
from typing import List
import azure.functions as func
from todo_item import ToDoItem


# Initialize the function app
app = func.FunctionApp()


@app.sql_trigger(arg_name="changes", 
                 table_name="[dbo].[ToDo]",
                 connection_string_setting="AZURE_SQL_CONNECTION_STRING_KEY")
def sql_trigger_todo(changes: List[func.SqlRow]) -> None:
    """SQL trigger function that responds to changes in the ToDo table."""
    logging.info("SQL trigger function processed changes")
    
    for change in changes:
        # Get the operation type and item data
        operation = change.operation
        item_data = dict(change.item)
        
        # Convert to ToDoItem for consistent handling
        todo_item = ToDoItem.from_dict(item_data)
        
        logging.info(f"Change operation: {operation}")
        logging.info(f"Id: {todo_item.id}, Title: {todo_item.title}, "
                    f"Url: {todo_item.url}, Completed: {todo_item.completed}")


@app.function_name("httptrigger-sql-output")
@app.route(route="httptrigger-sql-output", methods=["POST"])
@app.sql_output(arg_name="todo_output",
                table_name="dbo.ToDo", 
                connection_string_setting="AZURE_SQL_CONNECTION_STRING_KEY")
def http_trigger_sql_output(req: func.HttpRequest, todo_output: func.Out[func.SqlRow]) -> func.HttpResponse:
    """HTTP trigger with SQL output binding to insert ToDo items."""
    logging.info('Python HTTP trigger with SQL Output Binding function processed a request.')
    
    try:
        # Parse the request body
        req_body = req.get_json()
        
        if not req_body:
            return func.HttpResponse(
                "Please pass a valid JSON object in the request body",
                status_code=400
            )
        
        # Create ToDoItem from request
        todo_item = ToDoItem.from_dict(req_body)
        
        # Set the SQL output - using the dictionary directly since SqlRow.from_dict may not exist
        todo_output.set(todo_item.to_dict())
        
        # Return success response
        return func.HttpResponse(
            json.dumps(todo_item.to_dict()),
            status_code=200,
            mimetype="application/json"
        )
        
    except ValueError as e:
        logging.error(f"JSON parsing error: {e}")
        return func.HttpResponse(
            "Invalid JSON in request body",
            status_code=400
        )
    except Exception as e:
        logging.error(f"Error processing request: {e}")
        return func.HttpResponse(
            "Internal server error",
            status_code=500
        )