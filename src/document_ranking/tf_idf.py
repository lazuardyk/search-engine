# Reference: https://www.kaggle.com/code/yclaudel/find-similar-articles-with-tf-idf
from src.database.database import Database

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

class TfIdf:
    def __init__(self):
        self.db = Database()
    
    def search(self, tfidf_matrix, model, request, top_n = 5):
        request_transform = model.transform([request])
        similarity = np.dot(request_transform,np.transpose(tfidf_matrix))
        x = np.array(similarity.toarray()[0])
        indices=np.argsort(x)[-5:][::-1]
        return indices
    
    def print_result(self, request_content, indices, X):
        print('\nKeyword: ' + request_content)
        print('\nBest Results:')
        for i in indices:
            print('id = {0:5d} - title = {1} - url = {2}'.format(i,X['title'].loc[i],X['url'].loc[i]))
    
    def run(self, keyword):
        db_connection = self.db.connect()
        query = "SELECT * FROM `page_information`"
        df = pd.read_sql(query, db_connection)
        # print(df)

        text_content = df['content_text']
        vector = TfidfVectorizer(
                                    lowercase=True, # Convert everything to lower case 
                                    use_idf=True,   # Use idf
                                    norm=u'l2',     # Normalization
                                    smooth_idf=True # Prevents divide-by-zero errors
                                    )
        tfidf = vector.fit_transform(text_content)

        result = self.search(tfidf, vector, keyword, top_n = 5)
        self.print_result(keyword, result, df)
        self.db.close_connection(db_connection)