"""Small AIC_BE JSON client. Preserves backend responses and never submits answers."""
import argparse
import json
import os
from pathlib import Path
import sys
import urllib.error
import urllib.parse
import urllib.request


OPERATIONS = {
    "semantic": "/search",
    "fuse": "/fuse_search",
    "temporal": "/temporal_search",
    "ocr": "/search_OCR",
    "asr": "/search_ASR",
    "conversation": "/search_cir",
    "similar": "/search_by_frame",
    "agent-retrieval": "/agent_retrieval",
    "translate": "/translate",
}


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        # Avoid forwarding configured bearer credentials to another server.
        return None


def request_json(base_url, path, payload=None, timeout=90):
    parts = urllib.parse.urlsplit(base_url)
    if parts.scheme not in ("http", "https") or not parts.netloc:
        raise ValueError("AIC_API_BASE_URL must be an absolute http(s) URL")
    if parts.username or parts.password or parts.query or parts.fragment:
        raise ValueError("Use a base URL without credentials, query, or fragment")
    if timeout <= 0:
        raise ValueError("timeout must be positive")
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    token = os.environ.get("AIC_API_TOKEN")
    if token:
        headers["Authorization"] = "Bearer " + token
    data = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(base_url.rstrip("/") + path, data=data, headers=headers)
    try:
        with urllib.request.build_opener(NoRedirect()).open(req, timeout=timeout) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        detail = exc.read(4096).decode("utf-8", errors="replace")
        raise RuntimeError(f"AIC_BE HTTP {exc.code}: {detail}") from None
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Cannot reach AIC_BE: {exc.reason}") from None


def inspect_api(base_url, timeout):
    spec = request_json(base_url, "/openapi.json", timeout=timeout)
    paths = spec.get("paths", {})
    operations = {name: "post" in paths.get(path, {}) for name, path in OPERATIONS.items()}
    return {
        "title": spec.get("info", {}).get("title"),
        "operations": operations,
        "missing": [name for name, available in operations.items() if not available],
        "paths": sorted(paths),
        "note": "Route presence only; run a small query to check loaded models/indices. VQA requires inspecting media.",
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=["doctor", "openapi", *OPERATIONS])
    parser.add_argument("--base-url", default=os.environ.get("AIC_API_BASE_URL", "http://127.0.0.1:8000"))
    parser.add_argument("--payload", type=Path, help="UTF-8 JSON file (or omit and pass JSON on stdin)")
    parser.add_argument("--output", type=Path, help="Save full JSON response")
    parser.add_argument("--timeout", type=float, default=90)
    args = parser.parse_args(argv)
    try:
        if args.operation == "doctor":
            result = inspect_api(args.base_url, args.timeout)
        elif args.operation == "openapi":
            result = request_json(args.base_url, "/openapi.json", timeout=args.timeout)
        else:
            if not args.payload and sys.stdin.isatty():
                parser.error("provide --payload or pipe a JSON object on stdin")
            raw = args.payload.read_text(encoding="utf-8-sig") if args.payload else sys.stdin.read()
            payload = json.loads(raw)
            if not isinstance(payload, dict):
                raise ValueError("payload must be a JSON object")
            result = request_json(args.base_url, OPERATIONS[args.operation], payload, args.timeout)
        output = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(output, encoding="utf-8")
            print(f"Saved {args.output}")
        else:
            print(output, end="")
        return 1 if args.operation == "doctor" and result["missing"] else 0
    except (ValueError, OSError, RuntimeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    raise SystemExit(main())
