import unittest

from app import answer_payload


class AppTest(unittest.TestCase):
    def test_api_payload_returns_grounded_answer(self):
        result = answer_payload({"question": "Where did you go to college?"})
        self.assertIn("University of Washington", result["answer"])
        self.assertGreaterEqual(len(result["evidence"]), 1)
        self.assertEqual(result["profile"], "mirror/data/sample/crosleythomas_linkedin.txt")

    def test_api_payload_rejects_blank_question(self):
        with self.assertRaisesRegex(ValueError, "Enter a question"):
            answer_payload({"question": "   "})


if __name__ == "__main__":
    unittest.main()
