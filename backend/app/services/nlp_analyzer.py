from sentence_transformers import SentenceTransformer
from typing import Dict, List
import numpy as np
import logging

logger = logging.getLogger(__name__)

# Check if sentence transformer is available
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMER_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMER_AVAILABLE = False
    logger.warning("Sentence transformer not available - will use keyword matching for sentiment")

class NLPAnalyzer:
    def __init__(self):
        self.model = None
        self.berakhlak_keywords = {
            "berorientasi_pelayanan": [
                "melayani", "membantu", "kepentingan publik", "masyarakat", "pelayanan prima",
                "customer service", "responsif", "tanggap", "peduli", "mengutamakan"
            ],
            "akuntabel": [
                "bertanggung jawab", "akuntabilitas", "transparan", "melaporkan", "pertanggungjawaban",
                "konsekuensi", "jujur", "terbuka", "dapat dipertanggungjawabkan"
            ],
            "kompeten": [
                "kemampuan", "keterampilan", "profesional", "ahli", "berpengalaman",
                "berkualitas", "terlatih", "mahir", "menguasai", "kapabel", "skill"
            ],
            "harmonis": [
                "kerjasama", "harmoni", "rukun", "damai", "toleran", "menghormati",
                "perbedaan", "saling menghargai", "keberagaman", "inklusif"
            ],
            "loyal": [
                "setia", "loyalitas", "komitmen", "dedikasi", "pengabdian", "integritas",
                "konsisten", "berkomitmen", "dedikasi tinggi"
            ],
            "adaptif": [
                "fleksibel", "adaptasi", "perubahan", "inovasi", "kreatif", "dinamis",
                "menyesuaikan", "terbuka terhadap perubahan", "inovatif", "berkembang"
            ],
            "kolaboratif": [
                "kolaborasi", "teamwork", "tim", "bersama-sama", "gotong royong",
                "koordinasi", "sinergi", "bekerjasama", "kerja tim"
            ]
        }
        
        self.berakhlak_examples = {
            "berorientasi_pelayanan": [
                "Saya selalu mengutamakan kepentingan masyarakat dalam bekerja",
                "Memberikan pelayanan terbaik adalah prioritas utama saya"
            ],
            "akuntabel": [
                "Saya bertanggung jawab penuh atas setiap keputusan yang saya buat",
                "Transparansi dan akuntabilitas adalah prinsip kerja saya"
            ],
            "kompeten": [
                "Saya memiliki keahlian dan pengalaman yang relevan dengan posisi ini",
                "Saya terus mengembangkan kompetensi dan keterampilan profesional saya"
            ],
            "harmonis": [
                "Saya menghargai perbedaan dan menciptakan lingkungan kerja yang harmonis",
                "Toleransi dan saling menghormati sangat penting dalam tim"
            ],
            "loyal": [
                "Saya berkomitmen tinggi terhadap organisasi dan tugas yang diberikan",
                "Dedikasi dan loyalitas adalah bagian dari integritas saya"
            ],
            "adaptif": [
                "Saya fleksibel dan mudah beradaptasi dengan perubahan",
                "Inovasi dan kreativitas adalah kunci menghadapi tantangan baru"
            ],
            "kolaboratif": [
                "Saya percaya kerjasama tim menghasilkan hasil yang lebih baik",
                "Saya aktif berkolaborasi dan berkontribusi dalam tim"
            ]
        }
    
    def initialize(self):
        if self.model is None:
            logger.info("Loading sentence transformer model")
            self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
            
            self.berakhlak_embeddings = {}
            for dimension, examples in self.berakhlak_examples.items():
                self.berakhlak_embeddings[dimension] = self.model.encode(examples)
            
            logger.info("NLP model loaded successfully")
    
    def analyze_berakhlak_values(self, text: str) -> Dict[str, float]:
        self.initialize()
        
        text_lower = text.lower()
        scores = {}
        
        for dimension, keywords in self.berakhlak_keywords.items():
            keyword_score = sum(1 for keyword in keywords if keyword in text_lower)
            keyword_score = min(keyword_score / 3.0, 1.0)
            
            text_embedding = self.model.encode([text])
            dimension_embeddings = self.berakhlak_embeddings[dimension]
            
            similarities = []
            for dim_emb in dimension_embeddings:
                sim = np.dot(text_embedding[0], dim_emb) / (
                    np.linalg.norm(text_embedding[0]) * np.linalg.norm(dim_emb)
                )
                similarities.append(sim)
            
            semantic_score = max(similarities) if similarities else 0.0
            
            final_score = (keyword_score * 0.4 + semantic_score * 0.6)
            scores[dimension] = max(0.0, min(1.0, final_score))
        
        return scores
    
    def calculate_coherence(self, text_segments: List[str]) -> float:
        if len(text_segments) < 2:
            return 1.0
        
        self.initialize()
        
        embeddings = self.model.encode(text_segments)
        
        similarities = []
        for i in range(len(embeddings) - 1):
            sim = np.dot(embeddings[i], embeddings[i+1]) / (
                np.linalg.norm(embeddings[i]) * np.linalg.norm(embeddings[i+1])
            )
            similarities.append(sim)
        
        coherence = np.mean(similarities)
        return max(0.0, min(1.0, coherence))
    
    def analyze_sentiment(self, text: str) -> Dict:
        """
        Analyze sentiment using semantic similarity with positive/negative reference sentences.
        Returns dict with score (0.0-1.0) and label (positive/neutral/negative).
        
        This is much more accurate than keyword matching as it understands context.
        """
        if not text or len(text.strip()) < 5:
            return {'score': 0.5, 'label': 'neutral', 'confidence': 0.0}
        
        self.initialize()
        
        # Use semantic similarity for accurate sentiment analysis
        if self.model and SENTENCE_TRANSFORMER_AVAILABLE:
            return self._analyze_sentiment_semantic(text)
        else:
            # Fallback to improved keyword-based analysis
            return self._analyze_sentiment_keywords(text)
    
    def _analyze_sentiment_semantic(self, text: str) -> Dict:
        """
        Semantic sentiment analysis using sentence transformers.
        Compares text with positive and negative reference sentences.
        """
        # Reference sentences for positive and negative sentiment (Indonesian)
        positive_references = [
            "Saya sangat senang dan puas dengan pengalaman ini",
            "Ini adalah hal yang sangat baik dan positif",
            "Saya merasa optimis dan bersemangat tentang ini",
            "Pengalaman yang luar biasa dan menyenangkan",
            "Saya sangat antusias dan termotivasi"
        ]
        
        negative_references = [
            "Saya sangat kecewa dan tidak puas dengan ini",
            "Ini adalah pengalaman yang buruk dan negatif",
            "Saya merasa pesimis dan tidak yakin tentang ini",
            "Pengalaman yang mengecewakan dan tidak menyenangkan",
            "Saya merasa frustasi dan tidak termotivasi"
        ]
        
        try:
            # Encode text and references
            text_embedding = self.model.encode([text])[0]
            positive_embeddings = self.model.encode(positive_references)
            negative_embeddings = self.model.encode(negative_references)
            
            # Calculate similarities
            positive_similarities = [
                np.dot(text_embedding, pos_emb) / (
                    np.linalg.norm(text_embedding) * np.linalg.norm(pos_emb)
                ) for pos_emb in positive_embeddings
            ]
            
            negative_similarities = [
                np.dot(text_embedding, neg_emb) / (
                    np.linalg.norm(text_embedding) * np.linalg.norm(neg_emb)
                ) for neg_emb in negative_embeddings
            ]
            
            # Get max similarities
            max_positive = max(positive_similarities)
            max_negative = max(negative_similarities)
            avg_positive = np.mean(positive_similarities)
            avg_negative = np.mean(negative_similarities)
            
            # Calculate sentiment score
            # Range: 0.0 (very negative) to 1.0 (very positive)
            # 0.5 is neutral
            if max_positive > max_negative:
                # More positive
                confidence = max_positive
                # Score between 0.5 and 1.0
                score = 0.5 + (max_positive * 0.5)
                label = 'positive' if score >= 0.65 else 'neutral'
            elif max_negative > max_positive:
                # More negative
                confidence = max_negative
                # Score between 0.0 and 0.5
                score = 0.5 - (max_negative * 0.5)
                label = 'negative' if score <= 0.35 else 'neutral'
            else:
                # Neutral
                confidence = max(max_positive, max_negative)
                score = 0.5
                label = 'neutral'
            
            # Ensure score is in valid range
            score = max(0.0, min(1.0, score))
            
            return {
                'score': float(score),
                'label': label,
                'confidence': float(confidence)
            }
            
        except Exception as e:
            logger.error(f"Error in semantic sentiment analysis: {e}")
            # Fallback to keyword-based
            return self._analyze_sentiment_keywords(text)
    
    def _analyze_sentiment_keywords(self, text: str) -> Dict:
        """
        Improved keyword-based sentiment analysis (fallback).
        """
        # Expanded keyword lists for better coverage
        positive_words = [
            "baik", "bagus", "senang", "suka", "positif", "setuju", "ya", "benar",
            "hebat", "luar biasa", "sempurna", "optimal", "efektif", "berhasil",
            "memuaskan", "antusias", "termotivasi", "bersemangat", "optimis",
            "sangat baik", "excellent", "mantap", "oke", "siap", "mampu"
        ]
        
        negative_words = [
            "buruk", "jelek", "sedih", "tidak", "negatif", "salah", "kurang",
            "gagal", "mengecewakan", "pesimis", "sulit", "masalah", "kesulitan",
            "lemah", "kurang baik", "tidak baik", "belum", "susah", "tidak mampu",
            "tidak bisa", "tidak dapat", "tidak siap"
        ]
        
        text_lower = text.lower()
        
        # Count occurrences (not just presence)
        positive_count = sum(text_lower.count(word) for word in positive_words)
        negative_count = sum(text_lower.count(word) for word in negative_words)
        
        total = positive_count + negative_count
        
        if total == 0:
            return {'score': 0.5, 'label': 'neutral', 'confidence': 0.0}
        
        # Calculate sentiment score
        sentiment_ratio = (positive_count - negative_count) / total
        score = (sentiment_ratio + 1) / 2  # Convert from [-1, 1] to [0, 1]
        
        # Determine label
        if score >= 0.65:
            label = 'positive'
        elif score <= 0.35:
            label = 'negative'
        else:
            label = 'neutral'
        
        # Confidence based on total word count
        confidence = min(1.0, total / 5.0)  # Higher if more sentiment words found
        
        return {
            'score': float(score),
            'label': label,
            'confidence': float(confidence)
        }
    
    def analyze_sentiment_legacy(self, text: str) -> float:
        """
        Legacy method for backward compatibility.
        Returns only the score (0.0-1.0).
        """
        result = self.analyze_sentiment(text)
        return result['score']
    
    def cleanup(self):
        if self.model is not None:
            del self.model
            self.model = None
            logger.info("NLP model cleaned up")
