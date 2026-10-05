from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class BilingualDocumentationTests(unittest.TestCase):
    def test_public_markdown_has_chinese_counterpart_and_language_switchers(self):
        english_docs = sorted(
            path
            for path in ROOT.rglob("*.md")
            if not path.name.endswith(".zh-CN.md")
            and ".git" not in path.parts
        )

        self.assertTrue(english_docs)

        missing: list[str] = []
        bad_switchers: list[str] = []

        for english in english_docs:
            chinese = english.with_name(
                english.name.removesuffix(".md") + ".zh-CN.md"
            )
            if not chinese.exists():
                missing.append(str(english.relative_to(ROOT)))
                continue

            english_text = english.read_text(encoding="utf-8")
            chinese_text = chinese.read_text(encoding="utf-8")

            english_nav = (
                f"> English | [简体中文]({chinese.name})"
            )
            chinese_nav = (
                f"> [English]({english.name}) | 简体中文"
            )

            if english_nav not in english_text:
                bad_switchers.append(
                    f"{english.relative_to(ROOT)} missing English->Chinese switcher"
                )
            if chinese_nav not in chinese_text:
                bad_switchers.append(
                    f"{chinese.relative_to(ROOT)} missing Chinese->English switcher"
                )

        self.assertEqual(missing, [], f"missing Chinese docs: {missing}")
        self.assertEqual(
            bad_switchers,
            [],
            f"invalid bilingual navigation: {bad_switchers}",
        )


if __name__ == "__main__":
    unittest.main()
