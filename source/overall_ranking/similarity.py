from source.document_ranking.tf_idf import TfIdf
from source.page_ranking.page_rank import PageRank


class Similarity:
    """Kelas yang digunakan untuk melakukan perankingan keseluruhan (similarity score)."""

    def __init__(self):
        self.tf_idf = TfIdf()
        self.page_rank = PageRank()
        self.tf_idf_percentage = 0.6
        self.page_rank_percentage = 0.4

    def get_all_similarity_for_api(self, keyword, sort, start=None, length=None):
        """
        Fungsi untuk mendapatkan perankingan keseluruhan berdasarkan keyword tertentu.

        Args:
            keyword (str): Kata pencarian (bisa lebih dari satu kata)
            sort (str): Sort by similarity/pagerank/tfidf
            start (int): Indeks awal (optional, untuk pagination)
            length (int): Total data (optional, untuk pagination)

        Returns:
            list: List berisi dictionary yang terdapat url dan total skor keseluruhan, empty list jika tidak ada datanya
        """

        tfidf_results = self.tf_idf.get_all_tfidf_for_api(keyword, start, length)

        if len(tfidf_results) < 1:
            return []

        page_ids = [res["page_id"] for res in tfidf_results]
        page_rank_results = self.page_rank.get_all_pagerank_by_page_ids(page_ids)

        similarity_scores = []
        for i in range(len(tfidf_results)):
            page_id = page_ids[i]
            url = tfidf_results[i]["url"]
            tfidf_total = tfidf_results[i]["tfidf_total"]

            for page_rank_result in page_rank_results:
                if page_rank_result["page_id"] == page_id:
                    page_rank_score = page_rank_result["pagerank_score"]

            similarity_score = (self.tf_idf_percentage * tfidf_total) + (self.page_rank_percentage + page_rank_score)
            similarity_scores.append(
                {
                    "id_page": page_id,
                    "url": url,
                    "similarity_score": similarity_score,
                    "tfidf_total": tfidf_total,
                    "pagerank_score": page_rank_score,
                }
            )

        if sort == "tfidf":
            sorted_similarity_scores = sorted(similarity_scores, key=lambda d: d["tfidf_total"], reverse=True)
        elif sort == "pagerank":
            sorted_similarity_scores = sorted(similarity_scores, key=lambda d: d["pagerank_score"], reverse=True)
        else:
            sorted_similarity_scores = sorted(similarity_scores, key=lambda d: d["similarity_score"], reverse=True)

        return sorted_similarity_scores
