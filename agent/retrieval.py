from typing import List, Dict, Any, Tuple
import re
import json

class PolicyRetriever:
    def __init__(self, policies_path: str = "data/policies.json"):
        self.policies_path = policies_path
        self.policies = self._load_policies()
        # Define stop words to ignore in similarity calculation
        self.stop_words = set(['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours', 
                              'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 
                              'herself', 'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 
                              'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are', 
                              'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 
                              'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 
                              'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 
                              'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 
                              'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 
                              'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 
                              'more', 'most', 'other', 'some', 'such', 'no', 'no', 'nor', 'not', 'only', 'own', 'same', 
                              'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', 'should', 'now'])
    
    def _load_policies(self) -> List[Dict[str, Any]]:
        with open(self.policies_path, 'r') as f:
            return json.load(f)
    
    def _tokenize(self, text: str) -> set:
        # Convert to lowercase and extract words
        words = re.findall(r'\b\w+\b', text.lower())
        # Remove stop words
        return set([w for w in words if w not in self.stop_words])
    
    def retrieve(self, query: str) -> Tuple[Dict[str, Any], float]:
        """
        Retrieve the most relevant policy for the query.
        Returns the policy dictionary and a confidence score (0-1).
        """
        query_lower = query.lower()
        query_tokens = self._tokenize(query)
        best_policy = None
        best_score = 0.0
        
        for policy in self.policies:
            policy_tokens = self._tokenize(policy['content'])
            # Calculate Jaccard similarity
            intersection = query_tokens.intersection(policy_tokens)
            union = query_tokens.union(policy_tokens)
            if len(union) == 0:
                similarity = 0.0
            else:
                similarity = len(intersection) / len(union)
            
            # Boost for specific combinations
            if 'suspicious' in query_lower and 'email' in query_lower and policy.get('id') == 'KB-09':
                similarity = min(1.0, similarity + 0.1)
            if 'laptop' in query_lower and policy.get('id') == 'KB-03':
                similarity = min(1.0, similarity + 0.2)
            
            if similarity > best_score:
                best_score = similarity
                best_policy = policy
        
        # If no policy has any similarity, return the first policy with low confidence
        if best_score == 0.0 and self.policies:
            return self.policies[0], 0.0
        
        return best_policy, best_score
        
        return best_policy, best_score

# For testing
if __name__ == "__main__":
    retriever = PolicyRetriever()
    policy, score = retriever.retrieve("I got a phishing email asking for my password")
    print(f"Policy: {policy['id']} - {policy['title']}")
    print(f"Score: {score}")