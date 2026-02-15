from finance_report_assistant.processing.tokenizer_eval import evaluate_tokenizer_metrics


def test_evaluate_tokenizer_metrics_returns_expected_fields() -> None:
    texts = ["alpha beta beta", "gamma delta"]
    metrics = evaluate_tokenizer_metrics(texts, rare_threshold=1)

    assert metrics["num_chunks"] == 2
    assert metrics["total_tokens"] == 5
    assert metrics["unique_tokens"] == 4
    assert 0 <= metrics["rare_token_ratio"] <= 1
