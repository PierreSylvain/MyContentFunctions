import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId
import pickle
import numpy as np
import pandas as pd
import json
import os
import logging

class content_based_filtering:
    def __init__(self, filename):
        self.df = None               
           
        # Load articles
        self.articles = pickle.load( open(filename, "rb" ) )   
   
    def get_cosine_similarity(self, a, b):
        """Returns the cosine similarity of 2 vectors
        @params
            a vector
            b vector
        @return
            cosine similarity
        """
        dot_product = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        return dot_product / (norm_a * norm_b)

    def get_last_article(self, user_id):
        """Get the last article ID for a given user ID

        Args:
            user_id (string): User ID

        Returns:
            int: Article ID
        """        
        client = MongoClient(os.environ["MONGO_URI"])       
        db = client['mycontent2']
        mycontent = db['mycontent']    

        doc = mycontent.find_one(
                {"user_id": int(user_id)},
                sort=[('click_timestamp', pymongo.DESCENDING)]
        )
        logging.info(f"last user Doc {doc['click_article_id']}")
        if doc is None:
            return 0

        return doc['click_article_id']


    def cbf_sort(self, data):
        return data[2]

    def get_recommendations(self, user_id, prediction):
        """Get Score for article recommendation

        Args:
            user_id (int): User ID

        Returns:
            Array: Array of articles with recommentation score and score rating
        """
        article_id = self.get_last_article(user_id)
        
        self.articles = np.delete(self.articles, (article_id,), axis=0)
        score = []
        for idx, article in enumerate(self.articles):
            sim = self.get_cosine_similarity(
                np.array(self.articles[article_id]), np.array(article))
            if sim <= 0.25:
                cbf = 0
            elif sim < 0.5:
                cbf = 1
            elif sim <= 0.5:
                cbf = 2
            else:
                cbf = 3
            score.append([user_id, idx, sim, cbf])

        score.sort(key=self.cbf_sort, reverse=True)
        score_df = pd.DataFrame(score, columns=['user_id', 'article_id', 'sim', 'CBF'])

        if prediction > 0:
            score_df = score_df['article_id'][:prediction]
            return score_df.to_json(orient = 'records')
            
        return score_df
        


