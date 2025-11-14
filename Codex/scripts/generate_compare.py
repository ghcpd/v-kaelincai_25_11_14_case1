import argparse
import json
from pathlib import Path
from textwrap import dedent


def load_json(path: Path):
    if not path.exists():
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


def format_case(pre_case, post_case):
    lines = []
    lines.append(f"### {post_case['id']}")
    lines.append("")
    lines.append("| Metric | Baseline | Enhanced |")
    lines.append("|--------|----------|----------|")
    lines.append(
        f"| Time to first frame (ms) | "
        f"{pre_case['metrics'].get('timeToFirstFrameMs', 'n/a')} | "
        f"{post_case['time_to_first_frame_ms']:.1f} |"
    )
    lines.append(
        f"| Resume error (s) | {pre_case['metrics'].get('resume_error_s', 'n/a')} | "
        f"{post_case['resume_error_s']:.2f} |"
    )
    lines.append(
        f"| Quality | baseline static | {post_case.get('quality', 'n/a')} |"
    )
    lines.append(
        f"| Screenshot | ![]({pre_case['metrics'].get('screenshot','')}) | "
        f"![]({post_case.get('screenshot','')}) |"
    )
    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate comparison report.")
    parser.add_argument("--pre", required=True, type=Path)
    parser.add_argument("--post", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    pre = load_json(args.pre)
    post = load_json(args.post)

    body = [
        "# Enhanced Course Playback Comparison",
        "",
        "## Summary",
        f"- Avg baseline TTF: {pre['avg_time_to_first_frame_ms']:.1f} ms",
        f"- Avg enhanced TTF: {post['avg_time_to_first_frame_ms']:.1f} ms",
        f"- Avg enhanced stall: {post.get('avg_stall_ms', 0):.1f} ms",
        "",
        "## Detailed Cases",
    ]

    pre_cases = {case["id"]: case for case in pre["cases"]}
    for case in post["cases"]:
        pre_case = pre_cases.get(case["id"], {"metrics": {}})
        body.append(format_case(pre_case, case))

    args.out.write_text("\n".join(body), encoding="utf-8")


if __name__ == "__main__":
    main()
