import logging
from shared_code.content_based_filtering import content_based_filtering
from shared_code.collaborative_filtering import collaborative_filtering
import azure.functions as func
from pathlib import Path
import pandas as pd


def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    '''Get Score for article recommendation
        Args:
            req (HttRequest): user request
            context (Context): Azure function context

        Returns:
            HttResponse: List of selected articles
    '''    
    
    # user ID
    user_id = req.params.get('userId')
    if not user_id:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            user_id = req_body.get('userId')

     # recommendation (number of)
    recommendation = req.params.get('recommendation')
    if not recommendation:
        try:
            req_body = req.get_json()
        except ValueError:
            recommendation = 2
        else:
            recommendation = req_body.get('recommendation')
    
    # Do recommendation
    if user_id:
        logging.info("Process content filtering")
        filename = str(context.function_directory) + '/../shared_code/articles_embeddings.pickle'
        cbf = content_based_filtering(filename)        
        cbf_scores = cbf.get_recommendations(user_id, 0)

        logging.info("Process collaborative filtering")
        model = str(context.function_directory) + '/../shared_code/model.dump'
        cf = collaborative_filtering(model)        
        cf_scores = cf.get_recommendations(user_id, 0)    

        logging.info("Set hybrid recommendations")
        hybrid = pd.merge(cf_scores, cbf_scores, on=['user_id','article_id'])
        hybrid['score'] = hybrid['CF'] * 2 + hybrid['CBF']

        hybrid = hybrid.sort_values(by=['score'], ascending=False)
        return func.HttpResponse(f"{hybrid['article_id'][:int(recommendation)].to_json(orient = 'records')}")
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a userId in the query string or in the request body for a personalized response.",
             status_code=200
        )