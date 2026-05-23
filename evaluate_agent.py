# evaluate_agent.py - Calculate competition scores
import requests
import json
import numpy as np
from rouge_score import rouge_scorer
from bert_score import BERTScorer
from typing import List, Dict, Any
import time

class AgentEvaluator:
    def __init__(self, api_base="http://localhost:8000"):
        self.api_base = api_base
        self.scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
        # Initialize BERTScore (downloads model first time)
        self.bert_scorer = BERTScorer(lang="en", rescale_with_baseline=True)
        
    def calculate_rouge(self, generated: str, reference: str) -> Dict:
        """Calculate ROUGE scores for review quality"""
        scores = self.scorer.score(reference, generated)
        return {
            "rouge1": scores['rouge1'].fmeasure,
            "rouge2": scores['rouge2'].fmeasure,
            "rougeL": scores['rougeL'].fmeasure
        }
    
    def calculate_bertscore(self, generated: List[str], references: List[str]) -> float:
        """Calculate BERTScore for semantic similarity"""
        P, R, F1 = self.bert_scorer.score(generated, references)
        return F1.mean().item()
    
    def calculate_rmse(self, predictions: List[float], actuals: List[float]) -> float:
        """Calculate RMSE for rating accuracy"""
        return np.sqrt(np.mean((np.array(predictions) - np.array(actuals)) ** 2))
    
    def calculate_ndcg(self, recommendations: List[Dict], ground_truth: List[str], k=10) -> float:
        """Calculate NDCG@k for ranking quality"""
        # Simplified NDCG calculation
        relevances = []
        for i, rec in enumerate(recommendations[:k]):
            relevance = 1 if rec.get('name') in ground_truth else 0
            relevances.append(relevance)
        
        # Calculate DCG
        dcg = sum([rel / np.log2(i + 2) for i, rel in enumerate(relevances)])
        
        # Calculate IDCG (ideal)
        ideal_rel = sorted(relevances, reverse=True)
        idcg = sum([rel / np.log2(i + 2) for i, rel in enumerate(ideal_rel)])
        
        return dcg / idcg if idcg > 0 else 0
    
    def test_task_a(self, test_cases: List[Dict]) -> Dict:
        """Evaluate Task A performance"""
        print("\n" + "="*50)
        print("Evaluating Task A - User Modeling")
        print("="*50)
        
        predictions = []
        ground_truth_ratings = []
        generated_reviews = []
        reference_reviews = []
        
        for i, case in enumerate(test_cases):
            print(f"\nTest case {i+1}/{len(test_cases)}...")
            
            # Call API
            response = requests.post(
                f"{self.api_base}/task_a/review",
                json={
                    "user_persona": case["user"],
                    "product_details": case["product"]
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                predictions.append(result["rating"])
                ground_truth_ratings.append(case["expected_rating"])
                generated_reviews.append(result["review_text"])
                reference_reviews.append(case["reference_review"])
            else:
                print(f"Error: {response.status_code}")
            
            time.sleep(0.5)  # Avoid rate limiting
        
        # Calculate scores
        rmse = self.calculate_rmse(predictions, ground_truth_ratings)
        rouge_scores = {}
        for gen, ref in zip(generated_reviews, reference_reviews):
            rouge = self.calculate_rouge(gen, ref)
            for k in rouge:
                rouge_scores[k] = rouge_scores.get(k, 0) + rouge[k]
        
        # Average ROUGE scores
        for k in rouge_scores:
            rouge_scores[k] /= len(generated_reviews)
        
        bertscore = self.calculate_bertscore(generated_reviews, reference_reviews)
        
        return {
            "rmse": rmse,
            "rouge_scores": rouge_scores,
            "bertscore": bertscore,
            "samples_evaluated": len(generated_reviews)
        }
    
    def test_task_b(self, test_cases: List[Dict]) -> Dict:
        """Evaluate Task B performance"""
        print("\n" + "="*50)
        print("Evaluating Task B - Recommendation")
        print("="*50)
        
        ndcg_scores = []
        hit_rates = []
        
        for i, case in enumerate(test_cases):
            print(f"\nTest case {i+1}/{len(test_cases)}...")
            
            response = requests.post(
                f"{self.api_base}/task_b/recommend",
                json={
                    "user_persona": case["user"],
                    "conversation_history": []
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                recommendations = result["recommendations"]
                
                # Calculate NDCG@10
                ndcg = self.calculate_ndcg(recommendations, case["relevant_items"], k=10)
                ndcg_scores.append(ndcg)
                
                # Calculate Hit Rate (did top-1 match?)
                hit = 1 if recommendations and recommendations[0]["name"] in case["relevant_items"] else 0
                hit_rates.append(hit)
            else:
                print(f"Error: {response.status_code}")
            
            time.sleep(0.5)
        
        return {
            "ndcg_10": np.mean(ndcg_scores),
            "hit_rate": np.mean(hit_rates),
            "samples_evaluated": len(ndcg_scores)
        }
    
    def generate_report(self, task_a_results: Dict, task_b_results: Dict) -> str:
        """Generate formatted report"""
        report = f"""
{'='*60}
BCT LLM AGENT - COMPETITION SCORING REPORT
{'='*60}

TASK A - User Modeling (55 points possible)
--------------------------------------------
Rating Accuracy (RMSE):     {task_a_results['rmse']:.4f}  (Lower is better, target <0.5)
ROUGE-1 Score:              {task_a_results['rouge_scores']['rouge1']:.4f}
ROUGE-2 Score:              {task_a_results['rouge_scores']['rouge2']:.4f}
ROUGE-L Score:              {task_a_results['rouge_scores']['rougeL']:.4f}
BERTScore:                  {task_a_results['bertscore']:.4f}

TASK B - Recommendation (50 points possible)
--------------------------------------------
NDCG@10:                    {task_b_results['ndcg_10']:.4f}  (Target >0.6)
Hit Rate:                   {task_b_results['hit_rate']:.4f}

Samples Evaluated: {task_a_results['samples_evaluated']} (Task A), {task_b_results['samples_evaluated']} (Task B)

{'='*60}
"""
        return report

# Sample test cases (use real data from your datasets)
if __name__ == "__main__":
    # Create test cases based on your dataset
    test_cases_a = [
        {
            "user": {"age": 22, "location": "Lagos", "interests": ["food"], "preferences": {"price_sensitive": True, "likes_spicy": True}},
            "product": {"name": "Jollof Rice", "category": "food", "price": 2500, "description": "Nigerian jollof rice"},
            "expected_rating": 4,
            "reference_review": "This jollof rice is delicious and authentic. Worth the price!"
        },
        {
            "user": {"age": 30, "location": "Abuja", "interests": ["tech"], "preferences": {"price_sensitive": False, "likes_spicy": False}},
            "product": {"name": "Laptop", "category": "tech", "price": 500000, "description": "High performance laptop"},
            "expected_rating": 5,
            "reference_review": "Excellent laptop, very fast and reliable."
        }
    ]
    
    test_cases_b = [
        {
            "user": {"age": 22, "location": "Lagos", "interests": ["food", "tech"], "preferences": {"price_sensitive": True}},
            "relevant_items": ["Amazon Gift Card", "Jollof Rice", "Power Bank"]
        }
    ]
    
    evaluator = AgentEvaluator()
    
    print("Starting evaluation...")
    print("Make sure your server is running: python main_final.py")
    print()
    
    input("Press Enter to start Task A evaluation...")
    results_a = evaluator.test_task_a(test_cases_a)
    
    input("\nPress Enter to start Task B evaluation...")
    results_b = evaluator.test_task_b(test_cases_b)
    
    # Print report
    print(evaluator.generate_report(results_a, results_b))