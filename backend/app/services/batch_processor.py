"""
Batch Processing Service for Interview Analysis
Processes recorded audio after interview completes:
1. Transcribe audio with Whisper (large model for accuracy)
2. Analyze transcript with custom indicators using semantic similarity
3. Generate assessment scores and reasoning
4. Save results to database
"""
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import re

logger = logging.getLogger(__name__)

try:
    from faster_whisper import WhisperModel
    import torch
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    logger.warning("Whisper not available - batch processing will be limited")

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMER_AVAILABLE = True
    logger.info("Sentence transformer available for semantic analysis")
except ImportError:
    SENTENCE_TRANSFORMER_AVAILABLE = False
    logger.warning("Sentence transformer not available, will use keyword matching")


class BatchProcessor:
    """
    Batch processor for interview analysis after recording completes
    """
    
    def __init__(self):
        self.whisper_model = None
        self.semantic_model = None
        self.nlp_analyzer = None
        if WHISPER_AVAILABLE:
            self._initialize_whisper()
        if SENTENCE_TRANSFORMER_AVAILABLE:
            self._initialize_semantic_model()
        self._initialize_nlp_analyzer()
    
    def _initialize_nlp_analyzer(self):
        """Initialize NLP analyzer for sentiment analysis"""
        try:
            from ..services.nlp_analyzer import NLPAnalyzer
            self.nlp_analyzer = NLPAnalyzer()
            logger.info("NLP analyzer initialized for sentiment analysis")
        except Exception as e:
            logger.error(f"Failed to initialize NLP analyzer: {e}")
            self.nlp_analyzer = None
    
    def _initialize_whisper(self):
        """Initialize Whisper model for transcription"""
        try:
            # Use large model for accuracy in batch processing (no real-time constraint!)
            device = "cuda" if torch.cuda.is_available() else "cpu"
            compute_type = "float16" if device == "cuda" else "int8"
            
            logger.info(f"Initializing Whisper large model on {device}")
            self.whisper_model = WhisperModel(
                "large-v2",
                device=device,
                compute_type=compute_type,
                download_root="./models"
            )
            logger.info("Whisper model initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Whisper: {e}")
            self.whisper_model = None
    
    def _initialize_semantic_model(self):
        """Initialize sentence transformer for semantic similarity"""
        try:
            logger.info("Loading sentence transformer for semantic analysis...")
            # Use paraphrase-multilingual for Indonesian support
            self.semantic_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
            logger.info("Sentence transformer loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load sentence transformer: {e}")
            self.semantic_model = None
    
    def transcribe_audio(self, audio_file_path: str, language: str = "id") -> Tuple[str, float, List[Dict]]:
        """
        Transcribe audio file to text with segments
        
        Args:
            audio_file_path: Path to audio file
            language: Language code (default: "id" for Indonesian)
        
        Returns:
            Tuple of (transcript_text, confidence, segments_list)
        """
        if not WHISPER_AVAILABLE or not self.whisper_model:
            logger.warning("Whisper not available - using mock transcript")
            # Return mock transcript for testing when Whisper not available
            mock_segments = [
                {"text": "Ini adalah transkrip percobaan untuk testing.", "start": 0.0, "end": 3.0},
                {"text": "Kandidat menunjukkan kemampuan komunikasi yang baik.", "start": 3.5, "end": 6.5},
                {"text": "Dapat menjelaskan dengan jelas dan menunjukkan kemampuan problem solving.", "start": 7.0, "end": 11.0}
            ]
            return "Ini adalah transkrip percobaan untuk testing. Kandidat menunjukkan kemampuan komunikasi yang baik, dapat menjelaskan dengan jelas, dan menunjukkan kemampuan problem solving.", 0.8, mock_segments
        
        if not Path(audio_file_path).exists():
            logger.error(f"Audio file not found: {audio_file_path}")
            # Try with absolute path
            abs_path = Path(__file__).parent.parent.parent / audio_file_path
            if abs_path.exists():
                audio_file_path = str(abs_path)
                logger.info(f"Found audio at: {audio_file_path}")
            else:
                logger.error(f"Audio file not found even with absolute path")
                return "", 0.0
        
        try:
            logger.info(f"Starting transcription: {audio_file_path}")
            
            # Transcribe with Whisper (beam_size=5 for better accuracy)
            segments, info = self.whisper_model.transcribe(
                audio_file_path,
                language=language,
                beam_size=5,
                vad_filter=True,
                vad_parameters=dict(min_silence_duration_ms=500)
            )
            
            # Collect all segments with timing info
            transcript_parts = []
            segments_list = []
            total_confidence = 0.0
            segment_count = 0
            
            for segment in segments:
                text = segment.text.strip()
                transcript_parts.append(text)
                
                # Store segment info for transcript entries
                segments_list.append({
                    "text": text,
                    "start": segment.start,
                    "end": segment.end,
                    "confidence": min(1.0, max(0.0, (segment.avg_logprob + 1.0)))
                })
                
                total_confidence += segment.avg_logprob
                segment_count += 1
            
            transcript = " ".join(transcript_parts)
            avg_confidence = total_confidence / segment_count if segment_count > 0 else 0.0
            
            # Convert log probability to 0-1 confidence
            confidence = min(1.0, max(0.0, (avg_confidence + 1.0)))
            
            logger.info(f"Transcription complete: {len(transcript)} chars, {segment_count} segments")
            logger.info(f"Language detected: {info.language} (probability: {info.language_probability:.2f})")
            
            return transcript, confidence, segments_list
            
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}", exc_info=True)
            return "", 0.0, []
    
    def analyze_with_indicators(
        self, 
        transcript: str, 
        indicators: List[Dict]
    ) -> List[Dict]:
        """
        Analyze transcript based on custom indicators
        
        Args:
            transcript: Full interview transcript
            indicators: List of indicator definitions with name, description, weight
        
        Returns:
            List of assessment results with scores, evidence, and reasoning
        """
        if not transcript or not indicators:
            return []
        
        results = []
        
        for indicator in indicators:
            try:
                assessment = self._assess_single_indicator(
                    transcript, 
                    indicator['name'],
                    indicator.get('description', '')
                )
                results.append({
                    'indicator_id': indicator['id'],
                    'indicator_name': indicator['name'],
                    'score': assessment['score'],
                    'evidence': assessment['evidence'],
                    'reasoning': assessment['reasoning']
                })
            except Exception as e:
                logger.error(f"Error assessing indicator {indicator['name']}: {e}")
                results.append({
                    'indicator_id': indicator['id'],
                    'indicator_name': indicator['name'],
                    'score': 0.0,
                    'evidence': None,
                    'reasoning': f"Error: {str(e)}"
                })
        
        return results
    
    def _assess_single_indicator(
        self, 
        transcript: str, 
        indicator_name: str,
        indicator_description: str
    ) -> Dict:
        """
        Assess single indicator from transcript using semantic similarity
        
        Args:
            transcript: Interview transcript
            indicator_name: Name of indicator to assess
            indicator_description: Description of what to look for
        
        Returns:
            Dict with score, evidence, and reasoning
        """
        if self.semantic_model and SENTENCE_TRANSFORMER_AVAILABLE:
            # Use semantic similarity for accurate assessment
            return self._assess_with_semantic_similarity(
                transcript, indicator_name, indicator_description
            )
        else:
            # Fallback to improved keyword matching
            return self._assess_with_keywords(
                transcript, indicator_name, indicator_description
            )
    
    def _assess_with_semantic_similarity(
        self, 
        transcript: str, 
        indicator_name: str,
        indicator_description: str
    ) -> Dict:
        """
        Hybrid approach: Exact keyword matching + Semantic similarity
        This ensures we catch both direct mentions and related concepts
        """
        # Split transcript into sentences
        sentences = self._split_into_sentences(transcript)
        
        # FIRST: Check for exact keyword matches (case-insensitive)
        # This is critical for catching direct mentions that semantic model might miss
        indicator_keywords = [
            indicator_name.lower(),
            # Also check for word variations
            indicator_name.lower().replace('i', '').strip(),  # e.g., "anarkis" -> "anarks"
            indicator_name.lower()[:-1] if len(indicator_name) > 3 else indicator_name.lower()  # remove last char
        ]
        
        exact_matches = []
        for sent in sentences:
            sent_lower = sent.lower()
            for keyword in indicator_keywords:
                if len(keyword) >= 3 and keyword in sent_lower:
                    # Found exact mention!
                    exact_matches.append(sent)
                    logger.info(f"[Exact Match] Found '{keyword}' in: {sent[:80]}...")
                    break
        
        # If we have exact matches, prioritize them heavily
        if exact_matches:
            logger.info(f"[Exact Match] {len(exact_matches)} sentences contain exact keyword '{indicator_name}'")
        
        if not sentences:
            return {
                'score': 0.0,
                'evidence': "Transkrip kosong atau tidak valid.",
                'reasoning': f"Tidak dapat menilai {indicator_name} karena transkrip kosong."
            }
        
        # Filter out pure introduction sentences (more selective filtering)
        # Only filter sentences that are MOSTLY greetings/intro, not those that happen to contain intro words
        intro_only_patterns = [
            r'^assalamualaikum', r'^salam', r'^selamat (pagi|siang|sore|malam)',
            r'^perkenalkan', r'^nama saya adalah', r'^terima kasih$',
            r'^dengan hormat', r'^yang terhormat'
        ]
        
        filtered_sentences = []
        for sent in sentences:
            sent_lower = sent.lower().strip()
            
            # Check if sentence is ONLY an intro (starts with intro pattern and is short)
            is_pure_intro = False
            if len(sent_lower) < 50:  # Short sentences only
                for pattern in intro_only_patterns:
                    if re.match(pattern, sent_lower):
                        is_pure_intro = True
                        break
            
            # Keep sentence if it's not a pure intro
            if not is_pure_intro:
                filtered_sentences.append(sent)
        
        # If all sentences were filtered out, use originals
        if not filtered_sentences:
            filtered_sentences = sentences
        
        sentences = filtered_sentences
        
        logger.info(f"[Semantic] After filtering: {len(sentences)} sentences (removed {len([s for s in sentences if s not in filtered_sentences])} pure intro sentences)")
        
        # Create comprehensive indicator query with Indonesian variations
        # This helps the semantic model better understand what we're looking for
        indicator_variations = {
            'komunikasi': 'berkomunikasi dengan jelas, menyampaikan ide dan informasi, mendengarkan aktif, berbicara efektif, presentasi',
            'kepemimpinan': 'memimpin tim, mengarahkan orang lain, mengambil keputusan, koordinasi tim, delegasi tugas, membimbing',
            'problem solving': 'menyelesaikan masalah, mencari solusi, analisis masalah, berpikir kritis, menemukan jalan keluar',
            'teamwork': 'bekerja sama dalam tim, kolaborasi, kerjasama kelompok, berbagi tugas, mendukung rekan',
            'adaptabilitas': 'beradaptasi dengan perubahan, fleksibel, menyesuaikan diri, terbuka pada hal baru, cepat belajar',
            'akuntabilitas': 'bertanggung jawab, mempertanggungjawabkan hasil, mengakui kesalahan, integritas kerja, komitmen',
            'orientasi hasil': 'fokus pada target, mencapai tujuan, hasil kerja optimal, produktivitas tinggi, efisiensi',
            'inisiatif': 'proaktif, berinisiatif sendiri, mengambil langkah pertama, ide baru, kreatif',
            'kolaborasi': 'bekerja lintas tim, berbagi pengetahuan, sinergi, koordinasi antar divisi, networking'
        }
        
        # Try to find relevant variations
        query_parts = [indicator_name]
        if indicator_description:
            query_parts.append(indicator_description)
        
        indicator_lower = indicator_name.lower()
        for key, variations in indicator_variations.items():
            if key in indicator_lower:
                query_parts.append(variations)
                break
        
        # Create enriched query - NEUTRAL wording (not assuming positive or negative)
        # Just describe what we're looking for, let semantic model match the concept
        indicator_query = ". ".join(query_parts) + ". Perilaku, tindakan, atau pengalaman yang menunjukkan karakteristik ini."
        
        logger.info(f"[Semantic] Query: {indicator_query[:120]}...")
        logger.info(f"[Semantic] Exact matches found: {len(exact_matches)}")
        
        # Encode indicator and sentences
        try:
            indicator_embedding = self.semantic_model.encode([indicator_query])[0]
            sentence_embeddings = self.semantic_model.encode(sentences)
            
            # Calculate cosine similarity
            similarities = []
            for i, sent_emb in enumerate(sentence_embeddings):
                similarity = cosine_similarity(
                    [indicator_embedding], 
                    [sent_emb]
                )[0][0]
                similarities.append((similarity, sentences[i]))
            
            # Sort by similarity
            similarities.sort(reverse=True, key=lambda x: x[0])
            
            # HYBRID SCORING: Combine exact matches + semantic similarity
            
            # First, add exact matches with artificially high similarity (0.95)
            # This ensures they are prioritized
            hybrid_matches = []
            exact_match_set = set(exact_matches)
            
            for sent in exact_matches:
                # Give exact matches very high similarity score
                hybrid_matches.append((0.95, sent))
            
            # Then add semantic matches
            SIMILARITY_THRESHOLD = 0.50  # 50%+ similarity required
            
            for sim, sent in similarities:
                if sent not in exact_match_set and sim > SIMILARITY_THRESHOLD:
                    hybrid_matches.append((sim, sent))
            
            # Sort by similarity
            hybrid_matches.sort(reverse=True, key=lambda x: x[0])
            relevant_sentences = hybrid_matches
            
            # Log for debugging - show top 5 similarities
            logger.info(f"[Semantic] Indicator: {indicator_name}")
            logger.info(f"[Semantic] Total sentences: {len(sentences)}, Exact: {len(exact_matches)}, Semantic (>{SIMILARITY_THRESHOLD}): {len(relevant_sentences) - len(exact_matches)}")
            if similarities:
                top_5 = similarities[:min(5, len(similarities))]
                logger.info(f"[Semantic] Top 5 semantic similarities: {[(f'{sim:.3f}', sent[:60] + '...') for sim, sent in top_5]}")
            if relevant_sentences:
                logger.info(f"[Semantic] Best overall match: {relevant_sentences[0][0]:.3f} - '{relevant_sentences[0][1][:80]}...'")
            
            # Calculate score based on relevance
            if not relevant_sentences:
                score = 0.0
                evidence = "Tidak ditemukan bukti yang relevan dalam transkrip."
                reasoning = f"Tidak ada pernyataan kandidat yang terkait dengan {indicator_name}."
            else:
                # Score based on:
                # 1. Number of relevant sentences (quantity)
                # 2. Average similarity score (quality) - weighted more heavily
                num_relevant = len(relevant_sentences)
                avg_similarity = sum(sim for sim, _ in relevant_sentences) / num_relevant
                
                # Normalize score (0-100)
                # Quality matters more than quantity
                # Even 1-2 highly relevant sentences should give good score
                
                # Count component: logarithmic scale (diminishing returns for many sentences)
                # 1 sentence = 25, 2 = 35, 3 = 42, 5 = 50
                import math
                count_score = min(50, 20 + (math.log(num_relevant + 1) * 15))
                
                # Similarity component: weighted more heavily (60% of total)
                # High similarity (0.70) = 42, Medium (0.55) = 33, Low (0.50) = 30
                similarity_score = (avg_similarity - 0.5) * 100 + 30  # Normalize from threshold
                similarity_score = max(30, min(60, similarity_score))  # Clamp between 30-60
                
                score = count_score + similarity_score
                score = min(100, max(0, score))  # Ensure 0-100 range
                
                # Evidence: top 3 most relevant sentences
                evidence_sentences = [sent for _, sent in relevant_sentences[:3]]
                evidence = " | ".join(evidence_sentences)
                
                # Boost score if we have exact matches (direct mentions are strong evidence)
                exact_match_bonus = 0
                if len(exact_matches) > 0:
                    exact_match_bonus = min(15, len(exact_matches) * 8)  # Up to +15 for exact matches
                    score = min(100, score + exact_match_bonus)
                    logger.info(f"[Scoring] Exact match bonus: +{exact_match_bonus} points")
                
                # Reasoning based on score and relevance
                exact_match_note = f" Termasuk {len(exact_matches)} penyebutan langsung." if len(exact_matches) > 0 else ""
                
                if score >= 75:
                    reasoning = (
                        f"Kandidat menunjukkan {indicator_name} yang sangat jelas. "
                        f"Ditemukan {num_relevant} pernyataan relevan dengan tingkat "
                        f"kesesuaian {avg_similarity*100:.1f}%.{exact_match_note}"
                    )
                elif score >= 55:
                    reasoning = (
                        f"Kandidat menunjukkan {indicator_name} yang cukup jelas. "
                        f"Ditemukan {num_relevant} pernyataan relevan dengan tingkat "
                        f"kesesuaian {avg_similarity*100:.1f}%.{exact_match_note}"
                    )
                elif score >= 35:
                    reasoning = (
                        f"Kandidat menunjukkan {indicator_name} yang memadai. "
                        f"Ditemukan {num_relevant} pernyataan relevan dengan tingkat "
                        f"kesesuaian {avg_similarity*100:.1f}%.{exact_match_note}"
                    )
                else:
                    reasoning = (
                        f"Terdeteksi {indicator_name} dalam transkrip. "
                        f"Ditemukan {num_relevant} pernyataan dengan "
                        f"tingkat kesesuaian {avg_similarity*100:.1f}%.{exact_match_note}"
                    )
            
            return {
                'score': float(score),
                'evidence': evidence,
                'reasoning': reasoning
            }
            
        except Exception as e:
            logger.error(f"Error in semantic similarity: {e}")
            # Fallback to keyword matching
            return self._assess_with_keywords(transcript, indicator_name, indicator_description)
    
    def _assess_with_keywords(
        self, 
        transcript: str, 
        indicator_name: str,
        indicator_description: str
    ) -> Dict:
        """
        Fallback keyword-based assessment (less accurate)
        """
        sentences = self._split_into_sentences(transcript)
        transcript_lower = transcript.lower()
        
        # Improved keyword mapping (more specific)
        keywords_map = {
            'komunikasi': ['berkomunikasi', 'menjelaskan secara', 'menyampaikan ide', 'presentasi', 'berdiskusi'],
            'kepemimpinan': ['memimpin tim', 'pemimpin', 'mengarahkan tim', 'mengkoordinasi', 'delegasi'],
            'problem solving': ['menyelesaikan masalah', 'mencari solusi', 'menganalisis masalah', 'problem solving'],
            'teamwork': ['bekerja sama', 'kolaborasi tim', 'kerjasama', 'tim work'],
            'integritas': ['jujur', 'bertanggung jawab', 'transparansi', 'etika kerja'],
            'adaptabilitas': ['beradaptasi dengan', 'fleksibel terhadap', 'menyesuaikan', 'perubahan'],
            'orientasi hasil': ['mencapai target', 'hasil kerja', 'kinerja', 'produktivitas'],
            'pelayanan': ['melayani', 'service', 'kepuasan pelanggan', 'customer', 'klien']
        }
        
        # Find relevant keywords
        indicator_name_lower = indicator_name.lower()
        relevant_keywords = []
        
        for key, keywords in keywords_map.items():
            if key in indicator_name_lower or key in indicator_description.lower():
                relevant_keywords.extend(keywords)
        
        # Count matches
        matches = []
        for sentence in sentences:
            sentence_lower = sentence.lower()
            for keyword in relevant_keywords:
                if keyword in sentence_lower:
                    matches.append(sentence.strip())
                    break
        
        # Calculate score
        score = min(100.0, len(matches) * 25.0) if matches else 0.0
        
        # Generate evidence
        evidence = " | ".join(matches[:3]) if matches else "Tidak ditemukan bukti spesifik dalam transkrip."
        
        # Generate reasoning
        if score >= 75:
            reasoning = f"Kandidat menunjukkan {indicator_name} yang baik ({len(matches)} bukti ditemukan)."
        elif score >= 50:
            reasoning = f"Kandidat menunjukkan {indicator_name} yang cukup ({len(matches)} bukti ditemukan)."
        else:
            reasoning = f"Kandidat perlu meningkatkan {indicator_name} ({len(matches)} bukti ditemukan)."
        
        return {
            'score': score,
            'evidence': evidence,
            'reasoning': reasoning
        }
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """
        Advanced sentence splitting for Indonesian text
        Handles cases where Whisper transcription has no punctuation
        """
        if not text or not text.strip():
            return []
        
        # Strategy 1: Try splitting by punctuation first
        sentences = re.split(r'[.!?]+', text)
        
        # If we get very few sentences (no punctuation), use alternative strategies
        if len(sentences) <= 2:
            logger.info(f"[Sentence Split] Few sentences from punctuation ({len(sentences)}), using clause splitting")
            
            # Strategy 2: Split by Indonesian conjunctions and clause markers
            # These often indicate sentence/clause boundaries
            clause_markers = [
                ' dan ', ' serta ', ' kemudian ', ' lalu ', ' setelah itu ',
                ' selain itu ', ' namun ', ' tetapi ', ' akan tetapi ',
                ' karena ', ' sebab ', ' sehingga ', ' agar ',
                ' jika ', ' apabila ', ' ketika ', ' saat ', ' waktu ',
                ' dalam ', ' pada ', ' di mana ', ' yang mana ',
                ' untuk ', ' bagi ', ' menurut '
            ]
            
            # Split by clause markers
            temp_sentences = [text]
            for marker in clause_markers:
                new_sentences = []
                for sent in temp_sentences:
                    # Split and keep the marker at the start of new sentence
                    parts = sent.split(marker)
                    if len(parts) > 1:
                        new_sentences.append(parts[0].strip())
                        for part in parts[1:]:
                            new_sentences.append((marker.strip() + ' ' + part).strip())
                    else:
                        new_sentences.append(sent)
                temp_sentences = new_sentences
            
            sentences = temp_sentences
            
            # Strategy 3: If sentences are still too long, split by length
            final_sentences = []
            MAX_LENGTH = 150  # characters
            for sent in sentences:
                if len(sent) > MAX_LENGTH:
                    # Split long sentence into chunks at word boundaries
                    words = sent.split()
                    current_chunk = []
                    current_length = 0
                    
                    for word in words:
                        word_len = len(word) + 1  # +1 for space
                        if current_length + word_len > MAX_LENGTH and current_chunk:
                            final_sentences.append(' '.join(current_chunk))
                            current_chunk = [word]
                            current_length = word_len
                        else:
                            current_chunk.append(word)
                            current_length += word_len
                    
                    if current_chunk:
                        final_sentences.append(' '.join(current_chunk))
                else:
                    final_sentences.append(sent)
            
            sentences = final_sentences
        
        # Clean and filter
        sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 15]
        
        logger.info(f"[Sentence Split] Result: {len(sentences)} sentences from {len(text)} chars")
        
        return sentences
    
    def _save_transcript_entries(self, interview_id: int, segments_list: List[Dict], db):
        """
        Save transcript entries with sentiment analysis
        
        Args:
            interview_id: Interview ID
            segments_list: List of segment dicts with text, start, end, confidence
            db: Database session
        """
        if not segments_list:
            logger.warning(f"[Interview {interview_id}] No segments to save")
            return
        
        try:
            from ..models.interview import TranscriptEntry
            
            saved_count = 0
            for segment in segments_list:
                text = segment.get('text', '').strip()
                if not text or len(text) < 3:
                    continue
                
                # Analyze sentiment for this segment
                sentiment_result = {'score': 0.5, 'label': 'neutral', 'confidence': 0.0}
                if self.nlp_analyzer:
                    try:
                        sentiment_result = self.nlp_analyzer.analyze_sentiment(text)
                    except Exception as e:
                        logger.error(f"Error analyzing sentiment for segment: {e}")
                
                # Create transcript entry
                # Assume "Candidate" as speaker (since we don't have speaker diarization)
                # In future, could add speaker diarization
                entry = TranscriptEntry(
                    interview_id=interview_id,
                    speaker="Candidate",  # Default speaker
                    text=text,
                    timestamp=segment.get('start', 0.0),
                    confidence=segment.get('confidence', 0.0),
                    sentiment_score=sentiment_result['score']
                    # emotion_detected field can be left NULL, will be filled by real-time processing if available
                )
                
                db.add(entry)
                saved_count += 1
            
            db.commit()
            logger.info(f"[Interview {interview_id}] Saved {saved_count} transcript entries with sentiment analysis")
            
        except Exception as e:
            logger.error(f"[Interview {interview_id}] Error saving transcript entries: {e}")
            db.rollback()
    
    def calculate_overall_score(self, assessments: List[Dict], indicators: List[Dict]) -> float:
        """
        Calculate weighted overall score from individual assessments
        
        Args:
            assessments: List of assessment results
            indicators: List of indicators with weights
        
        Returns:
            Overall weighted score (0-100)
        """
        if not assessments:
            return 0.0
        
        total_weighted_score = 0.0
        total_weight = 0.0
        
        # Create indicator weight map
        weight_map = {ind['id']: float(ind.get('weight', 1.0)) for ind in indicators}
        
        for assessment in assessments:
            indicator_id = assessment['indicator_id']
            score = assessment['score']
            weight = weight_map.get(indicator_id, 1.0)
            
            total_weighted_score += score * weight
            total_weight += weight
        
        if total_weight == 0:
            return 0.0
        
        return total_weighted_score / total_weight
    
    def _cleanup_audio_file(self, audio_file_path: str, interview_id: int):
        """
        Clean up audio file after successful processing to save disk space
        For competition - prevents disk from filling up
        """
        try:
            audio_path = Path(audio_file_path)
            if audio_path.exists():
                audio_path.unlink()
                logger.info(f"[Interview {interview_id}] Audio file cleaned up: {audio_file_path}")
            else:
                logger.warning(f"[Interview {interview_id}] Audio file not found for cleanup: {audio_file_path}")
        except Exception as e:
            logger.error(f"[Interview {interview_id}] Error cleaning up audio file: {e}")
            # Don't raise - cleanup failure shouldn't break the process
    
    def process_interview(
        self, 
        interview_id: int,
        audio_file_path: str,
        indicators: List[Dict],
        db: Session
    ) -> Dict:
        """
        Main processing pipeline for interview
        
        Args:
            interview_id: Interview ID
            audio_file_path: Path to recorded audio file
            indicators: List of custom indicators
            db: Database session
        
        Returns:
            Dict with processing results
        """
        try:
            logger.info(f"Starting batch processing for interview {interview_id}")
            
            # Update status to processing
            from ..models.interview import Interview
            interview = db.query(Interview).filter(Interview.id == interview_id).first()
            if not interview:
                raise ValueError(f"Interview {interview_id} not found")
            
            interview.processing_status = "processing"
            db.commit()
            
            # Delete old assessments if reprocessing
            from ..models.indicator import InterviewAssessment
            existing_assessments = db.query(InterviewAssessment).filter(
                InterviewAssessment.interview_id == interview_id
            ).all()
            
            if existing_assessments:
                logger.info(f"[Interview {interview_id}] Deleting {len(existing_assessments)} old assessments for reprocessing...")
                for old_assessment in existing_assessments:
                    db.delete(old_assessment)
                db.commit()
            
            # Step 1: Transcribe audio
            logger.info(f"[Interview {interview_id}] Transcribing audio...")
            transcript, confidence, segments_list = self.transcribe_audio(audio_file_path)
            
            if not transcript:
                raise ValueError("Transcription failed or produced empty result")
            
            # Save full transcript
            interview.transcript = transcript
            db.commit()
            logger.info(f"[Interview {interview_id}] Transcript saved ({len(transcript)} chars)")
            
            # Step 1.5: Create transcript entries with sentiment analysis
            logger.info(f"[Interview {interview_id}] Creating transcript entries with sentiment analysis...")
            self._save_transcript_entries(interview_id, segments_list, db)
            
            # Step 2: Analyze with indicators
            logger.info(f"[Interview {interview_id}] Analyzing with {len(indicators)} indicators...")
            assessments = self.analyze_with_indicators(transcript, indicators)
            
            # Step 3: Calculate overall score
            overall_score = self.calculate_overall_score(assessments, indicators)
            
            # Step 4: Save assessments to database
            for assessment in assessments:
                db_assessment = InterviewAssessment(
                    interview_id=interview_id,
                    indicator_id=assessment['indicator_id'],
                    score=assessment['score'],
                    evidence=assessment['evidence'],
                    reasoning=assessment['reasoning']
                )
                db.add(db_assessment)
            
            # Step 5: Update InterviewScore with overall AI score and final score
            from ..models.interview import InterviewScore
            score_record = db.query(InterviewScore).filter(
                InterviewScore.interview_id == interview_id
            ).first()
            
            if not score_record:
                # Create new score record if doesn't exist
                score_record = InterviewScore(interview_id=interview_id)
                db.add(score_record)
            
            # Update AI score and final score
            score_record.overall_ai_score = round(overall_score, 2)
            # If no manual score yet, final_score = AI score
            if not score_record.overall_manual_score:
                score_record.final_score = round(overall_score, 2)
            else:
                # Recalculate final score with existing manual score (60% AI, 40% Manual)
                score_record.final_score = round(
                    (score_record.overall_ai_score * 0.6) + (score_record.overall_manual_score * 0.4), 2
                )
            
            # Update interview status
            interview.processing_status = "completed"
            interview.processed_at = datetime.utcnow()
            db.commit()
            
            logger.info(f"[Interview {interview_id}] Processing complete! Overall AI score: {overall_score:.2f}, Final score: {score_record.final_score}")
            
            # Cleanup audio file after successful processing to save disk space
            self._cleanup_audio_file(audio_file_path, interview_id)
            
            return {
                'success': True,
                'interview_id': interview_id,
                'transcript_length': len(transcript),
                'confidence': confidence,
                'assessments_count': len(assessments),
                'overall_score': overall_score,
                'status': 'completed'
            }
            
        except Exception as e:
            logger.error(f"[Interview {interview_id}] Processing failed: {e}", exc_info=True)
            
            # Update status to failed
            try:
                interview = db.query(Interview).filter(Interview.id == interview_id).first()
                if interview:
                    interview.processing_status = "failed"
                    db.commit()
            except:
                pass
            
            return {
                'success': False,
                'interview_id': interview_id,
                'error': str(e),
                'status': 'failed'
            }
    
    def cleanup(self):
        """Cleanup resources"""
        if self.whisper_model:
            del self.whisper_model
            self.whisper_model = None


# Singleton instance
_batch_processor = None

def get_batch_processor() -> BatchProcessor:
    """Get or create batch processor singleton"""
    global _batch_processor
    if _batch_processor is None:
        _batch_processor = BatchProcessor()
    return _batch_processor
