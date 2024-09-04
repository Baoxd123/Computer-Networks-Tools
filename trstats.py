#!/usr/bin/env python3

import argparse
import subprocess
import json
import os
import time
import statistics
import matplotlib.pyplot as plt

def run_traceroute(target, max_hops):
    """Run traceroute to the target and return the raw output."""
    try:
        result = subprocess.run(
            ["traceroute", "-m", str(max_hops), target],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode == 0:
            return result.stdout
        else:
            print(f"Error running traceroute: {result.stderr}")
            return None
    except Exception as e:
        print(f"Exception running traceroute: {e}")
        return None

def parse_traceroute_output(traceroute_output):
    """Parse the traceroute output and extract hop information."""
    hops = []
    for line in traceroute_output.splitlines():
        if line.startswith("traceroute") or line.strip() == "":
            continue
        parts = line.split()
        hop_number = int(parts[0])
        hosts = []
        latencies = []

        i = 1
        while i < len(parts):
            if parts[i].startswith('(') and parts[i].endswith(')'):
                # Skip this part as it should have been paired already
                i += 1
                continue
            try:
                # If it's a latency value, process it
                latency = float(parts[i].replace("ms", ""))
                latencies.append(latency)
            except ValueError:
                # Assume this part is a hostname, and check the next part for an IP
                hostname = parts[i]
                if i + 1 < len(parts) and parts[i + 1].startswith('(') and parts[i + 1].endswith(')'):
                    ip_address = parts[i + 1]
                    if [hostname, ip_address] not in hosts:
                        hosts.append([hostname, ip_address])
                    i += 1  # Skip the IP part since we've just paired it
                else:
                    i = i
                #    hosts.append([hostname, f"({hostname})"])  # Handle case where no IP is found
            i += 1
        
        if latencies:
            hops.append({
                "avg": sum(latencies) / len(latencies),
                "hop": hop_number,
                "hosts": hosts,
                "max": max(latencies),
                "med": statistics.median(latencies),
                "min": min(latencies)
            })
    return hops

def aggregate_stats(hops_list):
    """Aggregate statistics across multiple traceroute runs."""
    aggregated = {}
    for hops in hops_list:
        for hop in hops:
            hop_number = hop["hop"]
            if hop_number not in aggregated:
                aggregated[hop_number] = {
                    "hop": hop_number,
                    "hosts": hop["hosts"],
                    "min": [],
                    "max": [],
                    "avg": [],
                    "med": []
                }
            aggregated[hop_number]["min"].append(hop["min"])
            aggregated[hop_number]["max"].append(hop["max"])
            aggregated[hop_number]["avg"].append(hop["avg"])
            aggregated[hop_number]["med"].append(hop["med"])
    
    # Calculate final statistics
    final_stats = []
    for hop_number in sorted(aggregated):
        hop = aggregated[hop_number]
        final_stats.append({
            "avg": round(sum(hop["avg"]) / len(hop["avg"]),3),
            "hop": hop["hop"],
            #"hosts": [[host, f"({host})"] for host in hop["hosts"]],
            "hosts": hop["hosts"],
            "max": max(hop["max"]),
            "med": statistics.median(hop["med"]),
            "min": min(hop["min"])
        })
    return final_stats

def save_to_json(data, output_file):
    """Save the data to a JSON file."""
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=4)

def generate_boxplot(hops_stats, output_file):
    """Generate a boxplot for latency statistics per hop."""
    latency_distribution = [
        [hop['min'], hop['med'], hop['avg'], hop['max']]
        for hop in hops_stats
    ]
    hops = [str(hop['hop']) for hop in hops_stats]

    plt.figure(figsize=(12, 6))
    plt.boxplot(latency_distribution, labels=hops, showmeans=True)
    plt.xlabel('Hop Number')
    plt.ylabel('Latency (ms)')
    plt.title('Latency Distribution per Hop')
    plt.grid(True)
    plt.savefig(output_file)
    plt.close()
    
def main():
    parser = argparse.ArgumentParser(description="Run traceroute multiple times towards a given target host")
    parser.add_argument('-n', '--num_runs', type=int, default=1, help="Number of times traceroute will run")
    parser.add_argument('-d', '--run_delay', type=int, default=1, help="Number of seconds to wait between two consecutive runs")
    parser.add_argument('-m', '--max_hops', type=int, default=30, help="Number of max hops per traceroute run")
    parser.add_argument('-o', '--output', required=True, help="Path and name of output JSON file containing the stats")
    parser.add_argument('-g', '--graph', required=True, help="Path and name of output PDF file containing stats graph")
    parser.add_argument('-t', '--target', help="A target domain name or IP address (required if --test is absent)")
    parser.add_argument('--test', help="Directory containing num_runs text files, each containing the output of a traceroute run")
    
    args = parser.parse_args()

    hops_list = []

    if args.test:
        # Read from pre-generated traceroute output files
        for i in range(1, args.num_runs + 1):
            file_path = os.path.join(args.test, f"tr_run-{i}.out")
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    traceroute_output = f.read()
                    hops = parse_traceroute_output(traceroute_output)
                    hops_list.append(hops)
            else:
                print(f"File {file_path} does not exist.")
    else:
        if not args.target:
            print("Target is required when not in test mode.")
            return
        # Run traceroute multiple times
        for _ in range(args.num_runs):
            traceroute_output = run_traceroute(args.target, args.max_hops)
            if traceroute_output:
                hops = parse_traceroute_output(traceroute_output)
                hops_list.append(hops)
            time.sleep(args.run_delay)

    # Aggregate the statistics
    final_stats = aggregate_stats(hops_list)

    # Save the statistics to a JSON file
    save_to_json(final_stats, args.output)

    # Generate the latency distribution graph
    generate_boxplot(final_stats, args.graph)

if __name__ == '__main__':
    main()
