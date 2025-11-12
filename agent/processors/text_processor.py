"""
Text processing component for natural language understanding
"""

import re
from typing import Dict, Any, List, Optional
from loguru import logger

try:
    from sentence_transformers import SentenceTransformer
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logger.warning("sentence-transformers not available, using fallback processing")

try:
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logger.warning("scikit-learn not available, using fallback similarity calculation")


class TextProcessor:
    """Text processor for natural language understanding and feature extraction"""
    
    def __init__(self, config):
        self.config = config
        
        # Initialize sentence transformer if available
        if TRANSFORMERS_AVAILABLE:
            try:
                self.model = SentenceTransformer(config.embedding_model)
                self.embedding_dim = self.model.get_sentence_embedding_dimension()
                logger.info(f"Loaded sentence transformer: {config.embedding_model}")
            except Exception as e:
                logger.warning(f"Failed to load sentence transformer: {e}")
                self.model = None
                self.embedding_dim = 384  # Default fallback
        else:
            self.model = None
            self.embedding_dim = 384
            
    def process(self, text: str) -> Dict[str, Any]:
        """Process text and extract features"""
        
        if not isinstance(text, str):
            text = str(text)
            
        processed = {
            "original_text": text,
            "cleaned_text": self._clean_text(text),
            "tokens": self._tokenize(text),
            "sentences": self._split_sentences(text),
            "features": self._extract_features(text),
            "embedding": self._get_embedding(text) if self.model else None,
            "language": self._detect_language(text),
            "complexity": self._assess_complexity(text)
        }
        
        return processed
        
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s\.\!\?\,\;\:\-]', '', text)
        
        # Normalize case
        text = text.strip()
        
        return text
        
    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization"""
        
        # Split on whitespace and punctuation
        tokens = re.findall(r'\b\w+\b', text.lower())
        return tokens
        
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        return sentences
        
    def _extract_features(self, text: str) -> Dict[str, Any]:
        """Extract linguistic features"""
        
        tokens = self._tokenize(text)
        sentences = self._split_sentences(text)
        
        features = {
            "word_count": len(tokens),
            "sentence_count": len(sentences),
            "avg_word_length": sum(len(word) for word in tokens) / len(tokens) if tokens else 0,
            "avg_sentence_length": sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0,
            "punctuation_count": len(re.findall(r'[^\w\s]', text)),
            "question_count": text.count('?'),
            "exclamation_count": text.count('!'),
            "has_numbers": bool(re.search(r'\d', text)),
            "has_urls": bool(re.search(r'http[s]?://\S+', text)),
            "has_email": bool(re.search(r'\S+@\S+\.\S+', text))
        }
        
        # Part-of-speech patterns (simplified)
        features["pos_patterns"] = self._extract_pos_patterns(tokens)
        
        return features
        
    def _extract_pos_patterns(self, tokens: List[str]) -> Dict[str, int]:
        """Extract simplified part-of-speech patterns"""
        
        # Very simplified POS detection
        patterns = {
            "nouns": 0,
            "verbs": 0,
            "adjectives": 0,
            "adverbs": 0
        }
        
        # Common word lists for each POS
        nouns = {"time", "person", "year", "way", "day", "man", "thing", "woman", "life", "child", "world", "school", "state", "family", "student", "group", "country", "problem", "hand", "part", "place", "case"}
        verbs = {"be", "have", "do", "say", "go", "get", "make", "know", "think", "take", "see", "come", "want", "look", "use", "find", "give", "tell", "work", "call", "try", "ask", "need", "feel", "become", "leave"}
        adjectives = {"good", "new", "first", "last", "long", "great", "little", "own", "other", "old", "right", "big", "high", "different", "small", "large", "next", "early", "young", "important", "few", "public", "bad", "same", "able"}
        adverbs = {"up", "so", "out", "just", "now", "how", "then", "more", "also", "here", "well", "only", "very", "even", "back", "there", "down", "still", "in", "as", "to", "when", "like", "some", "could", "them", "see", "other", "than", "then", "now", "look", "only", "come", "its", "over", "think", "also", "back", "after", "use", "two", "how", "our", "work"}
        
        for token in tokens:
            if token in nouns:
                patterns["nouns"] += 1
            elif token in verbs:
                patterns["verbs"] += 1
            elif token in adjectives:
                patterns["adjectives"] += 1
            elif token in adverbs:
                patterns["adverbs"] += 1
                
        return patterns
        
    def _get_embedding(self, text: str) -> Optional[List[float]]:
        """Get text embedding using sentence transformer"""
        
        if not self.model:
            return None
            
        try:
            embedding = self.model.encode(text)
            return embedding.tolist()
        except Exception as e:
            logger.warning(f"Failed to generate embedding: {e}")
            return None
            
    def _detect_language(self, text: str) -> str:
        """Simple language detection"""
        
        # Very basic language detection based on common words
        english_words = {"the", "be", "to", "of", "and", "a", "in", "that", "have", "i", "it", "for", "not", "on", "with", "he", "as", "you", "do", "at"}
        tokens = self._tokenize(text)
        
        if not tokens:
            return "unknown"
            
        english_count = sum(1 for token in tokens if token in english_words)
        english_ratio = english_count / len(tokens)
        
        if english_ratio > 0.3:
            return "english"
        else:
            return "unknown"
            
    def _assess_complexity(self, text: str) -> Dict[str, float]:
        """Assess text complexity"""
        
        tokens = self._tokenize(text)
        sentences = self._split_sentences(text)
        
        if not tokens or not sentences:
            return {"score": 0.0, "level": "very_simple"}
            
        # Simple complexity metrics
        avg_word_length = sum(len(word) for word in tokens) / len(tokens)
        avg_sentence_length = len(tokens) / len(sentences)
        
        # Count complex words (words with > 6 characters)
        complex_words = sum(1 for word in tokens if len(word) > 6)
        complex_word_ratio = complex_words / len(tokens)
        
        # Calculate complexity score (0-1)
        complexity_score = (
            min(1.0, avg_word_length / 8) * 0.3 +
            min(1.0, avg_sentence_length / 20) * 0.4 +
            complex_word_ratio * 0.3
        )
        
        # Determine complexity level
        if complexity_score < 0.3:
            level = "simple"
        elif complexity_score < 0.6:
            level = "moderate"
        elif complexity_score < 0.8:
            level = "complex"
        else:
            level = "very_complex"
            
        return {
            "score": complexity_score,
            "level": level,
            "avg_word_length": avg_word_length,
            "avg_sentence_length": avg_sentence_length,
            "complex_word_ratio": complex_word_ratio
        }
        
    def extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """Extract keywords from text"""
        
        tokens = self._tokenize(text)
        
        # Filter out common stop words
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "do", "does", "did", "will", "would", "could", "should", "may", "might", "must", "can", "this", "that", "these", "those", "i", "you", "he", "she", "it", "we", "they", "what", "which", "who", "when", "where", "why", "how"}
        
        filtered_tokens = [token for token in tokens if token not in stop_words and len(token) > 3]
        
        # Count word frequency
        from collections import Counter
        word_counts = Counter(filtered_tokens)
        
        # Return top keywords
        keywords = [word for word, count in word_counts.most_common(max_keywords)]
        return keywords
        
    def extract_entities(self, text: str) -> List[Dict[str, str]]:
        """Extract named entities (simplified)"""
        
        entities = []
        
        # Simple patterns for common entity types
        patterns = {
            "EMAIL": [r'\b[\w\.-]+@[\w\.-]+\.\w+\b'],
            "URL": [r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'],
            "PHONE": [r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'],
            "DATE": [r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b', r'\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b'],
            "MONEY": [r'\$\d+(?:\.\d{2})?', r'\b\d+(?:\.\d{2})?\s*(?:dollars?|USD|bucks?)\b'],
            "CAPITALIZED": [r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b']
        }
        
        for entity_type, type_patterns in patterns.items():
            for pattern in type_patterns:
                matches = re.findall(pattern, text)
                for match in matches:
                    entities.append({
                        "type": entity_type,
                        "text": match,
                        "start": text.find(match),
                        "end": text.find(match) + len(match)
                    })
                    
        return entities
        
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts"""
        
        if not self.model:
            # Fallback to simple word overlap
            tokens1 = set(self._tokenize(text1))
            tokens2 = set(self._tokenize(text2))
            
            if not tokens1 or not tokens2:
                return 0.0
                
            intersection = len(tokens1.intersection(tokens2))
            union = len(tokens1.union(tokens2))
            
            return intersection / union if union > 0 else 0.0
            
        try:
            embedding1 = self.model.encode(text1)
            embedding2 = self.model.encode(text2)
            
            # Calculate cosine similarity
            if SKLEARN_AVAILABLE:
                similarity = cosine_similarity([embedding1], [embedding2])[0][0]
            else:
                # Manual cosine similarity calculation
                dot_product = sum(a * b for a, b in zip(embedding1, embedding2))
                magnitude1 = sum(a * a for a in embedding1) ** 0.5
                magnitude2 = sum(b * b for b in embedding2) ** 0.5
                similarity = dot_product / (magnitude1 * magnitude2) if magnitude1 > 0 and magnitude2 > 0 else 0.0
            
            return float(similarity)
            
        except Exception as e:
            logger.warning(f"Failed to calculate similarity: {e}")
            return 0.0
