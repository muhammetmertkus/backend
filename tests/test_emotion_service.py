import pytest
from app.services.emotion_service import EmotionService

@pytest.fixture
def emotion_service():
    """Emotion service fixture."""
    return EmotionService()

def test_analyze_emotion(emotion_service, test_image):
    """Duygu analizi testi."""
    result = emotion_service.analyze_emotion(test_image)
    if result:
        assert 'dominant_emotion' in result
        assert 'emotions' in result
        assert 'confidence' in result
        assert 0 <= result['confidence'] <= 1

def test_analyze_emotions_batch(emotion_service):
    """Toplu duygu analizi testi."""
    faces = [b'test_image_data'] * 3  # Test için dummy veri
    results = emotion_service.analyze_emotions_batch(faces)
    assert isinstance(results, list)

def test_calculate_emotion_stats(emotion_service):
    """Duygu istatistikleri hesaplama testi."""
    emotions = [
        {'dominant_emotion': 'happy'},
        {'dominant_emotion': 'happy'},
        {'dominant_emotion': 'neutral'},
        {'dominant_emotion': 'sad'}
    ]
    
    stats = emotion_service.calculate_emotion_stats(emotions)
    assert 'total_analyzed' in stats
    assert 'stats' in stats
    assert 'percentages' in stats
    assert stats['total_analyzed'] == 4
    assert stats['stats']['happy'] == 2
    assert stats['stats']['neutral'] == 1
    assert stats['stats']['sad'] == 1 