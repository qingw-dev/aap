"""
Pydantic-based Trading Multi-Agent System
Modern Python 3.11+ implementation with type hints and Pydantic models
"""

import asyncio
import json
import logging
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from enum import StrEnum
from typing import Any, Literal

from aworld.agents.llm_agent import Agent
from aworld.config.conf import AgentConfig
from pydantic import BaseModel, Field, ValidationInfo, field_validator

from ..mcp_config import MCP_CONFIG


class LayerType(StrEnum):
    """Agent layer types for the trading system"""

    STRATEGIC = "strategic"
    TACTICAL = "tactical"
    EXECUTION = "execution"
    MONITORING = "monitoring"
    COORDINATION = "coordination"


class MessageType(StrEnum):
    """Message types for inter-agent communication"""

    COMMAND = "command"
    QUERY = "query"
    RESPONSE = "response"
    ALERT = "alert"
    HEARTBEAT = "heartbeat"


class Priority(StrEnum):
    """Message priority levels"""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TradingMessage(BaseModel):
    """Standardized message format for trading system communication"""

    message_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    timestamp: datetime = Field(default_factory=datetime.now)
    source_layer: LayerType
    source_agent: str
    target_layer: LayerType
    target_agent: str
    message_type: MessageType
    priority: Priority
    payload: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)

    class Config:
        """Pydantic configuration"""

        use_enum_values = True
        validate_assignment = True


class RiskMetrics(BaseModel):
    """Risk assessment metrics"""

    portfolio_var: float = Field(ge=0, description="Portfolio Value at Risk")
    expected_shortfall: float = Field(ge=0, description="Expected Shortfall")
    max_drawdown: float = Field(ge=0, description="Maximum Drawdown")
    beta: float = Field(description="Portfolio Beta")
    risk_limits: dict[str, float] = Field(default_factory=dict)


class Allocation(BaseModel):
    """Asset allocation configuration"""

    stocks: float = Field(ge=0, le=1, description="Stock allocation percentage")
    bonds: float = Field(ge=0, le=1, description="Bond allocation percentage")
    cash: float = Field(ge=0, le=1, description="Cash allocation percentage")
    rebalance_trigger: float = Field(
        ge=0, le=1, description="Rebalancing trigger threshold"
    )

    @field_validator("stocks", "bonds", "cash")
    @classmethod
    def validate_allocation_sum(cls, v: float, info: ValidationInfo) -> float:
        """Ensure allocation percentages sum to 1"""
        values = info.data
        total = sum(values.get(k, 0) for k in ["stocks", "bonds", "cash"])
        if total > 1:
            raise ValueError("Allocation percentages must sum to <= 1")
        return v


class TradingSignal(BaseModel):
    """Trading signal structure"""

    signal: Literal["BUY", "SELL", "HOLD"]
    confidence: float = Field(ge=0, le=1, description="Signal confidence level")
    entry_price: float | None = Field(ge=0, description="Entry price for BUY signals")
    stop_loss: float | None = Field(ge=0, description="Stop loss price")
    take_profit: float | None = Field(ge=0, description="Take profit price")
    position_size: float | None = Field(
        ge=0, le=1, description="Position size as portfolio percentage"
    )
    reason: str | None = Field(default=None, description="Reason for HOLD signals")


class BacktestStats(BaseModel):
    """Backtesting performance statistics"""

    sharpe_ratio: float = Field(description="Sharpe ratio")
    max_drawdown: float = Field(ge=0, description="Maximum drawdown")
    win_rate: float = Field(ge=0, le=1, description="Winning trade percentage")
    profit_factor: float = Field(ge=0, description="Profit factor")


class OrderPlan(BaseModel):
    """Order execution plan"""

    order_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    symbol: str = Field(min_length=1, description="Trading symbol")
    side: Literal["BUY", "SELL"] = Field(description="Order side")
    quantity: int = Field(gt=0, description="Order quantity")
    order_type: str = Field(default="LIMIT", description="Order type")
    price: float = Field(gt=0, description="Order price")
    algorithm: str = Field(default="VWAP", description="Execution algorithm")
    expected_slippage: float = Field(
        default=0.0, description="Expected slippage percentage"
    )
    estimated_fees: float = Field(default=0.0, description="Estimated trading fees")


class Alert(BaseModel):
    """System alert structure"""

    type: str = Field(description="Alert type")
    severity: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"] = Field(
        description="Alert severity"
    )
    message: str = Field(description="Alert message")
    timestamp: datetime = Field(default_factory=datetime.now)


