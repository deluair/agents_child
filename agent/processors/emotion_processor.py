"""
Emotion processing component for sentiment analysis and emotional intelligence
"""

import re
from typing import Dict, Any, List, Optional
from loguru import logger


class EmotionProcessor:
    """Emotion processor for sentiment analysis and emotional state detection"""
    
    def __init__(self):
        # Emotion keywords
        self.emotion_keywords = {
            "joy": ["happy", "joy", "excited", "delighted", "pleased", "glad", "cheerful", "enthusiastic", "wonderful", "fantastic", "great", "amazing", "love", "excellent"],
            "sadness": ["sad", "unhappy", "depressed", "down", "blue", "upset", "disappointed", "hurt", "grief", "sorrow", "miserable", "terrible", "awful"],
            "anger": ["angry", "mad", "furious", "irritated", "annoyed", "frustrated", "outraged", "enraged", "infuriated", "livid", "resentful"],
            "fear": ["afraid", "scared", "fearful", "anxious", "worried", "nervous", "terrified", "panic", "phobia", "dread", "concerned"],
            "surprise": ["surprised", "amazed", "astonished", "shocked", "stunned", "bewildered", "astounded", "unexpected", "sudden"],
            "disgust": ["disgusted", "revolted", "repulsed", "sickened", "nauseated", "appalled", "horrified", "disappointed"],
            "trust": ["trust", "confident", "secure", "safe", "reliable", "dependable", "faithful", "loyal", "honest"],
            "anticipation": ["excited", "eager", "looking forward", "anticipating", "expecting", "hopeful", "optimistic", "waiting"]
        }
        
        # Sentiment words
        self.positive_words = ["good", "great", "excellent", "wonderful", "fantastic", "amazing", "love", "like", "enjoy", "perfect", "best", "awesome", "brilliant", "outstanding", "superb"]
        self.negative_words = ["bad", "terrible", "awful", "horrible", "hate", "dislike", "worst", "disgusting", "dreadful", "appalling", "atrocious", "lousy", "poor"]
        
        # Intensity modifiers
        self.intensity_modifiers = {
            "very": 1.5,
            "extremely": 2.0,
            "really": 1.3,
            "quite": 1.2,
            "somewhat": 0.8,
            "slightly": 0.7,
            "a bit": 0.6,
            "too": 1.4,
            "so": 1.6,
            "incredibly": 1.8,
            "absolutely": 2.0
        }
        
    def analyze(self, text: str) -> Dict[str, Any]:
        """Analyze emotional content of text"""
        
        if not isinstance(text, str):
            text = str(text)
            
        text_lower = text.lower()
        
        # Detect emotions
        emotions = self._detect_emotions(text_lower)
        
        # Analyze sentiment
        sentiment = self._analyze_sentiment(text_lower)
        
        # Extract emotional intensity
        intensity = self._calculate_intensity(text_lower, emotions, sentiment)
        
        # Detect emotional tone
        tone = self._detect_tone(text_lower, emotions, sentiment)
        
        # Identify emotional triggers
        triggers = self._identify_triggers(text_lower)
        
        return {
            "emotions": emotions,
            "sentiment": sentiment,
            "intensity": intensity,
            "tone": tone,
            "triggers": triggers,
            "dominant_emotion": emotions[0]["emotion"] if emotions else "neutral",
            "emotional_complexity": len([e for e in emotions if e["score"] > 0.3])
        }
        
    def _detect_emotions(self, text: str) -> List[Dict[str, Any]]:
        """Detect emotions in text"""
        
        detected_emotions = []
        
        for emotion, keywords in self.emotion_keywords.items():
            score = 0.0
            matched_keywords = []
            
            for keyword in keywords:
                # Count occurrences of keyword
                count = len(re.findall(rf'\b{re.escape(keyword)}\b', text))
                if count > 0:
                    score += count * 0.5
                    matched_keywords.append(keyword)
                    
            # Check for intensity modifiers
            intensity_multiplier = self._get_intensity_multiplier(text)
            score *= intensity_multiplier
            
            if score > 0:
                detected_emotions.append({
                    "emotion": emotion,
                    "score": min(1.0, score),
                    "keywords": matched_keywords,
                    "intensity": intensity_multiplier
                })
                
        # Sort by score and return top emotions
        detected_emotions.sort(key=lambda x: x["score"], reverse=True)
        return detected_emotions
        
    def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment polarity"""
        
        positive_score = 0.0
        negative_score = 0.0
        positive_words = []
        negative_words = []
        
        # Count positive words
        for word in self.positive_words:
            count = len(re.findall(rf'\b{re.escape(word)}\b', text))
            if count > 0:
                positive_score += count
                positive_words.append(word)
                
        # Count negative words
        for word in self.negative_words:
            count = len(re.findall(rf'\b{re.escape(word)}\b', text))
            if count > 0:
                negative_score += count
                negative_words.append(word)
                
        # Apply intensity modifiers
        intensity = self._get_intensity_multiplier(text)
        positive_score *= intensity
        negative_score *= intensity
        
        # Calculate overall sentiment
        total_score = positive_score - negative_score
        max_possible = positive_score + negative_score
        
        if max_possible == 0:
            polarity = 0.0
            sentiment_label = "neutral"
        else:
            polarity = total_score / max_possible
            
            if polarity > 0.3:
                sentiment_label = "positive"
            elif polarity < -0.3:
                sentiment_label = "negative"
            else:
                sentiment_label = "neutral"
                
        return {
            "polarity": polarity,
            "label": sentiment_label,
            "positive_score": positive_score,
            "negative_score": negative_score,
            "positive_words": positive_words,
            "negative_words": negative_words
        }
        
    def _get_intensity_multiplier(self, text: str) -> float:
        """Get intensity multiplier based on modifiers in text"""
        
        multiplier = 1.0
        
        for modifier, value in self.intensity_modifiers.items():
            if modifier in text:
                multiplier = max(multiplier, value)
                
        # Check for exclamation marks
        exclamation_count = text.count('!')
        if exclamation_count > 0:
            multiplier *= (1 + exclamation_count * 0.2)
            
        # Check for all caps
        if text.isupper():
            multiplier *= 1.3
            
        return min(2.0, multiplier)  # Cap at 2.0
        
    def _calculate_intensity(self, text: str, emotions: List[Dict[str, Any]], 
                            sentiment: Dict[str, Any]) -> Dict[str, float]:
        """Calculate emotional intensity"""
        
        # Base intensity from emotions
        emotion_intensity = sum(e["score"] for e in emotions) / len(emotions) if emotions else 0.0
        
        # Sentiment intensity
        sentiment_intensity = abs(sentiment["polarity"])
        
        # Text-based intensity
        text_intensity = self._get_intensity_multiplier(text)
        
        return {
            "overall": (emotion_intensity + sentiment_intensity + text_intensity) / 3,
            "emotional": emotion_intensity,
            "sentiment": sentiment_intensity,
            "textual": text_intensity
        }
        
    def _detect_tone(self, text: str, emotions: List[Dict[str, Any]], 
                    sentiment: Dict[str, Any]) -> str:
        """Detect overall emotional tone"""
        
        if not emotions and sentiment["label"] == "neutral":
            return "neutral"
            
        # Analyze dominant emotion
        if emotions:
            dominant_emotion = emotions[0]["emotion"]
            
            # Map emotions to tones
            tone_mapping = {
                "joy": "positive",
                "trust": "positive",
                "anticipation": "positive",
                "sadness": "negative",
                "anger": "negative",
                "fear": "negative",
                "disgust": "negative",
                "surprise": "neutral"
            }
            
            return tone_mapping.get(dominant_emotion, "neutral")
            
        return sentiment["label"]
        
    def _identify_triggers(self, text: str) -> List[str]:
        """Identify emotional triggers in text"""
        
        triggers = []
        
        # Common trigger patterns
        trigger_patterns = {
            "personal_attack": ["stupid", "idiot", "dumb", "useless", "worthless"],
            "praise": ["brilliant", "genius", "perfect", "excellent", "outstanding"],
            "concern": ["worried", "concerned", "afraid", "scared", "nervous"],
            "excitement": ["excited", "thrilled", "ecstatic", "enthusiastic"],
            "frustration": ["frustrated", "annoyed", "irritated", "bothered"],
            "confusion": ["confused", "unclear", "don't understand", "puzzled"]
        }
        
        for trigger_type, keywords in trigger_patterns.items():
            for keyword in keywords:
                if keyword in text:
                    triggers.append(trigger_type)
                    break
                    
        return list(set(triggers))  # Remove duplicates
        
    def compare_emotions(self, text1: str, text2: str) -> Dict[str, Any]:
        """Compare emotional content between two texts"""
        
        analysis1 = self.analyze(text1)
        analysis2 = self.analyze(text2)
        
        # Compare dominant emotions
        emotion_match = (analysis1["dominant_emotion"] == analysis2["dominant_emotion"])
        
        # Compare sentiment
        sentiment_match = (analysis1["sentiment"]["label"] == analysis2["sentiment"]["label"])
        
        # Calculate emotional similarity
        emotion_similarity = self._calculate_emotional_similarity(analysis1, analysis2)
        
        return {
            "emotion_match": emotion_match,
            "sentiment_match": sentiment_match,
            "emotional_similarity": emotion_similarity,
            "text1_analysis": analysis1,
            "text2_analysis": analysis2
        }
        
    def _calculate_emotional_similarity(self, analysis1: Dict[str, Any], 
                                      analysis2: Dict[str, Any]) -> float:
        """Calculate emotional similarity between two analyses"""
        
        # Get emotion scores as dictionaries
        emotions1 = {e["emotion"]: e["score"] for e in analysis1["emotions"]}
        emotions2 = {e["emotion"]: e["score"] for e in analysis2["emotions"]}
        
        # Get all unique emotions
        all_emotions = set(emotions1.keys()).union(set(emotions2.keys()))
        
        if not all_emotions:
            return 1.0  # Both are neutral
            
        # Calculate cosine similarity
        dot_product = sum(emotions1.get(e, 0) * emotions2.get(e, 0) for e in all_emotions)
        magnitude1 = sum(emotions1.get(e, 0) ** 2 for e in all_emotions) ** 0.5
        magnitude2 = sum(emotions2.get(e, 0) ** 2 for e in all_emotions) ** 0.5
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
            
        return dot_product / (magnitude1 * magnitude2)
        
    def get_emotional_progression(self, texts: List[str]) -> Dict[str, Any]:
        """Analyze emotional progression across multiple texts"""
        
        if not texts:
            return {"progression": [], "summary": {}}
            
        analyses = [self.analyze(text) for text in texts]
        
        progression = []
        for i, analysis in enumerate(analyses):
            progression.append({
                "index": i,
                "dominant_emotion": analysis["dominant_emotion"],
                "sentiment": analysis["sentiment"]["label"],
                "intensity": analysis["intensity"]["overall"],
                "emotional_complexity": analysis["emotional_complexity"]
            })
            
        # Calculate summary statistics
        emotions = [p["dominant_emotion"] for p in progression]
        sentiments = [p["sentiment"] for p in progression]
        intensities = [p["intensity"] for p in progression]
        
        summary = {
            "emotion_distribution": {e: emotions.count(e) for e in set(emotions)},
            "sentiment_distribution": {s: sentiments.count(s) for s in set(sentiments)},
            "average_intensity": sum(intensities) / len(intensities) if intensities else 0.0,
            "intensity_range": {"min": min(intensities), "max": max(intensities)} if intensities else {"min": 0, "max": 0},
            "emotional_volatility": self._calculate_volatility(intensities)
        }
        
        return {
            "progression": progression,
            "summary": summary
        }
        
    def _calculate_volatility(self, values: List[float]) -> float:
        """Calculate emotional volatility (standard deviation)"""
        
        if len(values) < 2:
            return 0.0
            
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        
        return variance ** 0.5
