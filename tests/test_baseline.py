import tempfile
import unittest
from pathlib import Path

from baseline import answer_question


class BaselineTest(unittest.TestCase):
    def test_education_question_is_grounded(self):
        with tempfile.TemporaryDirectory() as directory:
            profile = Path(directory) / "profile.txt"
            profile.write_text(
                "Education\nUniversity of Washington\nBachelor of Science, Computer Science\n",
                encoding="utf-8",
            )
            result = answer_question("Where did you go to college?", profile)

        self.assertEqual(result["answer"], "I studied at University of Washington.")
        self.assertEqual(result["evidence"], ["University of Washington"])


if __name__ == "__main__":
    unittest.main()
