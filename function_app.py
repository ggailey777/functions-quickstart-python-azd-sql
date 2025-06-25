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
def sql_trigger_todo(changes: str) -> None:
    """SQL trigger function that responds to changes in the ToDo table."""
    logging.info("SQL trigger function processed changes")
    
    # Parse the changes string as JSON
    try:
        changes_list = json.loads(changes)
        
        for change in changes_list:
            # Get the operation type and item data
            operation = change.get('Operation', 'Unknown')
            item_data = change.get('Item', {})
            
            # Convert to ToDoItem for consistent handling
            todo_item = ToDoItem.from_dict(item_data)
            
            logging.info(f"Change operation: {operation}")
            logging.info(f"Id: {todo_item.id}, Title: {todo_item.title}, "
                        f"Url: {todo_item.url}, Completed: {todo_item.completed}")
    except json.JSONDecodeError:
        logging.error(f"Failed to parse changes as JSON: {changes}")
    except Exception as e:
        logging.error(f"Error processing changes: {str(e)}")
        logging.error(f"Changes content: {changes}")


@app.function_name("httptrigger-sql-output")
@app.route(route="httptriggersqloutput", methods=["POST"])
@app.sql_output(arg_name="todo",
                command_text="[dbo].[ToDo]", 
                connection_string_setting="AZURE_SQL_CONNECTION_STRING_KEY")
def http_trigger_sql_output(req: func.HttpRequest, todo: func.Out[func.SqlRow]) -> func.HttpResponse:
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
        
        row = func.SqlRow.from_dict(req_body)
        todo.set(row)
        
        # Return success response
        return func.HttpResponse(
            json.dumps(req_body),
            status_code=201,
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