import logging
from surprise import dump
from pymongo import MongoClient
import pandas as pd
import random
import os

class collaborative_filtering:
    """Algorithm for collaborative filtering
    """
    def __init__(self, model):
        """Init class : set directory name for data files

        Args:
            model (string): Model to load
        """
        logging.info(model)        
        self.model = model
        
    def get_articles_list(self, user_id):
        """Get list of all articles

        Args:
            user_id (int): User ID

        Returns:
            list: List of article IDs
        """
        client = MongoClient(os.environ["MONGO_URI"])       
        db = client['mycontent2']
        mycontent = db['mycontent']    
        return mycontent.find().distinct('click_article_id')

    def get_recommendations(self, user_id, recommendation):
        """Get collaborative filtering

        Args:
            user_id (int): User ID
            recommendation (int): Number of recommendation to return

        Returns:
            json or dataframe: json with the list of articles IDS or dataframe with all the records
        """
        score = []
        logging.info(self.model)
        _, algo = dump.load(self.model)        
        for article_id in self.get_articles_list(user_id):                  
            rating = algo.predict(user_id, article_id)                  
            score.append([rating.uid, rating.iid,rating.est, round(rating.est)])
        score_df = pd.DataFrame(score, columns=['user_id', 'article_id', 'raw', 'CF'])       
        score_df = score_df.sort_values(by=['raw'], ascending=False)

        if recommendation > 0:
            score_df = score_df['article_id'][:recommendation]
            return score_df.to_json(orient = 'records')
        
        return score_df
        
    
