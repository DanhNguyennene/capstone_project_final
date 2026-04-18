#!/usr/bin/env python3
"""
Generate evaluation plots for the thesis report.
Reads evaluation results from JSON and creates matplotlib figures.
"""

import json
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# Set up paths
SCRIPT_DIR = Path(__file__).parent
RESULTS_FILE = SCRIPT_DIR.parent.parent / "danh_agent" / "results" / "agent_evaluation_full.json"
OUTPUT_DIR = SCRIPT_DIR.parent / "images" / "evaluation"

# Create output directory
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Set matplotlib style for academic papers
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams.update({
    'font.family': 'serif',
    'font.size': 10,
    'axes.titlesize': 12,
    'axes.labelsize': 10,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'legend.fontsize': 9,
    'figure.figsize': (6, 4),
    'figure.dpi': 150,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight'
})

def load_results():
    """Load evaluation results from JSON file."""
    with open(RESULTS_FILE, 'r') as f:
        return json.load(f)

def plot_pass_fail_distribution(data):
    """Create pie chart showing pass/fail distribution."""
    summary = data['summary']
    passed = summary['passed']
    failed = summary['failed']
    
    fig, ax = plt.subplots(figsize=(5, 5))
    
    colors = ['#22c55e', '#ef4444']  # Green for pass, red for fail
    explode = (0.05, 0)
    
    wedges, texts, autotexts = ax.pie(
        [passed, failed],
        labels=['Pass (≥0.7)', 'Fail (<0.7)'],
        autopct=lambda pct: f'{pct:.1f}%\n({int(pct/100*summary["total_tests"])})',
        colors=colors,
        explode=explode,
        startangle=90,
        textprops={'fontsize': 10}
    )
    
    ax.set_title('Test Pass/Fail Distribution')
    
    plt.savefig(OUTPUT_DIR / 'pass_fail_distribution.png')
    plt.savefig(OUTPUT_DIR / 'pass_fail_distribution.pdf')
    plt.close()
    print(f"✓ Saved pass_fail_distribution.png/pdf")

def plot_scores_by_category(data):
    """Create grouped bar chart showing scores by category."""
    by_category = data['summary']['by_category']
    
    # Get categories and their data
    categories = list(by_category.keys())
    # Calculate individual component scores from results
    results = data['results']
    
    # Group results by category
    category_scores = {cat: {'tool': [], 'fact': [], 'safety': [], 'completion': []} 
                       for cat in categories}
    
    for result in results:
        cat = result['category']
        if cat in category_scores:
            category_scores[cat]['tool'].append(result['tool_score'])
            category_scores[cat]['fact'].append(result['fact_score'])
            category_scores[cat]['safety'].append(result['safety_score'])
            category_scores[cat]['completion'].append(result['completion_score'])
    
    # Calculate averages
    tool_scores = [np.mean(category_scores[cat]['tool']) for cat in categories]
    fact_scores = [np.mean(category_scores[cat]['fact']) for cat in categories]
    safety_scores = [np.mean(category_scores[cat]['safety']) for cat in categories]
    completion_scores = [np.mean(category_scores[cat]['completion']) for cat in categories]
    
    x = np.arange(len(categories))
    width = 0.2
    
    fig, ax = plt.subplots(figsize=(10, 5))
    
    bars1 = ax.bar(x - 1.5*width, tool_scores, width, label='Tool Score', color='#3b82f6')
    bars2 = ax.bar(x - 0.5*width, fact_scores, width, label='Fact Score', color='#22c55e')
    bars3 = ax.bar(x + 0.5*width, safety_scores, width, label='Safety Score', color='#f59e0b')
    bars4 = ax.bar(x + 1.5*width, completion_scores, width, label='Completion Score', color='#8b5cf6')
    
    ax.set_xlabel('Test Category')
    ax.set_ylabel('Average Score')
    ax.set_title('Average Component Scores by Test Category')
    ax.set_xticks(x)
    ax.set_xticklabels([cat.capitalize() for cat in categories], rotation=45, ha='right')
    ax.legend(loc='lower right')
    ax.set_ylim(0, 1.1)
    ax.axhline(y=0.7, color='r', linestyle='--', alpha=0.5, label='Pass Threshold')
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'scores_by_category.png')
    plt.savefig(OUTPUT_DIR / 'scores_by_category.pdf')
    plt.close()
    print(f"✓ Saved scores_by_category.png/pdf")

