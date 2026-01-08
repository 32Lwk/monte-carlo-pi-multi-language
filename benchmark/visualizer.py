#!/usr/bin/env python3
"""
結果を可視化するスクリプト
HTMLレポートを生成します。
"""

import json
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
RESULTS_DIR = ROOT_DIR / "results"

def generate_html_report():
    """HTMLレポートを生成"""
    results_file = RESULTS_DIR / "results.json"
    
    if not results_file.exists():
        print("No results file found. Run runner.py first.")
        return
    
    with open(results_file, "r") as f:
        results = json.load(f)
    
    # HTMLテンプレート
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Monte Carlo Pi Benchmark Results</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        .chart-container {{ width: 800px; height: 400px; margin: 20px 0; }}
    </style>
</head>
<body>
    <h1>Monte Carlo Pi Benchmark Results</h1>
    
    <h2>Results Table</h2>
    <table>
        <tr>
            <th>Language</th>
            <th>Variant</th>
            <th>Mode</th>
            <th>Time (ms)</th>
            <th>Error</th>
            <th>Memory (MB)</th>
        </tr>
"""
    
    for result in results:
        html += f"""
        <tr>
            <td>{result.get('language', 'N/A')}</td>
            <td>{result.get('variant', 'standard')}</td>
            <td>{result.get('mode', 'single')}</td>
            <td>{result.get('time_ms', 0):.2f}</td>
            <td>{result.get('error', 0):.15f}</td>
            <td>{result.get('memory_mb', 0):.2f}</td>
        </tr>
"""
    
    html += """
    </table>
    
    <h2>Charts</h2>
    <div class="chart-container">
        <canvas id="timeChart"></canvas>
    </div>
    
    <script>
        const results = """ + json.dumps(results) + """;
        
        const ctx = document.getElementById('timeChart').getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: results.map(r => r.language + ' ' + r.variant + ' ' + r.mode),
                datasets: [{
                    label: 'Time (ms)',
                    data: results.map(r => r.time_ms),
                    backgroundColor: 'rgba(54, 162, 235, 0.5)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    </script>
</body>
</html>
"""
    
    # HTMLファイルを保存
    html_file = RESULTS_DIR / "report.html"
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html)
    
    print(f"HTML report saved to {html_file}")


if __name__ == "__main__":
    generate_html_report()