class Task(BaseModel):
    """Scheduled task structure"""

    task_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    task_type: str = Field(description="Task type identifier")
    priority: Priority
    created_at: datetime = Field(default_factory=datetime.now)
    status: Literal["queued", "processing", "completed", "failed"] = Field(
        default="queued"
    )
    payload: dict[str, Any] = Field(default_factory=dict)


class AgentState(BaseModel):
    """Agent state tracking"""

    agent_id: str
    name: str
    layer: LayerType
    status: Literal["idle", "processing", "error", "maintenance"] = Field(
        default="idle"
    )
    last_activity: datetime = Field(default_factory=datetime.now)
    memory_usage: dict[str, Any] = Field(default_factory=dict)


class TradingAgent(ABC):
    """Abstract base class for trading agents with Pydantic-based configuration"""

    def __init__(
        self,
        name: str,
        layer: LayerType,
        config: AgentConfig,
        system_prompt: str = "",
        tools: list[str] | None = None,
    ) -> None:
        self.agent_id = str(uuid.uuid4())
        self.name = name
        self.layer = layer
        self.config = config
        self.system_prompt = system_prompt
        self.tools = tools or []
        self.state = "idle"
        self.memory: dict[str, Any] = {}

        # Create underlying LLM agent
        self.llm_agent = Agent(
            agent_id=self.agent_id,
            name=name,
            desc=f"{layer.value} layer trading agent",
            conf=config,
            system_prompt=system_prompt,
            mcp_servers=tools,
            mcp_config=MCP_CONFIG,
        )

    async def process_message(self, message: TradingMessage) -> TradingMessage:
        """Process incoming message with error handling"""
        try:
            self.state = "processing"

            # Record message to memory
            self.memory[str(message.message_id)] = {
                "received": message.model_dump(),
                "processed_at": datetime.now().isoformat(),
            }

            # Process logic implemented by subclasses
            response = await self._process_logic(message)

            self.state = "idle"
            return response

        except Exception as e:
            logging.error(f"Agent {self.name} processing error: {e}")
            self.state = "error"
            return self._create_error_response(message, str(e))

    @abstractmethod
    async def _process_logic(self, message: TradingMessage) -> TradingMessage:
        """Specific processing logic implemented by subclasses"""

    def _create_response(
        self,
        original_message: TradingMessage,
        payload: dict[str, Any],
        message_type: MessageType = MessageType.RESPONSE,
    ) -> TradingMessage:
        """Create response message"""
        return TradingMessage(
            source_layer=self.layer,
            source_agent=self.name,
            target_layer=original_message.source_layer,
            target_agent=original_message.source_agent,
            message_type=message_type,
            priority=original_message.priority,
            payload=payload,
            metadata={"response_to": str(original_message.message_id)},
        )

    def _create_error_response(
        self, original_message: TradingMessage, error_message: str
    ) -> TradingMessage:
        """Create error response message"""
        return self._create_response(
            original_message,
            {"error": error_message, "status": "failed"},
            MessageType.ALERT,
        )


class PortfolioManagerAgent(TradingAgent):
    """Portfolio management agent for strategic layer"""

    def __init__(self, config: AgentConfig) -> None:
        super().__init__(
            name="PortfolioManager",
            layer=LayerType.STRATEGIC,
            config=config,
            system_prompt="""
            You are a portfolio management expert responsible for overall investment strategy and asset allocation decisions.
            Key responsibilities:
            1. Develop investment strategies based on macro analysis
            2. Optimize asset allocation weights
            3. Control overall portfolio risk
            4. Evaluate investment performance and attribution analysis

            Based on market information and risk parameters, provide optimal asset allocation recommendations.
            """,
            tools=["search", "browser-use", "think"],
        )

    async def _process_logic(self, message: TradingMessage) -> TradingMessage:
        """Process portfolio management logic"""
        if message.message_type == MessageType.QUERY:
            # Generate allocation based on market conditions
            allocation = Allocation(
                stocks=0.6,
                bonds=0.3,
                cash=0.1,
                rebalance_trigger=0.05,
            )

            return self._create_response(
                message,
                {
                    "allocation": allocation.model_dump(),
                    "expected_return": 0.08,
                    "expected_volatility": 0.15,
                    "sharpe_ratio": 0.53,
                    "timestamp": datetime.now().isoformat(),
                },
            )

        return self._create_response(
            message, {"status": "received", "agent": self.name}
        )


