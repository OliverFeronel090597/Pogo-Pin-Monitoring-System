import sys
import os
import json
from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtWidgets import QApplication, QVBoxLayout, QWidget, QPushButton, QHBoxLayout
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineSettings


class GraphData(QWidget):
    def __init__(self, categories, bar_data, line_data, right_label, left_label, 
                 top_label, bottom_label, parent=None):
        super().__init__(parent)
        self.categories = categories
        self.bar_data = bar_data
        self.line_data = line_data
        self.right_label = right_label
        self.left_label = left_label
        self.top_label = top_label
        self.bottom_label = bottom_label
        self.is_initialized = False
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create web view with optimized settings
        self.web_view = QWebEngineView()
        self.web_view.setMinimumHeight(700)
        
        # Optimize WebEngine settings to reduce flicker
        settings = self.web_view.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.Accelerated2dCanvasEnabled, False)
        settings.setAttribute(QWebEngineSettings.WebAttribute.WebGLEnabled, False)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
        
        # Prevent flicker during resize and updates
        self.web_view.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, True)
        self.web_view.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        
        # Load HTML once
        html_content = self.generate_html()
        self.web_view.setHtml(html_content, QUrl("file:///"))
        
        # Connect signals
        self.web_view.loadFinished.connect(self.on_page_loaded)
        
        layout.addWidget(self.web_view)

    def on_page_loaded(self, ok):
        """Called when page is fully loaded"""
        if ok and not self.is_initialized:
            self.is_initialized = True

    def update_chart_data(self, categories, bar_data, line_data):
        """Update chart data without flickering"""
        self.categories = categories
        self.bar_data = bar_data
        self.line_data = line_data
        
        # Use JavaScript update if initialized
        if self.is_initialized:
            # Prepare data for JavaScript
            categories_json = json.dumps(categories)
            bar_data_json = json.dumps(bar_data)
            line_data_json = json.dumps(line_data)
            
            js_code = f"""
                (function() {{
                    try {{
                        // Update global data
                        window.categories = {categories_json};
                        window.barData = {bar_data_json};
                        window.lineData = {line_data_json};
                        
                        // Update main chart
                        if (window.mainChart) {{
                            window.mainChart.data.labels = window.categories;
                            window.mainChart.data.datasets[0].data = window.barData;
                            window.mainChart.data.datasets[1].data = window.lineData;
                            window.mainChart.update('none');
                        }}
                        
                        // Update pie chart
                        if (window.pieChart) {{
                            window.pieChart.data.labels = window.categories;
                            window.pieChart.data.datasets[0].data = window.barData;
                            window.pieChart.update('none');
                        }}
                        
                        // Update donut chart
                        if (window.donutChart) {{
                            window.donutChart.data.labels = window.categories;
                            window.donutChart.data.datasets[0].data = window.barData;
                            window.donutChart.update('none');
                        }}
                        
                        // Update radar chart
                        if (window.radarChart) {{
                            const maxBar = Math.max(...window.barData);
                            const maxLine = Math.max(...window.lineData);
                            window.radarChart.data.labels = window.categories;
                            window.radarChart.data.datasets[0].data = window.barData;
                            if (maxLine > 0) {{
                                window.radarChart.data.datasets[1].data = window.lineData.map(v => (v / maxLine) * maxBar);
                            }} else {{
                                window.radarChart.data.datasets[1].data = window.lineData;
                            }}
                            window.radarChart.update('none');
                        }}
                        
                        // Update distribution chart
                        if (window.distributionChart) {{
                            const sortedBar = [...window.barData].sort((a, b) => a - b);
                            const minVal = sortedBar[0] || 0;
                            const maxVal = sortedBar[sortedBar.length - 1] || 1;
                            const range = maxVal - minVal;
                            const binCount = Math.min(6, Math.max(3, Math.ceil(range / 3) + 1));
                            const binSize = range / binCount || 1;
                            
                            const bins = Array(binCount).fill(0);
                            const binLabels = [];
                            
                            for (let i = 0; i < binCount; i++) {{
                                const lower = minVal + i * binSize;
                                const upper = minVal + (i + 1) * binSize;
                                binLabels.push(lower.toFixed(1) + '-' + upper.toFixed(1));
                            }}
                            
                            window.barData.forEach(val => {{
                                let idx = Math.floor((val - minVal) / binSize);
                                if (idx >= binCount) idx = binCount - 1;
                                if (idx < 0) idx = 0;
                                bins[idx]++;
                            }});
                            
                            window.distributionChart.data.labels = binLabels;
                            window.distributionChart.data.datasets[0].data = bins;
                            window.distributionChart.update('none');
                        }}
                        
                        // Update statistics
                        updateStatistics({bar_data_json}, {line_data_json}, {categories_json});
                        
                        console.log('✅ Charts updated successfully');
                    }} catch(e) {{
                        console.error('Update error:', e);
                    }}
                }})();
                
                // Helper function to update statistics
                function updateStatistics(barData, lineData, categories) {{
                    try {{
                        // Calculate statistics
                        const totalBar = barData.reduce((a, b) => a + b, 0);
                        const avgBar = totalBar / barData.length;
                        const maxBar = Math.max(...barData);
                        const minBar = Math.min(...barData);
                        const totalLine = lineData.reduce((a, b) => a + b, 0);
                        const avgLine = totalLine / lineData.length;
                        const maxLine = Math.max(...lineData);
                        const minLine = Math.min(...lineData);
                        
                        // Find top 3 and bottom 3
                        const barWithIdx = barData.map((val, idx) => [val, idx]);
                        barWithIdx.sort((a, b) => b[0] - a[0]);
                        const top3 = barWithIdx.slice(0, 3).map(([val, idx]) => 
                            categories[idx] + ' (' + val.toFixed(0) + ')'
                        ).join(', ');
                        const bottom3 = barWithIdx.slice(-3).map(([val, idx]) => 
                            categories[idx] + ' (' + val.toFixed(0) + ')'
                        ).join(', ');
                        
                        // Update stats in the stats dashboard
                        const statElements = {{
                            'barTotal': totalBar.toFixed(0),
                            'barAvg': avgBar.toFixed(0),
                            'barMax': maxBar.toFixed(0),
                            'barMin': minBar.toFixed(0),
                            'lineAvg': '€' + avgLine.toFixed(2),
                            'lineMax': '€' + maxLine.toFixed(2),
                            'lineMin': '€' + minLine.toFixed(2),
                            'top3': top3,
                            'bottom3': bottom3,
                            'totalCategories': categories.length
                        }};
                        
                        // Update stat items
                        document.querySelectorAll('[id]').forEach(el => {{
                            if (statElements[el.id] !== undefined) {{
                                el.textContent = statElements[el.id];
                            }}
                        }});
                        
                    }} catch(e) {{
                        console.error('Error updating statistics:', e);
                    }}
                }}
            """
            self.web_view.page().runJavaScript(js_code)

    def generate_html(self):
        """Generate optimized HTML with Chart.js - no flicker"""
        
        # Convert data to float if it contains strings
        try:
            line_data_float = [float(x) if isinstance(x, str) else x for x in self.line_data]
        except (ValueError, TypeError):
            line_data_float = self.line_data
        
        try:
            bar_data_float = [float(x) if isinstance(x, str) else x for x in self.bar_data]
        except (ValueError, TypeError):
            bar_data_float = self.bar_data
        
        # Ensure we have sample data if empty
        if not self.categories:
            self.categories = ['Sample A', 'Sample B', 'Sample C', 'Sample D', 'Sample E']
            bar_data_float = [10, 20, 15, 30, 25]
            line_data_float = [5.5, 10.0, 7.75, 15.2, 12.3]
            self.right_label = self.right_label or 'Total Price in EURO'
            self.left_label = self.left_label or 'Frequency'
            self.top_label = self.top_label or 'Sample Data Analysis'
            self.bottom_label = self.bottom_label or 'Sample Data Insights'
        
        # Prepare data for JavaScript
        categories_json = json.dumps(self.categories)
        bar_data_json = json.dumps(bar_data_float)
        line_data_json = json.dumps(line_data_float)
        
        # Calculate comprehensive statistics
        total_bar = sum(bar_data_float) if bar_data_float else 0
        avg_bar = sum(bar_data_float) / len(bar_data_float) if bar_data_float else 0
        avg_line = sum(line_data_float) / len(line_data_float) if line_data_float else 0
        max_bar = max(bar_data_float) if bar_data_float else 0
        max_line = max(line_data_float) if line_data_float else 0
        min_bar = min(bar_data_float) if bar_data_float else 0
        min_line = min(line_data_float) if line_data_float else 0
        
        # Calculate median
        sorted_bar = sorted(bar_data_float) if bar_data_float else []
        sorted_line = sorted(line_data_float) if line_data_float else []
        median_bar = sorted_bar[len(sorted_bar)//2] if sorted_bar else 0
        median_line = sorted_line[len(sorted_line)//2] if sorted_line else 0
        
        # Calculate standard deviation
        if len(bar_data_float) > 1:
            variance_bar = sum((x - avg_bar) ** 2 for x in bar_data_float) / len(bar_data_float)
            std_bar = variance_bar ** 0.5
        else:
            std_bar = 0
            
        if len(line_data_float) > 1:
            variance_line = sum((x - avg_line) ** 2 for x in line_data_float) / len(line_data_float)
            std_line = variance_line ** 0.5
        else:
            std_line = 0
        
        # Calculate percentiles
        p25_bar = sorted_bar[len(sorted_bar)//4] if len(sorted_bar) >= 4 else (sorted_bar[0] if sorted_bar else 0)
        p75_bar = sorted_bar[3*len(sorted_bar)//4] if len(sorted_bar) >= 4 else (sorted_bar[-1] if sorted_bar else 0)
        p25_line = sorted_line[len(sorted_line)//4] if len(sorted_line) >= 4 else (sorted_line[0] if sorted_line else 0)
        p75_line = sorted_line[3*len(sorted_line)//4] if len(sorted_line) >= 4 else (sorted_line[-1] if sorted_line else 0)
        
        # Find top 3 and bottom 3
        bar_with_idx = [(val, idx) for idx, val in enumerate(bar_data_float)]
        bar_with_idx.sort(reverse=True)
        top_3_bar = [(self.categories[idx], val) for val, idx in bar_with_idx[:3]]
        bottom_3_bar = [(self.categories[idx], val) for val, idx in bar_with_idx[-3:]]
        
        # Format for display
        total_bar_display = f"{total_bar:,.0f}"
        avg_bar_display = f"{avg_bar:,.0f}"
        avg_line_display = f"€{avg_line:,.2f}"
        max_bar_display = f"{max_bar:,.0f}"
        max_line_display = f"€{max_line:,.2f}"
        min_bar_display = f"{min_bar:,.0f}"
        min_line_display = f"€{min_line:,.2f}"
        median_bar_display = f"{median_bar:,.0f}"
        median_line_display = f"€{median_line:,.2f}"
        std_bar_display = f"{std_bar:,.0f}"
        std_line_display = f"€{std_line:,.2f}"
        p25_bar_display = f"{p25_bar:,.0f}"
        p75_bar_display = f"{p75_bar:,.0f}"
        p25_line_display = f"€{p25_line:,.2f}"
        p75_line_display = f"€{p75_line:,.2f}"
        
        # Create top/bottom 3 display
        top_3_text = ", ".join([f"{name} ({val:,.0f})" for name, val in top_3_bar])
        bottom_3_text = ", ".join([f"{name} ({val:,.0f})" for name, val in bottom_3_bar])
        
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Dashboard</title>
            <script src="https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js"></script>
            <style>
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}

                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: #f0f2f5;
                    padding: 12px;
                    height: 100vh;
                    overflow: hidden;
                }}

                .graph-container {{
                    background: white;
                    border-radius: 12px;
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
                    padding: 16px;
                    height: 100%;
                    display: flex;
                    flex-direction: column;
                }}

                .tab-container {{
                    display: flex;
                    gap: 4px;
                    margin-bottom: 10px;
                    border-bottom: 1px solid #e9ecef;
                    padding-bottom: 8px;
                    flex-wrap: wrap;
                }}

                .tab-btn {{
                    padding: 6px 14px;
                    border: none;
                    border-radius: 6px;
                    font-size: 11px;
                    font-weight: 500;
                    cursor: pointer;
                    transition: all 0.2s;
                    background: transparent;
                    color: #6c757d;
                }}

                .tab-btn:hover {{
                    background: #f8f9fa;
                    color: #212529;
                }}

                .tab-btn.active {{
                    background: #4A90D9;
                    color: white;
                }}

                .tab-btn .icon {{ margin-right: 4px; }}

                .tab-content {{
                    flex: 1;
                    display: none;
                    min-height: 0;
                }}

                .tab-content.active {{
                    display: flex;
                    flex-direction: column;
                }}

                .chart-wrapper {{
                    position: relative;
                    flex: 1;
                    min-height: 280px;
                    background: #fafbfc;
                    border-radius: 8px;
                    padding: 8px;
                }}

                .chart-grid {{
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 10px;
                    flex: 1;
                    min-height: 0;
                }}

                .chart-grid .chart-wrapper {{
                    min-height: 180px;
                }}

                canvas {{
                    width: 100% !important;
                    height: 100% !important;
                }}

                .header {{
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 10px;
                    flex-wrap: wrap;
                    gap: 8px;
                }}

                .header h1 {{
                    font-size: 16px;
                    font-weight: 600;
                    color: #1a1a2e;
                    margin: 0;
                }}

                .stats-bar {{
                    display: flex;
                    gap: 10px;
                    flex-wrap: wrap;
                    padding: 8px 0 0 0;
                    border-top: 1px solid #e9ecef;
                    margin-top: 8px;
                }}

                .stat-item {{
                    text-align: center;
                    padding: 4px 10px;
                    background: #f8f9fa;
                    border-radius: 6px;
                }}

                .stat-item .number {{
                    font-size: 13px;
                    font-weight: 700;
                    color: #1a1a2e;
                }}

                .stat-item .label {{
                    font-size: 8px;
                    color: #6c757d;
                    text-transform: uppercase;
                    letter-spacing: 0.3px;
                }}

                .stat-item .number.bar-stat {{ color: #4A90D9; }}
                .stat-item .number.line-stat {{ color: #E74C3C; }}

                /* Stats Dashboard Styles */
                .stats-dashboard {{
                    flex: 1;
                    overflow-y: auto;
                    padding: 10px;
                    background: #fafbfc;
                    border-radius: 8px;
                }}

                .stats-grid {{
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 15px;
                    max-width: 100%;
                }}

                .stats-card {{
                    background: white;
                    padding: 15px;
                    border-radius: 8px;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
                }}

                .stats-card h3 {{
                    color: #4A90D9;
                    margin-bottom: 10px;
                    font-size: 14px;
                }}

                .stats-card.line-card h3 {{
                    color: #E74C3C;
                }}

                .stats-grid-inner {{
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 6px;
                    font-size: 12px;
                }}

                .stats-grid-inner strong {{
                    color: #495057;
                }}

                .stats-grid-inner .value {{
                    font-weight: 700;
                }}

                .stats-grid-inner .value.bar-value {{ color: #4A90D9; }}
                .stats-grid-inner .value.line-value {{ color: #E74C3C; }}
                .stats-grid-inner .value.highlight {{ color: #2ECC71; }}
                .stats-grid-inner .value.warning {{ color: #E74C3C; }}

                .insights-card {{
                    background: white;
                    padding: 15px;
                    border-radius: 8px;
                    margin-top: 12px;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
                }}

                .insights-card h3 {{
                    color: #2C3E50;
                    margin-bottom: 10px;
                    font-size: 14px;
                }}

                .insights-card .insight-item {{
                    font-size: 12px;
                    line-height: 2;
                }}

                .insights-card .insight-item .top {{ color: #2ECC71; font-weight: 600; }}
                .insights-card .insight-item .bottom {{ color: #E74C3C; font-weight: 600; }}

                @media (max-width: 768px) {{
                    .chart-grid {{ grid-template-columns: 1fr; }}
                    .stats-grid {{ grid-template-columns: 1fr; }}
                    .tab-btn {{ font-size: 10px; padding: 4px 10px; }}
                    .header h1 {{ font-size: 14px; }}
                }}
            </style>
        </head>
        <body>

        <div class="graph-container">
            <!-- Header -->
            <div class="header">
                <h1>{self.top_label}</h1>
                <div style="display: flex; gap: 8px; align-items: center;">
                    <span style="font-size: 11px; color: #6c757d;">Toggle:</span>
                    <button onclick="toggleDataset('bar')" style="padding:3px 10px;border:1px solid #4A90D9;border-radius:4px;background:white;color:#4A90D9;font-size:10px;cursor:pointer;">Frequency</button>
                    <button onclick="toggleDataset('line')" style="padding:3px 10px;border:1px solid #E74C3C;border-radius:4px;background:white;color:#E74C3C;font-size:10px;cursor:pointer;">Price</button>
                </div>
            </div>

            <!-- Tabs -->
            <div class="tab-container">
                <button class="tab-btn active" onclick="switchTab('tab1')">
                    <span class="icon">📊</span> Main
                </button>
                <button class="tab-btn" onclick="switchTab('tab2')">
                    <span class="icon">🥧</span> Pie
                </button>
                <button class="tab-btn" onclick="switchTab('tab3')">
                    <span class="icon">🕸️</span> Radar
                </button>
                <button class="tab-btn" onclick="switchTab('tab4')">
                    <span class="icon">📈</span> Distribution
                </button>
                <button class="tab-btn" onclick="switchTab('tab5')">
                    <span class="icon">📋</span> Summary
                </button>
            </div>

            <!-- Tab 1: Main Chart -->
            <div class="tab-content active" id="tab1">
                <div class="chart-wrapper">
                    <canvas id="mainChart"></canvas>
                </div>
            </div>

            <!-- Tab 2: Pie/Donut -->
            <div class="tab-content" id="tab2">
                <div class="chart-grid">
                    <div class="chart-wrapper"><canvas id="pieChart"></canvas></div>
                    <div class="chart-wrapper"><canvas id="donutChart"></canvas></div>
                </div>
            </div>

            <!-- Tab 3: Radar -->
            <div class="tab-content" id="tab3">
                <div class="chart-wrapper">
                    <canvas id="radarChart"></canvas>
                </div>
            </div>

            <!-- Tab 4: Distribution -->
            <div class="tab-content" id="tab4">
                <div class="chart-wrapper">
                    <canvas id="distributionChart"></canvas>
                </div>
            </div>

            <!-- Tab 5: Summary Statistics -->
            <div class="tab-content" id="tab5">
                <div class="stats-dashboard">
                    <div class="stats-grid">
                        <!-- Bar Data Statistics -->
                        <div class="stats-card">
                            <h3>📊 Frequency Statistics</h3>
                            <div class="stats-grid-inner">
                                <div><strong>Total:</strong> <span class="value bar-value">{total_bar_display}</span></div>
                                <div><strong>Average:</strong> <span class="value bar-value">{avg_bar_display}</span></div>
                                <div><strong>Median:</strong> <span class="value bar-value">{median_bar_display}</span></div>
                                <div><strong>Std Dev:</strong> <span class="value bar-value">{std_bar_display}</span></div>
                                <div><strong>Max:</strong> <span class="value highlight">{max_bar_display}</span></div>
                                <div><strong>Min:</strong> <span class="value warning">{min_bar_display}</span></div>
                                <div><strong>P25:</strong> <span class="value bar-value">{p25_bar_display}</span></div>
                                <div><strong>P75:</strong> <span class="value bar-value">{p75_bar_display}</span></div>
                            </div>
                        </div>
                        
                        <!-- Line Data Statistics -->
                        <div class="stats-card line-card">
                            <h3>💰 Price Statistics</h3>
                            <div class="stats-grid-inner">
                                <div><strong>Total:</strong> <span class="value line-value">{total_bar_display}</span></div>
                                <div><strong>Average:</strong> <span class="value line-value">{avg_line_display}</span></div>
                                <div><strong>Median:</strong> <span class="value line-value">{median_line_display}</span></div>
                                <div><strong>Std Dev:</strong> <span class="value line-value">{std_line_display}</span></div>
                                <div><strong>Max:</strong> <span class="value highlight">{max_line_display}</span></div>
                                <div><strong>Min:</strong> <span class="value warning">{min_line_display}</span></div>
                                <div><strong>P25:</strong> <span class="value line-value">{p25_line_display}</span></div>
                                <div><strong>P75:</strong> <span class="value line-value">{p75_line_display}</span></div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Key Insights -->
                    <div class="insights-card">
                        <h3>💡 Key Insights</h3>
                        <div class="insight-item">
                            <div>🏆 <strong>Top 3:</strong> <span class="top">{top_3_text}</span></div>
                            <div>📉 <strong>Bottom 3:</strong> <span class="bottom">{bottom_3_text}</span></div>
                            <div>📊 <strong>Total Categories:</strong> {len(self.categories)}</div>
                            <div>📈 <strong>Frequency Range:</strong> <span style="color: #4A90D9;">{min_bar_display}</span> → <span style="color: #4A90D9;">{max_bar_display}</span></div>
                            <div>📈 <strong>Price Range:</strong> <span style="color: #E74C3C;">{min_line_display}</span> → <span style="color: #E74C3C;">{max_line_display}</span></div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Stats Bar -->
            <div class="stats-bar">
                <div class="stat-item"><span class="number bar-stat">{total_bar_display}</span><div class="label">Total</div></div>
                <div class="stat-item"><span class="number bar-stat">{avg_bar_display}</span><div class="label">Avg Freq</div></div>
                <div class="stat-item"><span class="number line-stat">{avg_line_display}</span><div class="label">Avg Price</div></div>
                <div class="stat-item"><span class="number bar-stat">{max_bar_display}</span><div class="label">Max Freq</div></div>
                <div class="stat-item"><span class="number line-stat">{max_line_display}</span><div class="label">Max Price</div></div>
                <div class="stat-item"><span class="number bar-stat">{min_bar_display}</span><div class="label">Min Freq</div></div>
                <div class="stat-item"><span class="number line-stat">{min_line_display}</span><div class="label">Min Price</div></div>
            </div>
        </div>

        <script>
            // Data
            const categories = {categories_json};
            const barData = {bar_data_json};
            const lineData = {line_data_json};
            
            const colors = ['#4A90D9', '#2ECC71', '#E74C3C', '#F39C12', '#9B59B6', '#1ABC9C', '#3498DB'];
            
            let mainChart = null;
            let pieChart = null;
            let donutChart = null;
            let radarChart = null;
            let distributionChart = null;

            // ################################################################
            // Tab Switching
            // ################################################################
            function switchTab(tabId) {{
                document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
                document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
                
                document.getElementById(tabId).classList.add('active');
                document.querySelector(`.tab-btn[onclick="switchTab('${{tabId}}')"]`).classList.add('active');
                
                // Resize charts without animation
                setTimeout(() => {{
                    const charts = [mainChart, pieChart, donutChart, radarChart, distributionChart];
                    charts.forEach(chart => {{
                        if (chart && chart.resize) {{
                            chart.resize();
                        }}
                    }});
                }}, 50);
            }}

            // ################################################################
            // Main Chart - Bar (Frequency) + Line (Price)
            // ################################################################
            function createMainChart() {{
                const ctx = document.getElementById('mainChart').getContext('2d');
                
                mainChart = new Chart(ctx, {{
                    type: 'bar',
                    data: {{
                        labels: categories,
                        datasets: [{{
                            label: 'Frequency',
                            data: barData,
                            backgroundColor: 'rgba(74, 144, 217, 0.7)',
                            borderColor: '#4A90D9',
                            borderWidth: 1,
                            borderRadius: 4,
                            barPercentage: 0.6,
                            order: 1,
                            yAxisID: 'y'
                        }}, {{
                            label: 'Price',
                            data: lineData,
                            type: 'line',
                            borderColor: '#E74C3C',
                            backgroundColor: 'rgba(231, 76, 60, 0.05)',
                            pointBackgroundColor: '#E74C3C',
                            pointBorderColor: '#fff',
                            pointBorderWidth: 2,
                            pointRadius: 5,
                            pointHoverRadius: 7,
                            fill: true,
                            tension: 0.3,
                            order: 0,
                            yAxisID: 'y1'
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        interaction: {{
                            mode: 'index',
                            intersect: false
                        }},
                        plugins: {{
                            legend: {{
                                display: true,
                                position: 'top',
                                labels: {{
                                    font: {{ size: 11, weight: '600' }},
                                    padding: 10,
                                    usePointStyle: true,
                                    pointStyle: 'circle'
                                }}
                            }},
                            tooltip: {{
                                backgroundColor: 'rgba(0,0,0,0.8)',
                                titleFont: {{ size: 11 }},
                                bodyFont: {{ size: 10 }},
                                padding: 8,
                                cornerRadius: 6,
                                callbacks: {{
                                    label: function(context) {{
                                        let label = context.dataset.label || '';
                                        let val = context.parsed.y;
                                        if (context.dataset.yAxisID === 'y1') {{
                                            return label + ': €' + val.toFixed(2);
                                        }}
                                        return label + ': ' + val.toFixed(0);
                                    }}
                                }}
                            }}
                        }},
                        scales: {{
                            x: {{
                                grid: {{ display: false }},
                                ticks: {{ font: {{ size: 10 }} }}
                            }},
                            y: {{
                                beginAtZero: true,
                                position: 'left',
                                title: {{
                                    display: true,
                                    text: 'Frequency',
                                    font: {{ size: 10, weight: '600' }}
                                }},
                                grid: {{ color: 'rgba(0,0,0,0.05)' }},
                                ticks: {{ font: {{ size: 9 }} }}
                            }},
                            y1: {{
                                beginAtZero: true,
                                position: 'right',
                                title: {{
                                    display: true,
                                    text: 'Price (€)',
                                    font: {{ size: 10, weight: '600' }}
                                }},
                                grid: {{ drawOnChartArea: false }},
                                ticks: {{
                                    font: {{ size: 9 }},
                                    callback: function(v) {{ return '€' + v.toFixed(0); }}
                                }}
                            }}
                        }},
                        animation: {{ duration: 0 }}  // NO ANIMATION = NO FLICKER
                    }}
                }});
                mainChart.canvas.chart = mainChart;
            }}

            // ################################################################
            // Pie/Donut Charts
            // ################################################################
            function createPieCharts() {{
                const pieCtx = document.getElementById('pieChart').getContext('2d');
                pieChart = new Chart(pieCtx, {{
                    type: 'pie',
                    data: {{
                        labels: categories,
                        datasets: [{{
                            data: barData,
                            backgroundColor: colors.slice(0, categories.length).map(c => c + 'CC'),
                            borderWidth: 2,
                            borderColor: '#fff'
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {{
                            legend: {{
                                position: 'bottom',
                                labels: {{ font: {{ size: 9 }}, boxWidth: 10, padding: 6 }}
                            }},
                            title: {{
                                display: true,
                                text: 'Frequency Distribution',
                                font: {{ size: 12, weight: '600' }}
                            }}
                        }},
                        animation: {{ duration: 0 }}
                    }}
                }});
                pieChart.canvas.chart = pieChart;

                const donutCtx = document.getElementById('donutChart').getContext('2d');
                donutChart = new Chart(donutCtx, {{
                    type: 'doughnut',
                    data: {{
                        labels: categories,
                        datasets: [{{
                            data: barData,
                            backgroundColor: colors.slice(0, categories.length).map(c => c + 'CC'),
                            borderWidth: 2,
                            borderColor: '#fff'
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        cutout: '60%',
                        plugins: {{
                            legend: {{
                                position: 'bottom',
                                labels: {{ font: {{ size: 9 }}, boxWidth: 10, padding: 6 }}
                            }},
                            title: {{
                                display: true,
                                text: 'Donut Chart',
                                font: {{ size: 12, weight: '600' }}
                            }}
                        }},
                        animation: {{ duration: 0 }}
                    }}
                }});
                donutChart.canvas.chart = donutChart;
            }}

            // ################################################################
            // Radar Chart
            // ################################################################
            function createRadarChart() {{
                const ctx = document.getElementById('radarChart').getContext('2d');
                const maxBar = Math.max(...barData);
                const maxLine = Math.max(...lineData);
                
                radarChart = new Chart(ctx, {{
                    type: 'radar',
                    data: {{
                        labels: categories,
                        datasets: [{{
                            label: 'Frequency',
                            data: barData,
                            backgroundColor: 'rgba(74, 144, 217, 0.15)',
                            borderColor: '#4A90D9',
                            pointBackgroundColor: '#4A90D9',
                            pointRadius: 4,
                            borderWidth: 2
                        }}, {{
                            label: 'Price (scaled)',
                            data: lineData.map(v => (v / maxLine) * maxBar),
                            backgroundColor: 'rgba(231, 76, 60, 0.15)',
                            borderColor: '#E74C3C',
                            pointBackgroundColor: '#E74C3C',
                            pointRadius: 4,
                            borderWidth: 2
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {{
                            r: {{
                                beginAtZero: true,
                                ticks: {{ font: {{ size: 8 }}, backdropColor: 'transparent' }},
                                grid: {{ color: 'rgba(0,0,0,0.05)' }},
                                pointLabels: {{ font: {{ size: 9 }} }}
                            }}
                        }},
                        plugins: {{
                            legend: {{
                                position: 'bottom',
                                labels: {{ font: {{ size: 10 }}, padding: 10 }}
                            }}
                        }},
                        animation: {{ duration: 0 }}
                    }}
                }});
                radarChart.canvas.chart = radarChart;
            }}

            // ################################################################
            // Distribution Chart
            // ################################################################
            function createDistributionChart() {{
                const ctx = document.getElementById('distributionChart').getContext('2d');
                
                const sortedBar = [...barData].sort((a, b) => a - b);
                const minVal = sortedBar[0] || 0;
                const maxVal = sortedBar[sortedBar.length - 1] || 1;
                const range = maxVal - minVal;
                const binCount = Math.min(6, Math.max(3, Math.ceil(range / 3) + 1));
                const binSize = range / binCount || 1;
                
                const bins = Array(binCount).fill(0);
                const binLabels = [];
                
                for (let i = 0; i < binCount; i++) {{
                    const lower = minVal + i * binSize;
                    const upper = minVal + (i + 1) * binSize;
                    binLabels.push(lower.toFixed(1) + '-' + upper.toFixed(1));
                }}
                
                barData.forEach(val => {{
                    let idx = Math.floor((val - minVal) / binSize);
                    if (idx >= binCount) idx = binCount - 1;
                    if (idx < 0) idx = 0;
                    bins[idx]++;
                }});

                const gradient = ctx.createLinearGradient(0, 0, 0, 300);
                gradient.addColorStop(0, 'rgba(74, 144, 217, 0.8)');
                gradient.addColorStop(1, 'rgba(74, 144, 217, 0.3)');

                distributionChart = new Chart(ctx, {{
                    type: 'bar',
                    data: {{
                        labels: binLabels,
                        datasets: [{{
                            label: 'Frequency',
                            data: bins,
                            backgroundColor: gradient,
                            borderColor: '#4A90D9',
                            borderWidth: 2,
                            borderRadius: 6
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {{
                            legend: {{ display: false }},
                            title: {{
                                display: true,
                                text: '📊 Frequency Distribution Analysis',
                                font: {{ size: 13, weight: 'bold' }}
                            }}
                        }},
                        scales: {{
                            x: {{
                                title: {{
                                    display: true,
                                    text: 'Value Range',
                                    font: {{ size: 11, weight: '600' }}
                                }}
                            }},
                            y: {{
                                beginAtZero: true,
                                title: {{
                                    display: true,
                                    text: 'Count',
                                    font: {{ size: 11, weight: '600' }}
                                }}
                            }}
                        }},
                        animation: {{ duration: 0 }}
                    }}
                }});
                distributionChart.canvas.chart = distributionChart;
            }}

            // ################################################################
            // Toggle Dataset
            // ################################################################
            function toggleDataset(dataset) {{
                if (!mainChart) return;
                const meta = mainChart.getDatasetMeta(dataset === 'bar' ? 0 : 1);
                meta.hidden = !meta.hidden;
                mainChart.update('none');
            }}

            // ################################################################
            // Initialize
            // ################################################################
            document.addEventListener('DOMContentLoaded', function() {{
                createMainChart();
                createPieCharts();
                createRadarChart();
                createDistributionChart();
                console.log('✅ Dashboard loaded - no flicker!');
                console.log('📊 Bar = Frequency, Line = Price');
            }});

            // Keyboard shortcuts
            document.addEventListener('keydown', function(e) {{
                if (e.key === '1') toggleDataset('bar');
                if (e.key === '2') toggleDataset('line');
                if (e.key >= '3' && e.key <= '7') {{
                    const tabs = ['tab1', 'tab2', 'tab3', 'tab4', 'tab5'];
                    const idx = parseInt(e.key) - 3;
                    if (idx < tabs.length) switchTab(tabs[idx]);
                }}
            }});
        </script>
        </body>
        </html>
        """
        return html

    def resizeEvent(self, event):
        """Handle resize events without flicker"""
        super().resizeEvent(event)
        if self.is_initialized:
            self.web_view.page().runJavaScript("""
                try {
                    const charts = [window.mainChart, window.pieChart, window.donutChart, 
                                  window.radarChart, window.distributionChart];
                    charts.forEach(chart => {
                        if (chart && chart.resize) {
                            chart.resize();
                        }
                    });
                } catch(e) {
                    console.error('Resize error:', e);
                }
            """)


if __name__ == "__main__":
    # Disable hardware acceleration to prevent flicker
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseSoftwareOpenGL, True)
    
    app = QApplication(sys.argv)
    
    # Sample data - Frequency (Bar) and Price (Line)
    categories = ['Product A', 'Product B', 'Product C', 'Product D', 'Product E']
    bar_data = [42, 68, 55, 89, 73]  # Frequency
    line_data = ["125.50", "234.00", "189.75", "312.20", "267.30"]  # Price
    right_label = 'Price (€)'
    left_label = 'Frequency'
    top_label = '📊 Product Performance Dashboard'

    window = GraphData(categories, bar_data, line_data, right_label, 
                      left_label, top_label, '')
    window.setWindowTitle("Performance Dashboard")
    window.resize(1400, 850)
    window.show()
    
    sys.exit(app.exec())