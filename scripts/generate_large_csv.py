#!/usr/bin/env python3
"""
Generate a large CSV file for testing by replicating temperature data
along the time dimension while maintaining a consistent timeline.
"""

import csv
from datetime import datetime, timedelta
from pathlib import Path


def generate_large_csv(
    input_file: Path,
    output_file: Path,
    target_size_mb: int = 500,
) -> None:
    """
    Generate a large CSV by replicating data with continuous timestamps.

    Args:
        input_file: Path to the source CSV file
        output_file: Path to the output CSV file
        target_size_mb: Target size in megabytes
    """
    # Read the original data
    with open(input_file, "r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter=";")
        header = next(reader)
        original_rows = list(reader)

    # Parse timestamps from the original data
    original_timestamps = []
    for row in original_rows:
        dt = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")
        original_timestamps.append(dt)

    # Calculate the time span of the original data
    if len(original_timestamps) >= 2:
        original_duration = original_timestamps[-1] - original_timestamps[0]
    else:
        original_duration = timedelta(days=1)

    # Estimate how many replications we need
    original_size = input_file.stat().st_size
    target_size = target_size_mb * 1024 * 1024
    replications_needed = int(target_size / original_size) + 1

    print(f"Original file size: {original_size / 1024:.1f} KB")
    print(f"Target size: {target_size_mb} MB")
    print(f"Original data spans: {original_duration}")
    print(f"Number of replications: {replications_needed}")
    print(f"Estimated final duration: {original_duration * replications_needed}")

    # Write the large CSV
    rows_written = 0
    with open(output_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(header)

        for replication in range(replications_needed):
            # Calculate the time offset for this replication
            # Add a small gap between replications to ensure continuity
            time_offset = original_duration * replication + timedelta(seconds=60) * replication

            for i, row in enumerate(original_rows):
                # Calculate new timestamp
                new_timestamp = original_timestamps[i] + time_offset

                # Create new row with updated timestamp
                new_row = row.copy()
                new_row[0] = new_timestamp.strftime("%Y-%m-%d %H:%M:%S")
                new_row[1] = new_timestamp.strftime("%H:%M:%S")

                writer.writerow(new_row)
                rows_written += 1

            if (replication + 1) % 100 == 0:
                print(f"Completed {replication + 1}/{replications_needed} replications...")

    final_size = output_file.stat().st_size
    print(f"\nDone! Generated {output_file}")
    print(f"Final size: {final_size / 1024 / 1024:.1f} MB")
    print(f"Total rows: {rows_written:,}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate large CSV for testing")
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/MessTemperatur_20251221.csv"),
        help="Input CSV file",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/MessTemperatur_large.csv"),
        help="Output CSV file",
    )
    parser.add_argument(
        "--size",
        type=int,
        default=10,
        help="Target size in MB (default: 10)",
    )

    args = parser.parse_args()

    # Resolve paths relative to the script's parent directory
    script_dir = Path(__file__).parent.parent
    input_path = script_dir / args.input if not args.input.is_absolute() else args.input
    output_path = script_dir / args.output if not args.output.is_absolute() else args.output

    generate_large_csv(input_path, output_path, args.size)