class RiskManagerAgent(TradingAgent):
    """Risk management agent for strategic layer"""

    def __init__(self, config: AgentConfig) -> None:
        super().__init__(
            name="RiskManager",
            layer=LayerType.STRATEGIC,
            config=config,
            system_prompt="""
            You are a risk management expert responsible for assessing and controlling portfolio risk.
            Key responsibilities:
            1. Calculate VaR and expected tail loss
            2. Set risk limits and warning thresholds
            3. Conduct stress testing and scenario analysis
            4. Monitor risk concentration

            Based on current positions and market conditions, provide comprehensive risk assessment reports.
            """,
            tools=["search", "think", "document"],
        )

    async def _process_logic(self, message: TradingMessage) -> TradingMessage:
        """Process risk management logic"""
        # Calculate risk metrics
        risk_metrics = RiskMetrics(
            portfolio_var=0.02,  # 2% daily VaR
            expected_shortfall=0.035,
            max_drawdown=0.15,
            beta=1.1,
            risk_limits={
                "max_position_size": 0.1,
                "max_sector_exposure": 0.25,
                "stop_loss": 0.05,
            },
        )

        return self._create_response(
            message,
            {
                "risk_metrics": risk_metrics.model_dump(),
                "risk_status": "within_limits",
                "recommendations": [
                    "Consider reducing tech sector exposure",
                    "Implement tighter stop-losses",
                    "Increase cash allocation",
                ],
            },
        )


class StrategyResearchAgent(TradingAgent):
    """Strategy research agent for tactical layer"""

    def __init__(self, config: AgentConfig) -> None:
        super().__init__(
            name="StrategyResearch",
            layer=LayerType.TACTICAL,
            config=config,
            system_prompt="""
            You are a strategy research expert responsible for developing trading strategies and signals.
            Key responsibilities:
            1. Research and develop trading strategies
            2. Generate trading signals based on technical and fundamental analysis
            3. Conduct backtesting and performance evaluation
            4. Strategy parameter tuning
            
            2. Consider risk tolerance and market conditions
            3. Minimize transaction costs and market impact
            4. Provide clear reasoning for recommendations
            
            Based on historical data and market characteristics, provide feasible trading strategy recommendations.
            """,
            tools=["search", "think", "code", "browser-use"],
        )

    async def _process_logic(self, message: TradingMessage) -> TradingMessage:
        """Process strategy research logic"""
        strategy_type = message.payload.get("strategy_type", "momentum")

        # Generate trading signal based on strategy type
        signal = TradingSignal(
            signal="BUY",
            confidence=0.75,
            entry_price=100.0,
            stop_loss=95.0,
            take_profit=110.0,
            position_size=0.05,
        )

        # Backtest statistics
        backtest_stats = BacktestStats(
            sharpe_ratio=1.2,
            max_drawdown=0.08,
            win_rate=0.65,
            profit_factor=1.5,
        )

        return self._create_response(
            message,
            {
                "strategy_type": strategy_type,
                "signals": signal.model_dump(),
                "backtest_stats": backtest_stats.model_dump(),
            },
        )


class OrderExecutionAgent(TradingAgent):
    """Order execution agent for execution layer"""

    def __init__(self, config: AgentConfig) -> None:
        super().__init__(
            name="OrderExecution",
            layer=LayerType.EXECUTION,
            config=config,
            system_prompt="""
            You are an order execution expert responsible for optimizing trade execution quality.
            Key responsibilities:
            1. Select optimal execution algorithms
            2. Manage order routing and splitting
            3. Minimize market impact costs
            4. Monitor execution quality and slippage
            
            Based on trading signals and market conditions, develop optimal execution plans.
            """,
            tools=["browser-use", "code"],
        )

    async def _process_logic(self, message: TradingMessage) -> TradingMessage:
        """Process order execution logic"""
        order_request = message.payload.get("order", {})

        # Create execution plan
        order_plan = OrderPlan(
            symbol=order_request.get("symbol", "AAPL"),
            side=order_request.get("side", "BUY"),
            quantity=order_request.get("quantity", 100),
            price=order_request.get("price", 100.0),
        )

        return self._create_response(
            message,
            {
                "execution_plan": order_plan.model_dump(),
                "status": "pending_execution",
                "estimated_completion": "2024-01-01T10:30:00Z",
            },
        )


