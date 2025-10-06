import argparse
import json
import os
import re
from collections import Counter
import heapq

# %h - - %t "%r" %s %b "%{Referer}" "%{User-Agent}" %d
LOG_RE = re.compile(
    r'^(?P<ip>\S+)\s+-\s+-\s+\[(?P<date>[^\]]+)\]\s+'
    r'"(?P<method>GET|POST|PUT|DELETE|OPTIONS|HEAD)\s+(?P<url>\S+)\s+HTTP/\d\.\d"\s+'
    r'(?P<status>\d{3})\s+(?P<size>\S+)\s+"(?P<referer>[^"]*)"\s+"(?P<agent>[^"]*)"\s+'
    r'(?P<duration>\d+)\s*$'
)

ALL_METHODS = ("GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD")


def analyze_log(file_path: str) -> dict:
    total = 0
    by_method = Counter({m: 0 for m in ALL_METHODS})
    by_ip = Counter()
    # heap для топ-3: (duration, idx, payload)
    top3 = []
    idx = 0

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            m = LOG_RE.match(line)
            if not m:
                continue

            gd = m.groupdict()
            duration = int(gd["duration"])

            total += 1
            by_method[gd["method"]] += 1
            by_ip[gd["ip"]] += 1

            payload = {
                "ip": gd["ip"],
                "date": f'[{gd["date"]}]',
                "method": gd["method"],
                "url": gd["url"],
                "duration": duration,
            }

            if len(top3) < 3:
                heapq.heappush(top3, (duration, idx, payload))
            else:
                if duration > top3[0][0]:
                    heapq.heapreplace(top3, (duration, idx, payload))
            idx += 1

    top_longest = [p for _, _, p in sorted(top3, key=lambda t: t[0], reverse=True)]

    return {
        "top_ips": dict(by_ip.most_common(3)),
        "top_longest": top_longest,
        "total_stat": {m: by_method[m] for m in ALL_METHODS},
        "total_requests": total,
    }


def process_path(path: str):
    if os.path.isfile(path):
        files = [path]
    elif os.path.isdir(path):
        files = [os.path.join(path, name) for name in os.listdir(path) if name.endswith(".log")]
    else:
        raise FileNotFoundError(f"Путь не найден: {path}")

    for fp in files:
        stats = analyze_log(fp)
        out_name = f"result_{os.path.splitext(os.path.basename(fp))[0]}.json"
        with open(out_name, "w", encoding="utf-8") as w:
            json.dump(stats, w, ensure_ascii=False, indent=2)
        print(f"\n===== LOG FILE: {fp} =====")
        print(json.dumps(stats, ensure_ascii=False, indent=2))
        print(f"Сохранено: {out_name}")


def main():
    ap = argparse.ArgumentParser(description="Access.log analyzer")
    ap.add_argument("-l", "--log", required=True, help="Путь к лог-файлу или директории")
    args = ap.parse_args()
    process_path(args.log)


if __name__ == "__main__":
    main()
