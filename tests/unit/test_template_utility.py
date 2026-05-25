from types import SimpleNamespace

from game.templatetags.utility import obj_exists


def test_obj_exists_returns_false_for_removed_content_type_model():
    log_entry = SimpleNamespace(
        content_type=SimpleNamespace(model_class=lambda: None),
        object_id="missing",
    )

    assert obj_exists(log_entry) is False
