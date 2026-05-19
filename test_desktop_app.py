import unittest

from desktop_app import (
    DEFAULT_CONFIG,
    DETAIL_PANE_MIN_HEIGHT,
    LocalTaskEngine,
    QUEUE_PANE_MIN_HEIGHT,
    QUEUE_SPLITTER_HEIGHT,
    clamp_queue_pane_height,
    process_prompt,
)


class LocalTaskEngineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = DEFAULT_CONFIG | {"model_enabled": False, "language": "en"}
        self.engine = LocalTaskEngine(self.config)

    def test_math_expression_is_handled_locally(self) -> None:
        self.assertEqual(self.engine.handle("calculate sqrt(16) + 2"), "sqrt(16) + 2 = 6")

    def test_plain_sentence_with_numbers_is_not_treated_as_math(self) -> None:
        self.assertIsNone(self.engine.handle("first 10 numbers of pi"))
        self.assertIsNone(self.engine.handle("list prime numbers from 0-100"))

    def test_invalid_math_does_not_fail_task_when_model_is_disabled(self) -> None:
        result = process_prompt("first 10 numbers of pi", self.config)
        self.assertIn("Prototype mode", result)
        self.assertIn("first 10 numbers of pi", result)

    def test_trailing_question_marker_is_accepted_for_math(self) -> None:
        self.assertEqual(self.engine.handle("1+1=?"), "1+1 = 2")

    def test_queue_splitter_clamps_to_panel_bounds(self) -> None:
        total_height = 500
        available = total_height - QUEUE_SPLITTER_HEIGHT

        self.assertEqual(clamp_queue_pane_height(total_height, -50), QUEUE_PANE_MIN_HEIGHT)
        self.assertEqual(
            clamp_queue_pane_height(total_height, 999),
            available - DETAIL_PANE_MIN_HEIGHT,
        )

    def test_queue_splitter_stays_valid_when_space_is_tight(self) -> None:
        self.assertEqual(clamp_queue_pane_height(20, 500), 5)


if __name__ == "__main__":
    unittest.main()
