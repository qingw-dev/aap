#!/usr/bin/env python3
"""
交易多智能体系统可视化演示
展示五层智能体系的拓扑逻辑和工作流程
"""

import json
from typing import Any

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from matplotlib.patches import FancyBboxPatch


class TradingSystemVisualizer:
    """交易多智能体系统可视化工具"""

    def __init__(self):
        self.G = nx.DiGraph()
        self.layer_colors = {
            "strategic": "#FF6B6B",  # 红色 - 战略层
            "tactical": "#4ECDC4",  # 青色 - 战术层
            "execution": "#45B7D1",  # 蓝色 - 执行层
            "monitoring": "#96CEB4",  # 绿色 - 监控层
            "coordination": "#FECA57",  # 黄色 - 协调层
        }
        self._build_network()

    def _build_network(self):
        """构建智能体网络拓扑"""
        # 定义各层智能体
        agents = {
            "strategic": ["PortfolioManager", "RiskManager", "MacroAnalysis"],
            "tactical": ["StrategyResearch", "MarketAnalysis", "AssetAllocation"],
            "execution": ["OrderExecution", "PositionManager", "LiquidityManager"],
            "monitoring": ["RealTimeRisk", "Compliance", "SystemMonitor"],
            "coordination": [
                "TaskScheduler",
                "CommunicationCoordinator",
                "LearningOptimization",
            ],
        }

        # 添加节点
        for layer, agent_list in agents.items():
            for agent in agent_list:
                self.G.add_node(
                    agent, layer=layer, color=self.layer_colors[layer], size=2000
                )

        # 定义连接关系（基于实际工作流程）
        connections = [
            # 战略层内部
            ("PortfolioManager", "RiskManager"),
            ("RiskManager", "MacroAnalysis"),
            ("MacroAnalysis", "PortfolioManager"),
            # 战略层到战术层
            ("PortfolioManager", "StrategyResearch"),
            ("RiskManager", "AssetAllocation"),
            ("MacroAnalysis", "MarketAnalysis"),
            # 战术层内部
            ("StrategyResearch", "MarketAnalysis"),
            ("MarketAnalysis", "AssetAllocation"),
            ("AssetAllocation", "StrategyResearch"),
            # 战术层到执行层
            ("StrategyResearch", "OrderExecution"),
            ("AssetAllocation", "PositionManager"),
            ("MarketAnalysis", "LiquidityManager"),
            # 执行层内部
            ("OrderExecution", "PositionManager"),
            ("PositionManager", "LiquidityManager"),
            ("LiquidityManager", "OrderExecution"),
            # 执行层到监控层
            ("OrderExecution", "RealTimeRisk"),
            ("PositionManager", "Compliance"),
            ("LiquidityManager", "SystemMonitor"),
            # 监控层到协调层
            ("RealTimeRisk", "TaskScheduler"),
            ("Compliance", "CommunicationCoordinator"),
            ("SystemMonitor", "LearningOptimization"),
            # 协调层到各层
            ("TaskScheduler", "PortfolioManager"),
            ("CommunicationCoordinator", "StrategyResearch"),
            ("LearningOptimization", "OrderExecution"),
            # 监控层反馈
            ("RealTimeRisk", "RiskManager"),
            ("Compliance", "PortfolioManager"),
            ("SystemMonitor", "TaskScheduler"),
        ]

        # 添加边
        for source, target in connections:
            if source in self.G.nodes and target in self.G.nodes:
                self.G.add_edge(source, target, weight=1.0)

    def draw_system_topology(self, save_path: str = "trading_system_topology.png"):
        """绘制系统拓扑图"""
        fig, ax = plt.subplots(1, 1, figsize=(20, 16))

        # 创建分层布局
        pos = {}
        layer_y = {
            "strategic": 4,
            "tactical": 3,
            "execution": 2,
            "monitoring": 1,
            "coordination": 0,
        }

        # 为每层分配x坐标
        layer_agents = {}
        for agent, data in self.G.nodes(data=True):
            layer = data["layer"]
            if layer not in layer_agents:
                layer_agents[layer] = []
            layer_agents[layer].append(agent)

        for layer, agents in layer_agents.items():
            y = layer_y[layer]
            x_positions = np.linspace(1, 9, len(agents))
            for i, agent in enumerate(agents):
                pos[agent] = (x_positions[i], y)

        # 绘制节点
        for layer, color in self.layer_colors.items():
            layer_nodes = [
                n for n in self.G.nodes() if self.G.nodes[n]["layer"] == layer
            ]
            if layer_nodes:
                nx.draw_networkx_nodes(
                    self.G,
                    pos,
                    nodelist=layer_nodes,
                    node_color=color,
                    node_size=2000,
                    alpha=0.8,
                    ax=ax,
                )

        # 绘制边
        nx.draw_networkx_edges(
            self.G,
            pos,
            arrowstyle="->",
            arrowsize=20,
            edge_color="gray",
            alpha=0.6,
            width=2,
            ax=ax,
        )

        # 绘制标签
        nx.draw_networkx_labels(self.G, pos, font_size=10, font_weight="bold", ax=ax)

        # 添加层标签背景
        for layer, y in layer_y.items():
            bbox = FancyBboxPatch(
                (0.5, y - 0.3),
                8,
                0.6,
                boxstyle="round,pad=0.1",
                facecolor=self.layer_colors[layer],
                alpha=0.2,
                edgecolor="black",
                linewidth=2,
            )
            ax.add_patch(bbox)
            ax.text(
                4.5,
                y,
                f"{layer.upper()} LAYER",
                ha="center",
                va="center",
                fontsize=14,
                weight="bold",
            )

        # 设置图表属性
        ax.set_xlim(0, 10)
        ax.set_ylim(-0.5, 4.5)
        ax.set_title(
            "Trading Multi-Agent System Topology", fontsize=20, weight="bold", pad=20
        )
        ax.set_aspect("equal")
        ax.grid(True, alpha=0.3)

        # 隐藏坐标轴
        ax.set_xticks([])
        ax.set_yticks([])

        # 添加图例
        legend_elements = [
            mpatches.Patch(color=color, label=layer.upper())
            for layer, color in self.layer_colors.items()
        ]
        ax.legend(handles=legend_elements, loc="upper right", bbox_to_anchor=(1.15, 1))

        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        plt.close()

        print(f"系统拓扑图已保存到: {save_path}")

    def draw_data_flow(self, save_path: str = "data_flow_diagram.png"):
        """绘制数据流图"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle("Trading System Data Flow", fontsize=18, weight="bold")

        # 1. 战略决策流程
        strategic_flow = [
            "宏观数据 →",
            "宏观分析 →",
            "风险评估 →",
            "投资目标 →",
            "资产配置",
        ]

        ax1.text(
            0.5,
            0.5,
            "\n".join(strategic_flow),
            ha="center",
            va="center",
            fontsize=12,
            weight="bold",
            bbox=dict(
                boxstyle="round,pad=0.5",
                facecolor=self.layer_colors["strategic"],
                alpha=0.7,
            ),
        )
        ax1.set_title("Strategic Decision Flow", fontsize=14, weight="bold")
        ax1.set_xlim(0, 1)
        ax1.set_ylim(0, 1)
        ax1.axis("off")

        # 2. 战术决策流程
        tactical_flow = [
            "市场数据 →",
            "策略研发 →",
            "策略验证 →",
            "市场分析 →",
            "交易信号",
        ]

        ax2.text(
            0.5,
            0.5,
            "\n".join(tactical_flow),
            ha="center",
            va="center",
            fontsize=12,
            weight="bold",
            bbox=dict(
                boxstyle="round,pad=0.5",
                facecolor=self.layer_colors["tactical"],
                alpha=0.7,
            ),
        )
        ax2.set_title("Tactical Decision Flow", fontsize=14, weight="bold")
        ax2.set_xlim(0, 1)
        ax2.set_ylim(0, 1)
        ax2.axis("off")

        # 3. 执行决策流程
        execution_flow = [
            "交易信号 →",
            "订单执行 →",
            "流动性评估 →",
            "执行算法 →",
            "订单提交",
        ]

        ax3.text(
            0.5,
            0.5,
            "\n".join(execution_flow),
            ha="center",
            va="center",
            fontsize=12,
            weight="bold",
            bbox=dict(
                boxstyle="round,pad=0.5",
                facecolor=self.layer_colors["execution"],
                alpha=0.7,
            ),
        )
        ax3.set_title("Execution Decision Flow", fontsize=14, weight="bold")
        ax3.set_xlim(0, 1)
        ax3.set_ylim(0, 1)
        ax3.axis("off")

        # 4. 监控决策流程
        monitoring_flow = [
            "实时数据 →",
            "风险计算 →",
            "阈值检查 →",
            "警报生成 →",
            "应急处理",
        ]

        ax4.text(
            0.5,
            0.5,
            "\n".join(monitoring_flow),
            ha="center",
            va="center",
            fontsize=12,
            weight="bold",
            bbox=dict(
                boxstyle="round,pad=0.5",
                facecolor=self.layer_colors["monitoring"],
                alpha=0.7,
            ),
        )
        ax4.set_title("Monitoring Decision Flow", fontsize=14, weight="bold")
        ax4.set_xlim(0, 1)
        ax4.set_ylim(0, 1)
        ax4.axis("off")

        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        plt.close()

        print(f"数据流图已保存到: {save_path}")

    def generate_interactive_dashboard(self, save_path: str = "trading_dashboard.html"):
        """生成交互式仪表板"""
        html_content = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>交易多智能体系统仪表板</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        .layer-section {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 20px;
            margin: 20px 0;
            backdrop-filter: blur(10px);
        }
        .agent-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }
        .agent-card {
            background: rgba(255, 255, 255, 0.2);
            border-radius: 10px;
            padding: 15px;
            text-align: center;
            transition: transform 0.3s ease;
        }
        .agent-card:hover {
            transform: translateY(-5px);
        }
        .status-indicator {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            display: inline-block;
            margin-right: 8px;
        }
        .status-active { background-color: #4CAF50; }
        .status-warning { background-color: #FF9800; }
        .status-error { background-color: #F44336; }
        .chart-container {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 20px;
            margin: 20px 0;
        }
        .workflow-timeline {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin: 20px 0;
        }
        .timeline-step {
            flex: 1;
            text-align: center;
            padding: 10px;
            border-radius: 5px;
            margin: 0 5px;
            position: relative;
        }
        .timeline-step::after {
            content: '→';
            position: absolute;
            right: -15px;
            top: 50%;
            transform: translateY(-50%);
        }
        .timeline-step:last-child::after {
            display: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 交易多智能体系统仪表板</h1>
            <p>五层智能体系实时监控面板</p>
        </div>
        
        <!-- 系统概览 -->
        <div class="layer-section">
            <h2>📊 系统概览</h2>
            <div class="chart-container">
                <canvas id="systemChart" width="400" height="200"></canvas>
            </div>
        </div>
        
        <!-- 战略层 -->
        <div class="layer-section" style="border-left: 5px solid #FF6B6B;">
            <h2>🏛️ 战略层 (Strategic Layer)</h2>
            <div class="agent-grid">
                <div class="agent-card">
                    <div class="status-indicator status-active"></div>
                    <h4>投资组合管理</h4>
                    <p>资产配置: 60/30/10</p>
                    <small>夏普比率: 1.25</small>
                </div>
                <div class="agent-card">
                    <div class="status-indicator status-active"></div>
                    <h4>风险管理</h4>
                    <p>VaR: 2.1%</p>
                    <small>状态: 正常</small>
                </div>
                <div class="agent-card">
                    <div class="status-indicator status-warning"></div>
                    <h4>宏观分析</h4>
                    <p>市场情绪: 谨慎</p>
                    <small>更新: 5分钟前</small>
                </div>
            </div>
        </div>
        
        <!-- 战术层 -->
        <div class="layer-section" style="border-left: 5px solid #4ECDC4;">
            <h2>⚔️ 战术层 (Tactical Layer)</h2>
            <div class="agent-grid">
                <div class="agent-card">
                    <div class="status-indicator status-active"></div>
                    <h4>策略研发</h4>
                    <p>信号: 买入</p>
                    <small>置信度: 75%</small>
                </div>
                <div class="agent-card">
                    <div class="status-indicator status-active"></div>
                    <h4>市场分析</h4>
                    <p>趋势: 上升</p>
                    <small>强度: 中等</small>
                </div>
                <div class="agent-card">
                    <div class="status-indicator status-active"></div>
                    <h4>资产配置</h4>
                    <p>权重: 优化中</p>
                    <small>目标: 最大夏普</small>
                </div>
            </div>
        </div>
        
        <!-- 执行层 -->
        <div class="layer-section" style="border-left: 5px solid #45B7D1;">
            <h2>🚀 执行层 (Execution Layer)</h2>
            <div class="agent-grid">
                <div class="agent-card">
                    <div class="status-indicator status-active"></div>
                    <h4>订单执行</h4>
                    <p>算法: VWAP</p>
                    <small>进度: 65%</small>
                </div>
                <div class="agent-card">
                    <div class="status-indicator status-active"></div>
                    <h4>仓位管理</h4>
                    <p>杠杆: 1.2x</p>
                    <small>状态: 正常</small>
                </div>
                <div class="agent-card">
                    <div class="status-indicator status-active"></div>
                    <h4>流动性管理</h4>
                    <p>深度: 充足</p>
                    <small>价差: 0.01%</small>
                </div>
            </div>
        </div>
        
        <!-- 监控层 -->
        <div class="layer-section" style="border-left: 5px solid #96CEB4;">
            <h2>👁️ 监控层 (Monitoring Layer)</h2>
            <div class="agent-grid">
                <div class="agent-card">
                    <div class="status-indicator status-warning"></div>
                    <h4>实时风控</h4>
                    <p>警报: 1个</p>
                    <small>级别: 中等</small>
                </div>
                <div class="agent-card">
                    <div class="status-indicator status-active"></div>
                    <h4>合规检查</h4>
                    <p>状态: 合规</p>
                    <small>检查: 实时</small>
                </div>
                <div class="agent-card">
                    <div class="status-indicator status-active"></div>
                    <h4>系统监控</h4>
                    <p>延迟: 2ms</p>
                    <small>可用性: 99.9%</small>
                </div>
            </div>
        </div>
        
        <!-- 协调层 -->
        <div class="layer-section" style="border-left: 5px solid #FECA57;">
            <h2>🎯 协调层 (Coordination Layer)</h2>
            <div class="agent-grid">
                <div class="agent-card">
                    <div class="status-indicator status-active"></div>
                    <h4>任务调度</h4>
                    <p>队列: 3个任务</p>
                    <small>优先级: 动态</small>
                </div>
                <div class="agent-card">
                    <div class="status-indicator status-active"></div>
                    <h4>通信协调</h4>
                    <p>消息: 156条/分钟</p>
                    <small>延迟: <1ms</small>
                </div>
                <div class="agent-card">
                    <div class="status-indicator status-active"></div>
                    <h4>学习优化</h4>
                    <p>模型: 更新中</p>
                    <small>性能: +2.3%</small>
                </div>
            </div>
        </div>
        
        <!-- 工作流程时间线 -->
        <div class="layer-section">
            <h2>⏱️ 工作流程时间线</h2>
            <div class="workflow-timeline">
                <div class="timeline-step" style="background: #FF6B6B;">
                    <strong>战略决策</strong><br>
                    <small>资产配置</small>
                </div>
                <div class="timeline-step" style="background: #4ECDC4;">
                    <strong>战术制定</strong><br>
                    <small>策略生成</small>
                </div>
                <div class="timeline-step" style="background: #45B7D1;">
                    <strong>执行实施</strong><br>
                    <small>订单执行</small>
                </div>
                <div class="timeline-step" style="background: #96CEB4;">
                    <strong>监控反馈</strong><br>
                    <small>风险控制</small>
                </div>
                <div class="timeline-step" style="background: #FECA57;">
                    <strong>协调优化</strong><br>
                    <small>系统调优</small>
                </div>
            </div>
        </div>
        
        <!-- 实时数据图表 -->
        <div class="layer-section">
            <h2>📈 实时性能监控</h2>
            <div class="chart-container">
                <canvas id="performanceChart" width="400" height="200"></canvas>
            </div>
        </div>
    </div>

    <script>
        // 系统状态图表
        const ctx1 = document.getElementById('systemChart').getContext('2d');
        new Chart(ctx1, {
            type: 'doughnut',
            data: {
                labels: ['战略层', '战术层', '执行层', '监控层', '协调层'],
                datasets: [{
                    data: [3, 3, 3, 3, 3],
                    backgroundColor: ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57'],
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { color: 'white' }
                    }
                }
            }
        });

        // 性能监控图表
        const ctx2 = document.getElementById('performanceChart').getContext('2d');
        new Chart(ctx2, {
            type: 'line',
            data: {
                labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00'],
                datasets: [{
                    label: '系统响应时间 (ms)',
                    data: [12, 19, 8, 15, 10, 5],
                    borderColor: '#4ECDC4',
                    backgroundColor: 'rgba(78, 205, 196, 0.1)',
                    tension: 0.4
                }, {
                    label: '任务完成率 (%)',
                    data: [95, 90, 98, 92, 96, 99],
                    borderColor: '#96CEB4',
                    backgroundColor: 'rgba(150, 206, 180, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        labels: { color: 'white' }
                    }
                },
                scales: {
                    x: { ticks: { color: 'white' } },
                    y: { ticks: { color: 'white' } }
                }
            }
        });

        // 实时更新状态
        setInterval(() => {
            // 模拟数据更新
            const now = new Date().toLocaleTimeString();
            console.log(`系统更新于: ${now}`);
        }, 5000);
    </script>
</body>
</html>
        """

        with open(save_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        print(f"交互式仪表板已生成: {save_path}")

    def generate_system_report(self) -> dict[str, Any]:
        """生成系统报告"""
        report = {
            "system_overview": {
                "total_agents": len(self.G.nodes()),
                "total_connections": len(self.G.edges()),
                "layers": list(self.layer_colors.keys()),
                "network_density": nx.density(self.G),
            },
            "layer_details": {},
            "critical_paths": [],
            "recommendations": [],
        }

        # 分析各层
        for layer, color in self.layer_colors.items():
            layer_nodes = [
                n for n in self.G.nodes() if self.G.nodes[n]["layer"] == layer
            ]
            report["layer_details"][layer] = {
                "agents": layer_nodes,
                "count": len(layer_nodes),
                "color": color,
            }

        # 识别关键路径
        try:
            # 计算中心性
            centrality = nx.betweenness_centrality(self.G)
            top_agents = sorted(centrality.items(), key=lambda x: x[1], reverse=True)[
                :3
            ]
            report["critical_paths"] = [
                {"agent": agent, "centrality": score} for agent, score in top_agents
            ]
        except:
            pass

        # 生成建议
        report["recommendations"] = [
            "建议增加监控层到执行层的直接反馈路径",
            "考虑在协调层添加负载均衡机制",
            "建议为高频交易场景优化执行层算法",
            "考虑增加跨市场套利智能体",
            "建议实施实时A/B测试框架",
        ]

        return report


def main():
    """主函数 - 生成所有可视化"""
    print("🤖 正在生成交易多智能体系统可视化...")

    # 创建可视化工具
    visualizer = TradingSystemVisualizer()

    # 生成拓扑图
    visualizer.draw_system_topology("trading_system_topology.png")

    # 生成数据流图
    visualizer.draw_data_flow("data_flow_diagram.png")

    # 生成交互式仪表板
    visualizer.generate_interactive_dashboard("trading_dashboard.html")

    # 生成系统报告
    report = visualizer.generate_system_report()

    # 保存报告
    with open("system_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print("\n✅ 可视化生成完成!")
    print("📊 生成的文件:")
    print("   - trading_system_topology.png: 系统拓扑图")
    print("   - data_flow_diagram.png: 数据流图")
    print("   - trading_dashboard.html: 交互式仪表板")
    print("   - system_report.json: 系统分析报告")

    print("\n📈 系统概览:")
    print(f"   总智能体数量: {report['system_overview']['total_agents']}")
    print(f"   总连接数量: {report['system_overview']['total_connections']}")
    print(f"   网络密度: {report['system_overview']['network_density']:.3f}")

    print("\n🏛️ 各层智能体分布:")
    for layer, details in report["layer_details"].items():
        print(f"   {layer.upper()}: {details['count']} 个智能体")


if __name__ == "__main__":
    main()
