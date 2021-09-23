import logging
from .collaborative_filtering import collaborative_filtering
import azure.functions as func


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    user_id = req.params.get('userId')
    if not user_id:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            user_id = req_body.get('userId')

    prediction = req.params.get('prediction')
    if not prediction:
        try:
            req_body = req.get_json()
        except ValueError:
            prediction = 0
        else:
            prediction = req_body.get('prediction')

    if user_id:
        cf = collaborative_filtering()        
        cf_scores = cf.get_recommendations(user_id, int(prediction))       
        return func.HttpResponse(f"{cf_scores}")
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a userId in the query string or in the request body for a personalized response.",
             status_code=200
        )