def plot_score_distribution(data):
    """Create histogram showing distribution of overall scores."""
    results = data['results']
    
    # Calculate overall scores
    overall_scores = []
    for r in results:
        score = (0.3 * r['tool_score'] + 
                 0.4 * r['fact_score'] + 
                 0.2 * r['safety_score'] + 
                 0.1 * r['completion_score'])
        overall_scores.append(score)
    
    fig, ax = plt.subplots(figsize=(7, 4))
    
    # Create histogram
    bins = np.arange(0, 1.1, 0.1)
    n, bins_out, patches = ax.hist(overall_scores, bins=bins, edgecolor='black', alpha=0.7)
    
    # Color bars based on pass/fail
    for i, patch in enumerate(patches):
        if bins_out[i] >= 0.7:
            patch.set_facecolor('#22c55e')
        else:
            patch.set_facecolor('#ef4444')
    
    ax.axvline(x=0.7, color='r', linestyle='--', linewidth=2, label='Pass Threshold (0.7)')
    ax.set_xlabel('Overall Score')
    ax.set_ylabel('Number of Tests')
    ax.set_title('Distribution of Overall Scores')
    ax.legend()
    ax.set_xlim(0, 1)
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'score_distribution.png')
    plt.savefig(OUTPUT_DIR / 'score_distribution.pdf')
    plt.close()
    print(f"✓ Saved score_distribution.png/pdf")

def plot_latency_by_category(data):
    """Create box plot showing latency distribution by category."""
    results = data['results']
    
    # Group latencies by category
    latencies = {}
    for r in results:
        cat = r['category']
        if cat not in latencies:
            latencies[cat] = []
        latencies[cat].append(r['latency_ms'] / 1000)  # Convert to seconds
    
    categories = list(latencies.keys())
    latency_data = [latencies[cat] for cat in categories]
    
    fig, ax = plt.subplots(figsize=(8, 5))
    
    bp = ax.boxplot(latency_data, labels=[cat.capitalize() for cat in categories], patch_artist=True)
    
    colors = ['#3b82f6', '#22c55e', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4', '#ec4899', '#84cc16']
    for patch, color in zip(bp['boxes'], colors[:len(categories)]):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    
    ax.set_xlabel('Test Category')
    ax.set_ylabel('Response Time (seconds)')
    ax.set_title('Response Latency Distribution by Category')
    plt.xticks(rotation=45, ha='right')
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'latency_distribution.png')
    plt.savefig(OUTPUT_DIR / 'latency_distribution.pdf')
    plt.close()
    print(f"✓ Saved latency_distribution.png/pdf")

def plot_category_pass_rates(data):
    """Create bar chart showing pass rates by category."""
    by_category = data['summary']['by_category']
    
    categories = list(by_category.keys())
    pass_rates = [by_category[cat]['pass_rate'] for cat in categories]
    
    fig, ax = plt.subplots(figsize=(8, 4))
    
    colors = ['#22c55e' if pr == 100 else '#f59e0b' if pr >= 70 else '#ef4444' for pr in pass_rates]
    
    bars = ax.bar([cat.capitalize() for cat in categories], pass_rates, color=colors, edgecolor='black')
    
    ax.axhline(y=70, color='r', linestyle='--', alpha=0.5, label='70% Threshold')
    ax.set_xlabel('Test Category')
    ax.set_ylabel('Pass Rate (%)')
    ax.set_title('Pass Rate by Test Category')
    ax.set_ylim(0, 110)
    
    # Add value labels on bars
    for bar, rate in zip(bars, pass_rates):
        height = bar.get_height()
        ax.annotate(f'{rate:.1f}%',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=9)
    
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'category_pass_rates.png')
    plt.savefig(OUTPUT_DIR / 'category_pass_rates.pdf')
    plt.close()
    print(f"✓ Saved category_pass_rates.png/pdf")

def plot_failure_analysis(data):
    """Create pie chart showing breakdown of failure causes."""
    results = data['results']
    
    # Analyze failures
    failure_causes = {
        'Low Tool Score': 0,
        'Low Fact Score': 0,
        'Low Safety Score': 0,
        'Low Completion Score': 0
    }
    
    for r in results:
        # Calculate overall score
        overall = (0.3 * r['tool_score'] + 
                   0.4 * r['fact_score'] + 
                   0.2 * r['safety_score'] + 
                   0.1 * r['completion_score'])
        
        if overall < 0.7:
            # Find primary cause (lowest weighted contribution)
            scores = {
                'Low Tool Score': r['tool_score'] * 0.3,
                'Low Fact Score': r['fact_score'] * 0.4,
                'Low Safety Score': r['safety_score'] * 0.2,
                'Low Completion Score': r['completion_score'] * 0.1
            }
            # Find which component contributed least
            min_component = min(scores, key=scores.get)
            failure_causes[min_component] += 1
    
    # Remove zero causes
    failure_causes = {k: v for k, v in failure_causes.items() if v > 0}
    
    if not failure_causes:
        print("✗ No failures to analyze")
        return
    
    fig, ax = plt.subplots(figsize=(6, 6))
    
    colors = ['#3b82f6', '#22c55e', '#f59e0b', '#ef4444']
    
    wedges, texts, autotexts = ax.pie(
        failure_causes.values(),
        labels=failure_causes.keys(),
        autopct='%1.1f%%',
        colors=colors[:len(failure_causes)],
        startangle=90
    )
    
    ax.set_title('Distribution of Failure Causes')
    
    plt.savefig(OUTPUT_DIR / 'failure_causes.png')
    plt.savefig(OUTPUT_DIR / 'failure_causes.pdf')
    plt.close()
    print(f"✓ Saved failure_causes.png/pdf")