class RealTimeRiskAgent(TradingAgent):
    """Real-time risk monitoring agent for monitoring layer"""

    def __init__(self, config: AgentConfig) -> None:
        super().__init__(
            name="RealTimeRisk",
            layer=LayerType.MONITORING,
            config=config,
            system_prompt="""
            You are a real-time risk monitoring expert responsible for monitoring trading risks.
            Key responsibilities:
            1. Calculate risk indicators in real-time
            2. Monitor risk limits and thresholds
            3. Detect abnormal trading behavior
            4. Trigger risk alerts and emergency measures
            
            Based on real-time data, provide risk monitoring reports and early warning information.
            """,
            tools=["think", "document"],
        )

    async def _process_logic(self, message: TradingMessage) -> TradingMessage:
        """Process real-time risk monitoring logic"""
        # Calculate real-time risk
        risk_check = {
            "current_var": 0.018,
            "exposure_check": "PASSED",
            "margin_usage": 0.65,
            "alerts": [
                Alert(
                    type="POSITION_SIZE",
                    severity="MEDIUM",
                    message="Tech sector exposure approaching limit",
                ).model_dump()
            ],
        }

        return self._create_response(
            message,
            {
                "risk_status": risk_check,
                "action_required": len(risk_check["alerts"]) > 0,
                "next_check": "2024-01-01T10:05:00Z",
            },
        )


class TaskSchedulerAgent(TradingAgent):
    """Task scheduling agent for coordination layer"""

    def __init__(self, config: AgentConfig) -> None:
        super().__init__(
            name="TaskScheduler",
            layer=LayerType.COORDINATION,
            config=config,
            system_prompt="""
            You are a task scheduling expert responsible for coordinating work across agent layers.
            Key responsibilities:
            1. Task priority management
            2. Resource allocation and load balancing
            3. Failure detection and recovery
            4. Performance monitoring and optimization
            
            Based on system load and task requirements, develop optimal scheduling plans.
            """,
            tools=["think"],
        )
        self.task_queue: list[Task] = []
        self.agent_registry: dict[str, AgentState] = {}

    async def _process_logic(self, message: TradingMessage) -> TradingMessage:
        """Process task scheduling logic"""
        if message.message_type == MessageType.COMMAND:
            task_data = message.payload.get("task", {})

            # Create new task
            task = Task(
                task_type=task_data.get("type", "default"),
                priority=message.priority,
                payload=task_data,
            )

            # Add to task queue
            self.task_queue.append(task)

            # Sort by priority
            self.task_queue.sort(key=lambda t: t.priority, reverse=True)

            return self._create_response(
                message,
                {
                    "task_id": str(task.task_id),
                    "queue_position": len(self.task_queue),
                    "estimated_start": "2024-01-01T10:01:00Z",
                },
            )

        return self._create_response(
            message, {"status": "scheduler_active", "queue_size": len(self.task_queue)}
        )


class TradingWorkflowResult(BaseModel):
    """Result structure for complete trading workflow"""

    portfolio_allocation: dict[str, Any] | None = None
    risk_assessment: dict[str, Any] | None = None
    strategy_recommendation: dict[str, Any] | None = None
    execution_plan: dict[str, Any] | None = None
    risk_monitoring: dict[str, Any] | None = None
    success: bool = True
    errors: list[str] = []


