#!/usr/bin/env python3
"""
Test script for the Pydantic-based trading multi-agent system
Demonstrates the new Python 3.11+ features and Pydantic integration
"""

import asyncio
import json
from datetime import datetime
from uuid import uuid4

from aap.teams.trading_multi_agent_pydantic import (
    TradingMultiAgentSystem,
    TradingMessage,
    MessageType,
    Priority,
    LayerType,
    Allocation,
    RiskMetrics,
    TradingSignal,
    BacktestStats,
    OrderPlan,
    Alert,
    Task,
)
from aworld.config.conf import AgentConfig


async def test_pydantic_models():
    """Test Pydantic model validation and serialization"""
    print("=== Testing Pydantic Models ===")
    
    # Test Allocation model
    allocation = Allocation(
        stocks=0.6,
        bonds=0.3,
        cash=0.1,
        rebalance_trigger=0.05
    )
    print(f"Allocation model: {allocation.model_dump_json(indent=2)}")
    
    # Test RiskMetrics model
    risk_metrics = RiskMetrics(
        portfolio_var=0.02,
        expected_shortfall=0.035,
        max_drawdown=0.15,
        beta=1.1,
        risk_limits={"max_position_size": 0.1, "max_sector_exposure": 0.25}
    )
    print(f"RiskMetrics model: {risk_metrics.model_dump_json(indent=2)}")
    
    # Test TradingSignal model
    signal = TradingSignal(
        signal="BUY",
        confidence=0.75,
        entry_price=100.0,
        stop_loss=95.0,
        take_profit=110.0,
        position_size=0.05
    )
    print(f"TradingSignal model: {signal.model_dump_json(indent=2)}")
    
    # Test BacktestStats model
    backtest = BacktestStats(
        sharpe_ratio=1.2,
        max_drawdown=0.08,
        win_rate=0.65,
        profit_factor=1.5
    )
    print(f"BacktestStats model: {backtest.model_dump_json(indent=2)}")


async def test_message_system():
    """Test the message system with Pydantic models"""
    print("\n=== Testing Message System ===")
    
    # Create a test message
    message = TradingMessage(
        source_layer=LayerType.STRATEGIC,
        source_agent="portfolio_manager",
        target_layer=LayerType.TACTICAL,
        target_agent="strategy_research",
        message_type=MessageType.QUERY,
        priority=Priority.HIGH,
        payload={
            "market_data": {"sp500": 4500, "volatility": 18.5},
            "risk_limits": {"max_var": 0.02, "max_drawdown": 0.15}
        }
    )
    
    print(f"Message created: {message.model_dump_json(indent=2)}")
    
    # Test message serialization/deserialization
    serialized = message.model_dump_json()
    deserialized = TradingMessage.model_validate_json(serialized)
    print(f"Message round-trip successful: {deserialized.message_id == message.message_id}")


async def test_complete_workflow():
    """Test the complete trading workflow"""
    print("\n=== Testing Complete Workflow ===")
    
    # Initialize system
    config = AgentConfig()
    system = TradingMultiAgentSystem(config)
    
    # Sample market data
    market_data = {
        "sp500": {"price": 4500, "change": 0.02, "volume": 1000000},
        "bond_yield": {"ten_year": 0.045, "change": -0.001},
        "volatility": {"vix": 18.5, "change": -2.1},
        "sector_performance": {
            "technology": 0.03,
            "finance": 0.01,
            "energy": -0.02,
            "healthcare": 0.015,
        },
        "macro_indicators": {
            "gdp_growth": 0.025,
            "inflation": 0.032,
            "unemployment": 0.038,
        }
    }
    
    # Execute workflow
    result = await system.execute_trading_workflow(market_data)
    
    print("Workflow Result:")
    print(json.dumps(result.model_dump(), indent=2, default=str))
    
    # Get system status
    status = system.get_system_status()
    print("\nSystem Status:")
    print(json.dumps(status, indent=2, default=str))


async def test_error_handling():
    """Test error handling with Pydantic models"""
    print("\n=== Testing Error Handling ===")
    
    try:
        # Test invalid allocation (should fail validation)
        invalid_allocation = Allocation(
            stocks=0.8,
            bonds=0.3,  # This would make total > 1
            cash=0.1,
            rebalance_trigger=0.05
        )
    except ValueError as e:
        print(f"Expected validation error: {e}")
    
    try:
        # Test invalid trading signal
        invalid_signal = TradingSignal(
            signal="INVALID",  # Not in Literal["BUY", "SELL", "HOLD"]
            confidence=0.75
        )
    except ValueError as e:
        print(f"Expected validation error: {e}")


async def test_async_operations():
    """Test async operations with the new system"""
    print("\n=== Testing Async Operations ===")
    
    config = AgentConfig()
    system = TradingMultiAgentSystem(config)
    
    # Test concurrent message processing
    tasks = []
    for i in range(5):
        message = TradingMessage(
            source_layer=LayerType.COORDINATION,
            source_agent="test_system",
            target_layer=LayerType.MONITORING,
            target_agent="realtime_risk",
            message_type=MessageType.QUERY,
            priority=Priority.MEDIUM,
            payload={"test_id": i, "timestamp": datetime.now().isoformat()}
        )
        tasks.append(system.send_message(message))
    
    # Execute concurrently
    results = await asyncio.gather(*tasks)
    print(f"Processed {len(results)} messages concurrently")


async def main():
    """Main test runner"""
    print("Starting Pydantic-based trading system tests...")
    
    try:
        await test_pydantic_models()
        await test_message_system()
        await test_complete_workflow()
        await test_error_handling()
        await test_async_operations()
        
        print("\n✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())