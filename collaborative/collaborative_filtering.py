from surprise import dump
from pymongo import MongoClient
import pandas as pd

class collaborative_filtering:
    def __init__(self):

        db_url = "mongodb://127.0.0.1"
        db_port = 27017
        db_name = 'mycontent'
        coll_name = 'mycontent'

        client = MongoClient(db_url, db_port)
        db = client[db_name]
        self.mycontent = db[coll_name]       
            
        _, self.algo = dump.load('./collaborative/KNNBaseline.dump')
    
    def get_articles_list(self, user_id):
        return self.mycontent.find({"user_id": {"$ne": int(user_id)}}).distinct('click_article_id')

    def cf_sort(self, data):
        return data[2]

    def get_recommendations(self, user_id, prediction):
        score = []
        for article_id in self.get_articles_list(user_id):        
            rating = self.algo.predict(user_id, article_id)             
            score.append([user_id, article_id,round(rating.est)])

        score.sort(key=self.cf_sort, reverse=True)
        score_df = pd.DataFrame(score, columns=['user_id', 'article_id', 'CF'])

        if prediction > 0:
            score_df = score_df['article_id'][:prediction]

        return score_df.to_json(orient = 'records')        

    
