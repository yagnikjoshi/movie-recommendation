import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class RecommendationEngine:
    def __init__(self, df):
        """Initialize recommendation engine with movie DataFrame."""
        self.df = df.copy()
        self.df.reset_index(drop=True, inplace=True)
        self._build_similarity_matrix()

    def _build_similarity_matrix(self):
        """Compute TF-IDF and Cosine Similarity matrix."""
        # Using max_features=5000 and min_df=2 to optimize memory for 1000+ movies
        self.tfidf = TfidfVectorizer(stop_words='english', ngram_range=(1, 2), max_features=5000, min_df=2)
        self.tfidf_matrix = self.tfidf.fit_transform(self.df['combined_features'].fillna(''))
        self.cosine_sim = cosine_similarity(self.tfidf_matrix, self.tfidf_matrix)

        # Precompute IMDB Weighted Rating
        C = self.df['vote_average'].mean()
        m = self.df['vote_count'].quantile(0.50)  # 50th percentile as threshold

        def calculate_weighted_rating(x):
            v = x['vote_count']
            R = x['vote_average']
            return (v / (v + m) * R) + (m / (v + m) * C)

        self.df['weighted_rating'] = self.df.apply(calculate_weighted_rating, axis=1)
        min_wr = self.df['weighted_rating'].min()
        max_wr = self.df['weighted_rating'].max()
        if max_wr > min_wr:
            self.df['norm_rating'] = (self.df['weighted_rating'] - min_wr) / (max_wr - min_wr)
        else:
            self.df['norm_rating'] = 1.0

    def recommend(self, title, top_n=6, genre_filter=None, min_rating=0.0, popularity_weight=0.2):
        """
        Get top_n movie recommendations based on content similarity and popularity weighting.
        """
        matches = self.df[self.df['title'].str.lower() == title.lower()]
        if matches.empty:
            # Fallback if exact title match fails: try substring match
            matches = self.df[self.df['title'].str.lower().str.contains(title.lower())]
            if matches.empty:
                return pd.DataFrame()

        idx = matches.index[0]

        # Get pair-wise similarity scores
        sim_scores = list(enumerate(self.cosine_sim[idx]))

        # Calculate hybrid score
        hybrid_scores = []
        for i, sim in sim_scores:
            norm_r = self.df.loc[i, 'norm_rating']
            final_score = (1 - popularity_weight) * sim + (popularity_weight) * norm_r
            hybrid_scores.append((i, final_score, sim))

        # Sort by final score
        hybrid_scores = sorted(hybrid_scores, key=lambda x: x[1], reverse=True)

        # Exclude the input movie itself
        hybrid_scores = [item for item in hybrid_scores if item[0] != idx]

        if not hybrid_scores:
            return pd.DataFrame()

        # Find max similarity for relative scaling
        max_sim = max([item[2] for item in hybrid_scores]) if hybrid_scores else 1.0
        if max_sim == 0:
            max_sim = 1.0

        recommended_indices = []
        similarity_values = []
        match_percentages = []

        for i, score, raw_sim in hybrid_scores:
            row = self.df.iloc[i]
            
            # Apply filters if provided
            if genre_filter and genre_filter != "All":
                if genre_filter.lower() not in row['genres'].lower():
                    continue
                    
            if row['vote_average'] < min_rating:
                continue

            recommended_indices.append(i)
            similarity_values.append(raw_sim)
            
            # Intuitive match percentage calculation (scaled relative to max similarity + quality score)
            rel_sim = raw_sim / max_sim
            match_pct = int(round(65 + rel_sim * 25 + row['norm_rating'] * 10))
            match_pct = min(99, max(60, match_pct))
            match_percentages.append(match_pct)

            if len(recommended_indices) == top_n:
                break

        if not recommended_indices:
            return pd.DataFrame()

        recs = self.df.iloc[recommended_indices].copy()
        recs['similarity_score'] = similarity_values
        recs['match_percentage'] = match_percentages
        return recs

    def get_similarity_matrix_for_movies(self, movie_indices):
        """Return sub-matrix of similarity scores for visualization."""
        sub_matrix = self.cosine_sim[np.ix_(movie_indices, movie_indices)]
        return sub_matrix

    def get_common_keywords(self, movie1_title, movie2_title):
        """Find overlapping words/genres between two movies."""
        m1 = self.df[self.df['title'].str.lower() == movie1_title.lower()]
        m2 = self.df[self.df['title'].str.lower() == movie2_title.lower()]
        if m1.empty or m2.empty:
            return []
        
        g1 = set([g.strip().lower() for g in m1.iloc[0]['genres'].split(',')])
        g2 = set([g.strip().lower() for g in m2.iloc[0]['genres'].split(',')])
        common = g1.intersection(g2)
        return list(common)
