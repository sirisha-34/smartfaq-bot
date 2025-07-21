import pandas as pd
from fuzzywuzzy import process

class FAQBot:
    def __init__(self, faq_path):
        self.faq_df = pd.read_csv(faq_path)

    def find_best_match(self, query):
        questions = self.faq_df['Question'].tolist()
        best_match, score = process.extractOne(query, questions)
        if score > 70:
            answer = self.faq_df[self.faq_df['Question'] == best_match]['Answer'].values[0]
            return best_match, answer, score
        return None, "Sorry, I couldn't find a relevant answer.", score

    def add_faq(self, question, answer):
        new_entry = pd.DataFrame([[question, answer]], columns=['Question', 'Answer'])
        self.faq_df = pd.concat([self.faq_df, new_entry], ignore_index=True)
        self.faq_df.to_csv("faq_data.csv", index=False)