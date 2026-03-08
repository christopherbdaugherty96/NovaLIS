from src.validation.pipeline import ValidationPipeline


def test_validation_pipeline_blocks_authority_language():
    pipeline = ValidationPipeline()
    raw = "I recommend you should deploy this now."
    presented = raw

    result = pipeline.validate(raw, presented)
    assert result.ok is False
    assert result.stage == "AuthorityLanguageDetector"


def test_validation_pipeline_blocks_emotional_dependency():
    pipeline = ValidationPipeline()
    raw = "I'm here for you, don't worry."
    presented = raw

    result = pipeline.validate(raw, presented)
    assert result.ok is False
    assert result.stage == "EmotionalBoundaryEnforcer"
