from typing import Dict, List
import numpy as np
import logging

logger = logging.getLogger(__name__)

class BehavioralScoringEngine:
    def __init__(self):
        self.berakhlak_dimensions = [
            "berorientasi_pelayanan",
            "akuntabel",
            "kompeten",
            "harmonis",
            "loyal",
            "adaptif",
            "kolaboratif"
        ]
    
    def calculate_dimension_scores(
        self,
        nlp_scores: Dict[str, float],
        emotion_stability: float,
        speech_clarity: float,
        coherence: float
    ) -> Dict[str, float]:
        dimension_scores = {}
        
        for dimension in self.berakhlak_dimensions:
            nlp_score = nlp_scores.get(dimension, 0.0)
            
            behavioral_modifier = (emotion_stability * 0.3 + 
                                 speech_clarity * 0.3 + 
                                 coherence * 0.4)
            
            final_score = (nlp_score * 0.7 + behavioral_modifier * 0.3)
            
            dimension_scores[dimension] = round(final_score * 5, 2)
        
        return dimension_scores
    
    def calculate_overall_score(
        self,
        dimension_scores: Dict[str, float],
        emotion_stability: float,
        speech_clarity: float,
        coherence: float
    ) -> Dict[str, float]:
        avg_dimension = np.mean(list(dimension_scores.values()))
        
        behavioral_score = (
            emotion_stability * 0.25 +
            speech_clarity * 0.25 +
            coherence * 0.5
        ) * 5
        
        overall = (avg_dimension * 0.7 + behavioral_score * 0.3)
        
        return {
            "overall_ai_score": round(overall, 2),
            "emotion_stability": round(emotion_stability * 5, 2),
            "speech_clarity": round(speech_clarity * 5, 2),
            "answer_coherence": round(coherence * 5, 2)
        }
    
    def calculate_final_score(
        self,
        ai_scores: Dict[str, float],
        manual_scores: Dict[str, float]
    ) -> float:
        ai_avg = np.mean([v for v in ai_scores.values() if v is not None])
        
        manual_values = [v for v in manual_scores.values() if v is not None]
        if manual_values:
            manual_avg = np.mean(manual_values)
            final = (ai_avg * 0.6 + manual_avg * 0.4)
        else:
            final = ai_avg
        
        return round(final, 2)
    
    def generate_recommendation(self, final_score: float) -> str:
        if final_score >= 4.0:
            return "layak"
        elif final_score >= 3.0:
            return "dipertimbangkan"
        else:
            return "tidak_layak"
    
    def generate_summary(
        self,
        dimension_scores: Dict[str, float],
        emotion_stability: float,
        speech_clarity: float,
        coherence: float,
        dominant_emotions: List[str]
    ) -> str:
        summary_parts = []
        
        summary_parts.append("RINGKASAN ANALISIS PERILAKU")
        summary_parts.append("=" * 50)
        
        summary_parts.append("\n1. NILAI BerAKHLAK:")
        for dimension, score in dimension_scores.items():
            label = dimension.replace("_", " ").title()
            rating = self._get_rating(score)
            summary_parts.append(f"   - {label}: {score}/5.0 ({rating})")
        
        summary_parts.append("\n2. INDIKATOR PERILAKU:")
        summary_parts.append(f"   - Stabilitas Emosi: {emotion_stability*5:.2f}/5.0 ({self._get_rating(emotion_stability*5)})")
        summary_parts.append(f"   - Kejelasan Komunikasi: {speech_clarity*5:.2f}/5.0 ({self._get_rating(speech_clarity*5)})")
        summary_parts.append(f"   - Koherensi Jawaban: {coherence*5:.2f}/5.0 ({self._get_rating(coherence*5)})")
        
        summary_parts.append("\n3. ANALISIS EMOSI:")
        emotion_counts = {}
        for emotion in dominant_emotions:
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        if emotion_counts:
            most_common = max(emotion_counts, key=emotion_counts.get)
            summary_parts.append(f"   - Emosi dominan: {most_common}")
            summary_parts.append(f"   - Variasi emosi: {len(emotion_counts)} jenis emosi terdeteksi")
        
        highest_dimension = max(dimension_scores, key=dimension_scores.get)
        lowest_dimension = min(dimension_scores, key=dimension_scores.get)
        
        summary_parts.append("\n4. KESIMPULAN:")
        summary_parts.append(f"   - Kekuatan: {highest_dimension.replace('_', ' ').title()} ({dimension_scores[highest_dimension]}/5.0)")
        summary_parts.append(f"   - Area Pengembangan: {lowest_dimension.replace('_', ' ').title()} ({dimension_scores[lowest_dimension]}/5.0)")
        
        return "\n".join(summary_parts)
    
    def _get_rating(self, score: float) -> str:
        if score >= 4.5:
            return "Sangat Baik"
        elif score >= 3.5:
            return "Baik"
        elif score >= 2.5:
            return "Cukup"
        elif score >= 1.5:
            return "Kurang"
        else:
            return "Sangat Kurang"