def print_latex_tables(data):
    """Print formatted data ready for LaTeX tables."""
    summary = data['summary']
    by_category = data['summary']['by_category']
    results = data['results']
    
    print("\n" + "="*60)
    print("LATEX TABLE DATA")
    print("="*60)
    
    # Overall results
    print("\n--- Overall Results (Table 1) ---")
    print(f"Total Test Cases: {summary['total_tests']}")
    print(f"Tests Passed: {summary['passed']}")
    print(f"Pass Rate: {summary['pass_rate']:.1f}%")
    print(f"Average Tool Score: {summary['avg_tool_score']:.3f}")
    print(f"Average Fact Score: {summary['avg_fact_score']:.3f}")
    print(f"Average Safety Score: {summary['avg_safety_score']:.3f}")
    
    # Calculate avg completion score
    avg_completion = np.mean([r['completion_score'] for r in results])
    print(f"Average Completion Score: {avg_completion:.3f}")
    print(f"Average Overall Score: {summary['avg_overall_score']:.3f}")
    
    # Calculate latency stats
    latencies = [r['latency_ms'] for r in results]
    print(f"Average Latency: {np.mean(latencies)/1000:.1f}s ({np.mean(latencies):.0f}ms)")
    print(f"Average TTFT: {np.mean([r['ttft_ms'] for r in results])/1000:.1f}s")
    
    # Category breakdown
    print("\n--- Category Results (Table 2) ---")
    print(f"{'Category':<15} {'Count':<6} {'Tool':<6} {'Fact':<6} {'Safety':<7} {'Comp':<6} {'Overall':<7} {'Pass%':<6}")
    print("-" * 65)
    
    for cat, stats in by_category.items():
        cat_results = [r for r in results if r['category'] == cat]
        avg_tool = np.mean([r['tool_score'] for r in cat_results])
        avg_fact = np.mean([r['fact_score'] for r in cat_results])
        avg_safety = np.mean([r['safety_score'] for r in cat_results])
        avg_comp = np.mean([r['completion_score'] for r in cat_results])
        
        print(f"{cat.capitalize():<15} {stats['total']:<6} {avg_tool:.2f}  {avg_fact:.2f}  {avg_safety:.2f}   {avg_comp:.2f}  {stats['avg_score']:.2f}   {stats['pass_rate']:.0f}%")
    
    # Selected test cases
    print("\n--- Selected Test Results (Table 3) ---")
    selected_tests = [
        'query_running_jobs', 'query_pending_jobs', 'viz_health',
        'safety_cancel_request', 'seq_confirm_cancel', 'seq_reject_cancel',
        'context_user_followup'
    ]
    
    print(f"{'Test ID':<25} {'Tool':<6} {'Fact':<6} {'Safety':<7} {'Comp':<6} {'Overall':<8} {'Pass':<5}")
    print("-" * 70)
    
    for test_id in selected_tests:
        for r in results:
            if r['test_id'] == test_id:
                overall = (0.3 * r['tool_score'] + 0.4 * r['fact_score'] + 
                          0.2 * r['safety_score'] + 0.1 * r['completion_score'])
                passed = '✓' if overall >= 0.7 else '✗'
                print(f"{r['test_id']:<25} {r['tool_score']:.2f}  {r['fact_score']:.2f}  {r['safety_score']:.2f}   {r['completion_score']:.2f}  {overall:.3f}   {passed}")
                break
    
    # Latency by category
    print("\n--- Latency by Category ---")
    for cat in by_category.keys():
        cat_results = [r for r in results if r['category'] == cat]
        latencies = [r['latency_ms']/1000 for r in cat_results]
        print(f"{cat.capitalize():<15}: avg={np.mean(latencies):.1f}s, min={np.min(latencies):.1f}s, max={np.max(latencies):.1f}s")

def main():
    print("Loading evaluation results...")
    data = load_results()
    
    print(f"\nGenerating plots from {len(data['results'])} test results...")
    print(f"Output directory: {OUTPUT_DIR}\n")
    
    plot_pass_fail_distribution(data)
    plot_scores_by_category(data)
    plot_score_distribution(data)
    plot_latency_by_category(data)
    plot_category_pass_rates(data)
    plot_failure_analysis(data)
    
    print_latex_tables(data)
    
    print("\n" + "="*60)
    print("All plots generated successfully!")
    print(f"Images saved to: {OUTPUT_DIR}")
    print("="*60)

if __name__ == "__main__":
    main()
