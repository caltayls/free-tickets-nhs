from src.app.app import find_events

def lambda_handler(event, context):
    print("Lambda handler called.")
    find_events()
    print("Script ran successfully.")