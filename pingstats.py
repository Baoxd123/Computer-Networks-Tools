#!/usr/bin/env python3

import argparse
import subprocess
import json
import os
import time
import statistics
import matplotlib.pyplot as plt

def run_ping(target, max_pings, delay):
    """Run ping to the target and return the raw output."""
    try:
        result = subprocess.run(
            ["ping", "-c", str(max_pings), "-i", str(delay), target],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode == 0:
            return result.stdout
        else:
            print(f"Error running ping: {result.stderr}")
            return None
    except Exception as e:
        print(f"Exception running ping: {e}")
        return None

def parse_ping_output(ping_output):
    """Parse the ping output and extract latency information."""
    latencies = []
    for line in ping_output.splitlines():
        if "time=" in line:
            parts = line.split()
            for part in parts:
                if part.startswith("time="):
                    try:
                        latency = float(part.split("=")[1])
                        latencies.append(latency)
                    except ValueError:
                        continue
    
    if latencies:
        stats = {
            "avg": sum(latencies) / len(latencies),
            "max": max(latencies),
            "med": statistics.median(latencies),
            "min": min(latencies)
        }
        return stats
    else:
        return None

def aggregate_ping_stats(stats_list):
    """Aggregate statistics across multiple ping runs."""
    all_latencies = []
    for stats in stats_list:
        all_latencies.extend([stats["min"], stats["med"], stats["avg"], stats["max"]])
    
    aggregated_stats = {
        "avg": round(sum(all_latencies) / len(all_latencies), 3),
        "max": max(all_latencies),
        "med": statistics.median(all_latencies),
        "min": min(all_latencies)
    }
    return aggregated_stats

def save_to_json(data, output_file):
    """Save the data to a JSON file."""
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=4)

def generate_boxplot(latency_stats, output_file):
    """Generate a boxplot for latency statistics."""
    latency_distribution = [
        [latency_stats['min'], latency_stats['med'], latency_stats['avg'], latency_stats['max']]
    ]
    
    plt.figure(figsize=(12, 6))
    plt.boxplot(latency_distribution, showmeans=True)
    plt.xlabel('Ping Runs')
    plt.ylabel('Latency (ms)')
    plt.title('Ping Latency Distribution')
    plt.grid(True)
    plt.savefig(output_file)
    plt.close()

def main():
    parser = argparse.ArgumentParser(description="Run ping multiple times towards a given target host")
    parser.add_argument('-m', '--max_pings', type=int, default=10, help="Number of max ping packets to send")
    parser.add_argument('-d', '--delay', type=int, default=1, help="Number of seconds to wait between two consecutive ping packets")
    parser.add_argument('-o', '--output', required=True, help="Path and name of output JSON file containing the stats")
    parser.add_argument('-g', '--graph', required=True, help="Path and name of output PDF file containing stats graph")
    parser.add_argument('-t', '--target', help="A target domain name or IP address (required if --test is absent)")
    
    args = parser.parse_args()

    if not args.target:
        print("Target is required.")
        return

    # Run ping command
    ping_output = run_ping(args.target, args.max_pings, args.delay)
    if ping_output:
        stats = parse_ping_output(ping_output)
        
        if stats:
            # Save the statistics to a JSON file
            save_to_json(stats, args.output)

            # Generate the latency distribution graph
            generate_boxplot(stats, args.graph)

if __name__ == '__main__':
    main()
