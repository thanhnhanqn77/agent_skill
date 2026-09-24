"""Export reviewed AIC candidates, resolving keyframe IDs through explicit CSV maps."""
import argparse
import csv
import io
import json
from pathlib import Path
import re
import sys
import unicodedata


def integer(value, label):
    if isinstance(value, bool) or not re.fullmatch(r"[0-9]+", str(value)):
        raise ValueError(f"{label} must be a nonnegative integer: {value!r}")
    return int(value)


def video_name(value):
    name = str(value).replace("\\", "/").split("/")[-1]
    name = re.sub(r"\.mp4$", "", name, flags=re.I)
    if not re.fullmatch(r"L\d+_V\d+", name):
        raise ValueError(f"Invalid AIC video name: {value!r}")
    return name


def read_map(path, id_column=None):
    with Path(path).open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        columns = [(c or "").strip().lower() for c in reader.fieldnames or []]
        if len(set(columns)) != len(columns):
            raise ValueError(f"Duplicate map headers: {path}")
        reader.fieldnames = columns
        ids = [id_column.lower()] if id_column else [c for c in ("keyframe_id", "keyframeid", "id", "n") if c in columns]
        frames = [c for c in ("frame_idx", "frameidx", "frame_id") if c in columns]
        if len(ids) != 1 or ids[0] not in columns or len(frames) != 1:
            raise ValueError(f"Map needs an unambiguous ID column and frame_idx: {path}; use --map-id-column if needed")
        result = {}
        for row in reader:
            kid = integer((row.get(ids[0]) or "").strip(), "map keyframe")
            fid = integer((row.get(frames[0]) or "").strip(), "map frame_idx")
            if kid in result:
                raise ValueError(f"Duplicate keyframe {kid} in {path}")
            result[kid] = fid
        if not result:
            raise ValueError(f"Empty map: {path}")
        return result


def build_rows(document, map_dir=None, id_column=None):
    kind = str(document.get("type", "")).lower()
    if kind not in ("kis", "qa", "trake"):
        raise ValueError("type must be kis, qa, or trake")
    query_id = document.get("query_id", "")
    if not isinstance(query_id, str) or not re.fullmatch(r"[A-Za-z0-9_-]+", query_id) or not query_id.endswith("-" + kind):
        raise ValueError("query_id must be a filename stem ending in the matching -kis/-qa/-trake")
    expected = integer(document.get("event_count"), "event_count") if kind == "trake" else 1
    if expected < 1:
        raise ValueError("event_count must be positive")
    candidates = document.get("candidates")
    if not isinstance(candidates, list) or not 1 <= len(candidates) <= 100:
        raise ValueError("Supply 1..100 reviewed candidates; do not pad or silently truncate")
    cache, rows, seen = {}, [], set()
    for candidate in candidates:
        if not isinstance(candidate, dict):
            raise ValueError("Each candidate must be an object")
        evidence = candidate.get("evidence")
        if candidate.get("verified") is not True or not isinstance(evidence, list) or not evidence or not all(isinstance(e, str) and e.strip() for e in evidence):
            raise ValueError("Each candidate requires verified=true and nonempty evidence strings")
        vid = video_name(candidate.get("video_name", ""))
        has_keys, has_frames = "keyframe_ids" in candidate, "frame_indices" in candidate
        if has_keys == has_frames:
            raise ValueError("Supply exactly one of keyframe_ids or frame_indices")
        values = candidate["keyframe_ids" if has_keys else "frame_indices"]
        if not isinstance(values, list) or len(values) != expected:
            raise ValueError(f"{vid}: expected exactly {expected} frame(s) in event order")
        values = [integer(v, "frame") for v in values]
        if has_keys:
            if map_dir is None:
                raise ValueError("--map-dir is required for keyframe_ids")
            if vid not in cache:
                cache[vid] = read_map(Path(map_dir) / (vid + ".csv"), id_column)
            try:
                values = [cache[vid][v] for v in values]
            except KeyError as exc:
                raise ValueError(f"Missing keyframe {exc.args[0]} in map for {vid}") from None
        elif not isinstance(candidate.get("frame_source"), str) or not candidate["frame_source"].strip():
            raise ValueError("frame_indices requires frame_source describing verified original-video indexing")
        if kind == "trake" and any(a >= b for a, b in zip(values, values[1:])):
            raise ValueError("TRAKE frames must be strictly chronological; never reorder events to repair a candidate")
        row = [vid, *values]
        if kind == "qa":
            answer = candidate.get("answer")
            if not isinstance(answer, str):
                raise ValueError("QA answer must be a string, including numeric answers")
            answer = unicodedata.normalize("NFC", answer.strip())
            if not 1 <= len(answer) <= 100 or any(ord(c) < 32 for c in answer):
                raise ValueError("QA answer must have 1..100 characters and no control characters")
            row.append(answer)
        if tuple(row) in seen:
            raise ValueError("Duplicate submission row")
        seen.add(tuple(row))
        rows.append(row)
    return rows


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="Reviewed candidates JSON")
    parser.add_argument("--map-dir", type=Path, help="Local folder containing VIDEO.csv maps with headers")
    parser.add_argument("--map-id-column", help="Explicit keyframe column if header is ambiguous")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--force", action="store_true", help="Replace an existing CSV")
    args = parser.parse_args(argv)
    try:
        document = json.loads(args.input.read_text(encoding="utf-8-sig"))
        if not isinstance(document, dict):
            raise ValueError("Input must be a JSON object")
        rows = build_rows(document, args.map_dir, args.map_id_column)
        # Validate everything before creating a file. QA answer strings are always quoted.
        buffer = io.StringIO(newline="")
        writer = csv.writer(buffer, lineterminator="\n", quoting=csv.QUOTE_NONNUMERIC)
        writer.writerows(rows)
        args.output_dir.mkdir(parents=True, exist_ok=True)
        destination = args.output_dir / (document["query_id"] + ".csv")
        with destination.open("w" if args.force else "x", encoding="utf-8", newline="") as stream:
            stream.write(buffer.getvalue())
        print(f"Saved {len(rows)} rows: {destination}")
        return 0
    except (ValueError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    raise SystemExit(main())
