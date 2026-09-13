from app.messages import MESSAGES, message


def test_known_messages_have_english_and_spanish_translations():
    assert all(set(value) == {'en', 'es'} for value in MESSAGES.values())
    assert message('quota_exhausted', 'es-MX,es;q=0.9') == 'Cuota agotada'
    assert message('quota_exhausted') == 'Quota exhausted'
