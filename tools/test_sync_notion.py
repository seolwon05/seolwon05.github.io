import unittest

from sync_notion import SyncError, collect_notes, extract_frontmatter, inline, liquid_arg, render_blocks, render_callout, render_table


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

    def test_plain_markdown_example_stays_literal(self):
        self.assertEqual(inline([rich("![이미지설명](이미지 주소)")], {}, set()),
                         "<span>&#33;&#91;이미지설명&#93;&#40;이미지 주소&#41;</span>")

    def test_notion_frontmatter_paragraphs(self):
        blocks = [{"type": "divider"}]
        blocks += [{"type": "paragraph", "paragraph": {"rich_text": [rich(text)]}}
                   for text in ("title: 테스트", "date: 2026-11-24 13:53:00 +0900",
                                "categories: Development", "tags: programming")]
        blocks.append({"type": "heading_1", "heading_1": {"rich_text": [rich("본문")]}})
        metadata, body = extract_frontmatter(blocks)
        self.assertEqual(metadata["title"], "테스트")
        self.assertEqual(len(body), 1)
        self.assertEqual(body[0]["type"], "heading_1")

    def test_table_headers_and_cells(self):
        rows = [{"type": "table_row", "table_row": {"cells": [[rich(value)] for value in values]}}
                for values in (("구분", "설명"), ("테이블", "표가 올라갑니다"))]
        markup = render_table({"table_width": 2, "has_column_header": True,
                               "has_row_header": True}, rows, {}, set())
        self.assertIn('<th scope="col"><span>구분</span></th>', markup)
        self.assertIn('<th scope="row"><span>테이블</span></th>', markup)
        self.assertIn('<td><span>표가 올라갑니다</span></td>', markup)

    def test_table_width_mismatch_fails(self):
        with self.assertRaises(SyncError):
            render_table({"table_width": 2},
                         [{"type": "table_row", "table_row": {"cells": [[rich("하나")]]}}], {}, set())

    def test_link_and_background_color(self):
        linked = rich("원하는 영역", color="yellow_background")
        linked["href"] = "https://example.com/page"
        markup = inline([linked], {}, set())
        self.assertIn('href="https://example.com/page"', markup)
        self.assertIn('class="notion-color-yellow_background"', markup)

    def test_empty_paragraph_and_toggle(self):
        blocks = [
            {"type": "paragraph", "paragraph": {"rich_text": []}},
            {"type": "toggle", "id": "toggle", "has_children": False,
             "toggle": {"rich_text": [rich("자세히")]}},
        ]
        markup = render_blocks(blocks, "token", "page", {}, set(), True)
        self.assertIn('class="notion-spacer"', markup)
        self.assertIn("<summary><span>자세히</span></summary>", markup)

    def test_callout_title_and_body_separator(self):
        block = {"type": "callout", "id": "callout", "has_children": False,
                 "callout": {"rich_text": [rich("제목\n---\n내용") ]}}
        markup = render_callout(block, "token", "page", {}, set(), True, 0)
        self.assertIn('class="case-callout-title"><span>제목</span>', markup)
        self.assertIn("<p>내용</p>", markup)
        self.assertNotIn("<hr", markup)


if __name__ == "__main__":
    unittest.main()
