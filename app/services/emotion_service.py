from typing import Dict, List, Optional
from deepface import DeepFace
import numpy as np
from PIL import Image
import io
from app.utils.logger import logger

class EmotionService:
    """Duygu analizi servisi."""

    def analyze_emotion(self, image_data: bytes) -> Optional[Dict]:
        """Görüntüdeki yüzün duygusunu analiz et."""
        try:
            # Görüntüyü yükle
            image = Image.open(io.BytesIO(image_data))
            
            # DeepFace ile analiz
            result = DeepFace.analyze(
                np.array(image),
                actions=['emotion'],
                enforce_detection=False
            )
            
            if not result:
                return None
            
            # Sonuçları formatla
            emotions = result[0]['emotion']
            dominant_emotion = max(emotions.items(), key=lambda x: x[1])
            
            return {
                'dominant_emotion': dominant_emotion[0],
                'emotions': emotions,
                'confidence': dominant_emotion[1] / 100
            }
        except Exception as e:
            logger.error(f"Duygu analizi hatası: {str(e)}")
            return None

    def analyze_emotions_batch(self, face_images: List[bytes]) -> List[Dict]:
        """Birden fazla yüz görüntüsünü analiz et."""
        results = []
        for image_data in face_images:
            result = self.analyze_emotion(image_data)
            if result:
                results.append(result)
        return results

    def calculate_emotion_stats(self, emotions: List[Dict]) -> Dict:
        """Duygu istatistiklerini hesapla."""
        if not emotions:
            return {
                'total_analyzed': 0,
                'stats': {},
                'percentages': {}
            }
        
        # Duygu sayılarını hesapla
        stats = {}
        total = len(emotions)
        
        for emotion in emotions:
            dominant = emotion['dominant_emotion']
            stats[dominant] = stats.get(dominant, 0) + 1
        
        # Yüzdeleri hesapla
        percentages = {
            emotion: (count / total) * 100
            for emotion, count in stats.items()
        }
        
        return {
            'total_analyzed': total,
            'stats': stats,
            'percentages': percentages
        } 