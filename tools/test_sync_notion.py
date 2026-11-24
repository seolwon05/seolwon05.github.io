import unittest

from sync_notion import SyncError, collect_notes, inline, liquid_arg


def rich(text, **annotations):
    return {"plain_text": text, "annotations": annotations}


class NotionConversionTests(unittest.TestCase):
    def test_two_terms_and_literal_newlines(self):
        notes, blocks = collect_notes([
            {"type": "paragraph", "paragraph": {"rich_text": [rich("TLS: 실행 흐름\\n추가 설명", italic=True, color="gray")]}},
            {"type": "paragraph", "paragraph": {"rich_text": [rich("카나리: 보호 값", italic=True, color="gray")]}},
        ])
        self.assertEqual(blocks, [])
        used = set()
        result = inline([rich("TLS", underline=True), rich("와 "), rich("카나리", underline=True)], notes, used)
        self.assertIn('text="TLS" note="실행 흐름\\n추가 설명"', result)
        self.assertIn('text="카나리" note="보호 값"', result)
        self.assertEqual(used, {"TLS", "카나리"})
        self.assertNotIn("<u>", result)

    def test_missing_note_fails(self):
        with self.assertRaises(SyncError):
            inline([rich("TLS", underline=True)], {}, set())

    def test_quote_fails_before_liquid_generation(self):
        with self.assertRaises(SyncError):
            liquid_arg('a "quote"')


if __name__ == "__main__":
    unittest.main()
