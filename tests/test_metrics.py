from api.metrics import get_system_metrics


def test_metrics_keys():
    """Vérifie que les clés attendues sont présentes."""
    metrics = get_system_metrics()
    assert "cpu_percent" in metrics
    assert "memory_percent" in metrics
    assert "disk_percent" in metrics


def test_metrics_values_range():
    """Vérifie que les valeurs sont entre 0 et 100."""
    metrics = get_system_metrics()
    assert 0 <= metrics["cpu_percent"] <= 100
    assert 0 <= metrics["memory_percent"] <= 100
    assert 0 <= metrics["disk_percent"] <= 100