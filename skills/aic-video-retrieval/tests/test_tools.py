import contextlib
import copy
import csv
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from aic_client import request_json
from export_submission import build_rows, main, read_map


class SubmissionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "L00_V000.csv").write_text(
            "id,frame_idx,pts_time,fps\n0,0,0,25\n12,3450,138,25\n13,3500,140,25\n14,3600,144,25\n",
            encoding="utf-8-sig",
        )
        self.doc = {
            "query_id": "query-test-kis", "type": "kis",
            "candidates": [{"video_name": "folder\\L00_V000.mp4", "keyframe_ids": [12],
                            "verified": True, "evidence": ["Viewed test image"]}],
        }

    def test_maps_keyframe_to_original_frame_and_preserves_zero(self):
        self.assertEqual(build_rows(self.doc, self.root), [["L00_V000", 3450]])
        self.doc["candidates"][0]["keyframe_ids"] = [0]
        self.assertEqual(build_rows(self.doc, self.root), [["L00_V000", 0]])

    def test_never_falls_back_for_missing_map_or_id(self):
        with self.assertRaises(ValueError):
            build_rows(self.doc)
        self.doc["candidates"][0]["keyframe_ids"] = [99]
        with self.assertRaises(ValueError):
            build_rows(self.doc, self.root)

    def test_qa_csv_roundtrip_and_refuses_overwrite(self):
        self.doc.update(query_id="query-test-qa", type="qa")
        answer = 'Màu đỏ, có chữ "A"'
        self.doc["candidates"][0]["answer"] = answer
        source = self.root / "reviewed.json"
        source.write_text(json.dumps(self.doc, ensure_ascii=False), encoding="utf-8")
        args = [str(source), "--map-dir", str(self.root), "--output-dir", str(self.root / "out")]
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(main(args), 0)
            self.assertEqual(main(args), 1)
        with (self.root / "out/query-test-qa.csv").open(encoding="utf-8", newline="") as stream:
            self.assertEqual(list(csv.reader(stream)), [["L00_V000", "3450", answer]])

    def test_answer_length_and_newline_validation(self):
        self.doc.update(query_id="query-test-qa", type="qa")
        for answer in ("", "a" * 101, "two\nlines", 5):
            with self.subTest(answer=answer), self.assertRaises(ValueError):
                self.doc["candidates"][0]["answer"] = answer
                build_rows(self.doc, self.root)
        self.doc["candidates"][0]["answer"] = "a" * 100
        self.assertEqual(len(build_rows(self.doc, self.root)[0][-1]), 100)

    def test_trake_count_and_semantic_event_order_are_not_repaired(self):
        self.doc.update(query_id="query-test-trake", type="trake", event_count=3)
        for ids in ([12, 13], [13, 12, 14], [12, 12, 14]):
            with self.subTest(ids=ids), self.assertRaises(ValueError):
                self.doc["candidates"][0]["keyframe_ids"] = ids
                build_rows(self.doc, self.root)
        self.doc["candidates"][0]["keyframe_ids"] = [12, 13, 14]
        self.assertEqual(build_rows(self.doc, self.root), [["L00_V000", 3450, 3500, 3600]])

    def test_requires_evidence_and_review(self):
        for change in ({"verified": False}, {"evidence": []}, {"evidence": [""]}):
            doc = copy.deepcopy(self.doc)
            doc["candidates"][0].update(change)
            with self.subTest(change=change), self.assertRaises(ValueError):
                build_rows(doc, self.root)

    def test_duplicate_and_excess_rows(self):
        self.doc["candidates"] *= 2
        with self.assertRaises(ValueError):
            build_rows(self.doc, self.root)
        self.doc["candidates"] *= 51
        with self.assertRaises(ValueError):
            build_rows(self.doc, self.root)

    def test_explicit_video_frames_need_provenance(self):
        candidate = self.doc["candidates"][0]
        del candidate["keyframe_ids"]
        candidate["frame_indices"] = [3451]
        with self.assertRaises(ValueError):
            build_rows(self.doc)
        candidate["frame_source"] = "Verified original video frame sequence"
        self.assertEqual(build_rows(self.doc), [["L00_V000", 3451]])

    def test_rejects_ambiguous_or_duplicate_map(self):
        path = self.root / "ambiguous.csv"
        path.write_text("id,n,frame_idx\n0,1,200\n", encoding="utf-8")
        with self.assertRaises(ValueError):
            read_map(path)
        self.assertEqual(read_map(path, "n"), {1: 200})
        path.write_text("id,frame_idx\n0,0\n0,10\n", encoding="utf-8")
        with self.assertRaises(ValueError):
            read_map(path)

    def test_rejects_invalid_frames_and_filename_traversal(self):
        for value in (-1, 1.5, True, None):
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.doc["candidates"][0]["keyframe_ids"] = [value]
                build_rows(self.doc, self.root)
        self.doc["query_id"] = "../query-test-kis"
        with self.assertRaises(ValueError):
            build_rows(self.doc, self.root)


class ClientTests(unittest.TestCase):
    def test_rejects_unsafe_or_non_http_base_before_network(self):
        for url in ("file:///tmp/anything", "http://user:password@localhost", "http://localhost?token=abc"):
            with self.subTest(url=url), self.assertRaises(ValueError):
                request_json(url, "/openapi.json")


if __name__ == "__main__":
    unittest.main()
