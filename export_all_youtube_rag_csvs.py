"""Download every jamescalam/youtube-transcriptions row and export RAG-style CSV parts.

Install:  pip install -U datasets
Run:      python export_all_youtube_rag_csvs.py
Optional: python export_all_youtube_rag_csvs.py --rows-per-csv 1000 --zip

All original transcript segments are represented in at least one overlapping chunk.
"""

import argparse
import csv
from collections import defaultdict
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


DATASET = "jamescalam/youtube-transcriptions"
WINDOW = 20   # Source transcript segments per RAG chunk
STRIDE = 4    # Begin the next chunk four source segments later
COLUMNS = ["id", "blob", "channel_id", "end", "published", "start", "text", "title", "url"]


def export_parts(dataset, output_dir, rows_per_csv=2500):
    """Produce multiple CSVs and return (CSV paths, source-row count, chunk count, video count)."""
    if rows_per_csv < 1:
        raise ValueError("--rows-per-csv must be a positive integer")

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Group by video rather than chunking across video boundaries.
    videos = defaultdict(list)
    source_rows = 0
    for segment in dataset:
        videos[segment["url"]].append(segment)
        source_rows += 1

    paths = []
    output_rows = 0
    rows_in_current_part = 0
    file_handle = None
    writer = None
    try:
        for segments in videos.values():
            segments.sort(key=lambda row: float(row["start"]))
            # The last shorter window is intentionally kept: no original row is lost.
            covered_until = 0
            for i in range(0, len(segments), STRIDE):
                window = segments[i : i + WINDOW]
                first, last = window[0], window[-1]
                covered_until = max(covered_until, i + len(window))
                text = " ".join(str(row["text"] or "") for row in window)

                # Match the metadata order/types found in youtube_rag_data (2).csv.
                metadata = {
                    "channel_id": first["channel_id"],
                    "end": int(float(last["end"])),
                    "published": first["published"],
                    "start": int(float(first["start"])),
                    "text": text,
                    "title": first["title"],
                    "url": first["url"],
                }
                record = {"id": first["id"], "blob": str(metadata), **metadata}

                if writer is None or rows_in_current_part == rows_per_csv:
                    if file_handle is not None:
                        file_handle.close()
                    path = output_dir / f"youtube_rag_part_{len(paths) + 1:03d}.csv"
                    paths.append(path)
                    file_handle = path.open("w", encoding="utf-8", newline="")
                    writer = csv.DictWriter(file_handle, fieldnames=COLUMNS)
                    writer.writeheader()
                    rows_in_current_part = 0

                writer.writerow(record)
                output_rows += 1
                rows_in_current_part += 1
            assert covered_until == len(segments), "A source transcript segment was missed"
    finally:
        if file_handle is not None:
            file_handle.close()

    return paths, source_rows, output_rows, len(videos)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rows-per-csv", type=int, default=2500,
                        help="Maximum RAG chunks per CSV (default: 2500)")
    parser.add_argument("--output-dir", default="data/youtube_rag_full",
                        help="Folder for the resulting CSV files")
    parser.add_argument("--zip", action="store_true",
                        help="Also create one ZIP containing all CSV parts")
    args = parser.parse_args()

    from datasets import load_dataset

    print(f"Downloading full dataset: {DATASET} (split=train)...")
    dataset = load_dataset(DATASET, split="train")
    paths, source_rows, chunks, video_count = export_parts(
        dataset, args.output_dir, args.rows_per_csv
    )

    print(f"Original transcript segments: {source_rows:,}")
    print(f"Unique videos: {video_count:,}")
    print(f"RAG chunks generated: {chunks:,}")
    print(f"CSV files created: {len(paths)}")
    print(f"Saved to: {Path(args.output_dir).resolve()}")

    if args.zip:
        zip_path = Path(args.output_dir).with_suffix(".zip")
        with ZipFile(zip_path, "w", compression=ZIP_DEFLATED) as zip_file:
            for path in paths:
                zip_file.write(path, arcname=path.name)
        print(f"ZIP archive: {zip_path.resolve()}")


if __name__ == "__main__":
    main()