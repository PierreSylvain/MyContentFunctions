import logging
import requests
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

    if user_id:
        cbf_scores = requests.get('http://localhost:7071/api/content-based?userId=' + user_id + '&prediction=3')
        # cf_scores = requests.get('http://localhost:7071/api/collaborative?userId=' + user_id + '&prediction=3')
        return func.HttpResponse(f"{cbf_scores}")
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a userId in the query string or in the request body for a personalized response.",
             status_code=200
        )
