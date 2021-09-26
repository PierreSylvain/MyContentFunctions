from surprise import dump
from pymongo import MongoClient
import pandas as pd
import random
import os

class collaborative_filtering:
    def __init__(self, directory):       
        self.directory = directory
        
    def get_articles_list(self, user_id):
        client = MongoClient(os.environ["MONGO_URI"])       
        db = client['mycontent2']
        mycontent = db['mycontent']    
        return mycontent.find().distinct('click_article_id')

    def get_recommendations(self, user_id, prediction):
        score = []
        
        _, algo = dump.load(self.directory + 'model.dump')   
        for article_id in self.get_articles_list(user_id):                  
            rating = algo.predict(user_id, article_id)                  
            score.append([rating.uid, rating.iid,rating.est, round(rating.est)])
        score_df = pd.DataFrame(score, columns=['user_id', 'article_id', 'raw', 'CF'])
        score_df = score_df.sort_values(by=['CF'], ascending=False)

        if prediction > 0:
            score_df = score_df['article_id'][:prediction]
            return score_df.to_json(orient = 'records')
        
        return score_df
        
    
