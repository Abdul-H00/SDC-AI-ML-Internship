"""
Runs the AI Website Quality Auditor on 3 public furniture retail homepages
and writes a structured Markdown report (audit_report.md).

Sites chosen: three large, publicly accessible furniture retailer homepages,
picked to give a realistic score range (a well-resourced global brand, a
large online-only retailer, and a regional retailer) so the AI judgment
step has something meaningful to differentiate.
"""

import json
from website_auditor import audit_websites

FURNITURE_URLS = [
    "https://www.ashleyfurniture.com",
    "https://www.wayfair.com",
    "https://interwood.pk",
]

# A couple of deliberately bad inputs to demonstrate error handling
BAD_INPUTS = [
    "not-a-real-url",
    "",
]


def render_report(results: list[dict]) -> str:
    lines = ["# Website Quality Audit Report — Furniture Retailers\n"]
    lines.append("| Website | Score | Priority |")
    lines.append("|---|---|---|")
    for r in results:
        if "error" in r:
            lines.append(f"| {r.get('url', 'N/A')} | ERROR | - |")
        else:
            lines.append(f"| {r['url']} | {r['ai_judgment']['professionalism_score']}/100 | {r['ai_judgment']['priority']} |")
    lines.append("")

    for r in results:
        lines.append(f"\n---\n## {r.get('url', 'Unknown URL')}\n")
        if "error" in r:
            lines.append(f"**Error:** {r['error']}\n")
            continue

        lines.append(f"*Fetched via: {r['fetch_source']} | AI judgment mode: {r['judgment_mode']}*\n")

        lines.append("### Facts Detected (automated, no AI opinion)")
        for k, v in r["facts_detected"].items():
            if k == "url":
                continue
            lines.append(f"- **{k}**: {v}")

        j = r["ai_judgment"]
        lines.append("\n### AI-Generated Judgment (opinion, not fact)")
        lines.append(f"- **Score**: {j['professionalism_score']}/100")
        lines.append(f"- **Priority**: {j['priority']}")
        lines.append("- **Problems:**")
        for p in j["problems"]:
            lines.append(f"  - {p}")
        lines.append("- **Missing Features:**")
        for m in j["missing_features"]:
            lines.append(f"  - {m}")
        lines.append("- **Recommendations:**")
        for rec in j["recommendations"]:
            lines.append(f"  - {rec}")

    return "\n".join(lines)


def run():
    print("=== Running audit on furniture websites ===\n")
    results = audit_websites(FURNITURE_URLS)
    for r in results:
        print(json.dumps(r, indent=2))
        print()

    print("\n=== Testing error handling with bad inputs ===\n")
    bad_results = audit_websites(BAD_INPUTS)
    for r in bad_results:
        print(json.dumps(r, indent=2))
        print()

    report_md = render_report(results)
    with open("audit_report.md", "w") as f:
        f.write(report_md)
    print("Saved full report to audit_report.md")


if __name__ == "__main__":
    run()