class TradingMultiAgentSystem:
    """
    Main controller for trading multi-agent system
    with Pydantic-based configuration
    """

    def __init__(self, config: AgentConfig) -> None:
        self.config = config
        self.agents: dict[str, TradingAgent] = {}
        self.message_bus: list[TradingMessage] = []
        self.system_status: str = "initialized"
        self.agent_registry: dict[str, AgentState] = {}

        # Initialize all agents
        self._initialize_agents()

    def _initialize_agents(self) -> None:
        """Initialize all trading agents"""
        # Strategic layer
        self.agents["portfolio_manager"] = PortfolioManagerAgent(self.config)
        self.agents["risk_manager"] = RiskManagerAgent(self.config)

        # Tactical layer
        self.agents["strategy_research"] = StrategyResearchAgent(self.config)

        # Execution layer
        self.agents["order_execution"] = OrderExecutionAgent(self.config)

        # Monitoring layer
        self.agents["realtime_risk"] = RealTimeRiskAgent(self.config)

        # Coordination layer
        self.agents["task_scheduler"] = TaskSchedulerAgent(self.config)

        # Register agent states
        for agent_id, agent in self.agents.items():
            self.agent_registry[agent_id] = AgentState(
                agent_id=agent_id,
                name=agent.name,
                layer=agent.layer,
            )

        self.system_status = "ready"

    async def send_message(self, message: TradingMessage) -> TradingMessage:
        """Send message to target agent with validation"""
        target_agent = self.agents.get(message.target_agent)
        if not target_agent:
            return TradingMessage(
                source_layer=LayerType.COORDINATION,
                source_agent="system",
                target_layer=message.target_layer,
                target_agent=message.target_agent,
                message_type=MessageType.ALERT,
                priority=Priority.HIGH,
                payload={"error": "Agent not found"},
                metadata={"original_message_id": str(message.message_id)},
            )

        return await target_agent.process_message(message)

    async def execute_trading_workflow(
        self, market_data: dict[str, Any]
    ) -> TradingWorkflowResult:
        """Execute complete trading workflow with structured results"""
        result = TradingWorkflowResult()

        try:
            # 1. Strategic layer decision
            portfolio_msg = TradingMessage(
                source_layer=LayerType.COORDINATION,
                source_agent="system",
                target_layer=LayerType.STRATEGIC,
                target_agent="portfolio_manager",
                message_type=MessageType.QUERY,
                priority=Priority.HIGH,
                payload={"market_data": market_data},
                metadata={"workflow_step": "strategic_decision"},
            )

            portfolio_response = await self.send_message(portfolio_msg)
            result.portfolio_allocation = portfolio_response.payload

            # 2. Risk assessment
            risk_msg = TradingMessage(
                source_layer=LayerType.COORDINATION,
                source_agent="system",
                target_layer=LayerType.STRATEGIC,
                target_agent="risk_manager",
                message_type=MessageType.QUERY,
                priority=Priority.HIGH,
                payload={"portfolio": portfolio_response.payload},
                metadata={"workflow_step": "risk_assessment"},
            )

            risk_response = await self.send_message(risk_msg)
            result.risk_assessment = risk_response.payload

            # 3. Tactical layer strategy generation
            strategy_msg = TradingMessage(
                source_layer=LayerType.COORDINATION,
                source_agent="system",
                target_layer=LayerType.TACTICAL,
                target_agent="strategy_research",
                message_type=MessageType.QUERY,
                priority=Priority.MEDIUM,
                payload={
                    "market_data": market_data,
                    "risk_limits": risk_response.payload.get("risk_metrics", {}),
                },
                metadata={"workflow_step": "strategy_generation"},
            )

            strategy_response = await self.send_message(strategy_msg)
            result.strategy_recommendation = strategy_response.payload

            # 4. Execution layer order processing
            signals = strategy_response.payload.get("signals", {})
            if isinstance(signals, dict) and signals.get("signal") == "BUY":
                execution_msg = TradingMessage(
                    source_layer=LayerType.COORDINATION,
                    source_agent="system",
                    target_layer=LayerType.EXECUTION,
                    target_agent="order_execution",
                    message_type=MessageType.COMMAND,
                    priority=Priority.MEDIUM,
                    payload={
                        "order": {
                            "symbol": "AAPL",
                            "side": "BUY",
                            "quantity": 100,
                            "price": signals.get("entry_price", 100.0),
                        }
                    },
                    metadata={"workflow_step": "order_execution"},
                )

                execution_response = await self.send_message(execution_msg)
                result.execution_plan = execution_response.payload

            # 5. Real-time risk monitoring
            risk_monitor_msg = TradingMessage(
                source_layer=LayerType.COORDINATION,
                source_agent="system",
                target_layer=LayerType.MONITORING,
                target_agent="realtime_risk",
                message_type=MessageType.QUERY,
                priority=Priority.MEDIUM,
                payload={"portfolio": portfolio_response.payload},
                metadata={"workflow_step": "risk_monitoring"},
            )

            risk_monitor_response = await self.send_message(risk_monitor_msg)
            result.risk_monitoring = risk_monitor_response.payload

        except Exception as e:
            result.success = False
            result.errors.append(str(e))
            logging.error(f"Trading workflow execution failed: {e}")

        return result

    def get_system_status(self) -> dict[str, Any]:
        """Get comprehensive system status"""
        return {
            "system_status": self.system_status,
            "total_agents": len(self.agents),
            "agent_states": {
                agent_id: state.model_dump()
                for agent_id, state in self.agent_registry.items()
            },
            "message_bus_length": len(self.message_bus),
            "uptime": datetime.now().isoformat(),
        }


# Example usage and testing
async def main() -> None:
    """Example usage of the trading multi-agent system"""
    # Initialize system
    config = AgentConfig()  # Use appropriate configuration
    system = TradingMultiAgentSystem(config)

    # Sample market data
    market_data = {
        "sp500": {"price": 4500, "change": 0.02},
        "bond_yield": {"ten_year": 0.045, "change": -0.001},
        "volatility": {"vix": 18.5},
        "sector_performance": {
            "tech": 0.03,
            "finance": 0.01,
            "energy": -0.02,
        },
    }

    # Execute complete workflow
    result = await system.execute_trading_workflow(market_data)

    print("Trading Workflow Result:")
    print(json.dumps(result.model_dump(), indent=2, default=str))


if __name__ == "__main__":
    asyncio.run(main())
