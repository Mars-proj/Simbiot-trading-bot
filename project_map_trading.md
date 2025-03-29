# Project Map: Trading Logic

## Overview
This file serves as the central hub for the trading bot project, providing a comprehensive overview of the system, its modules, their dependencies, and the roadmap for development, maintenance, and optimization. The goal is to create a self-learning, self-evolving market X-ray system capable of scaling to 1000+ users, opening real trades, and processing signals from all strategies (MovingAverageStrategy, RSIDivergenceStrategy, BollingerBandsBreakoutStrategy, MACDTrendFollowingStrategy, and ML signals from retraining_manager). The system must have maximally flexible and dynamic thresholds, autonomously perform all operations, and continuously learn and improve its performance.

**Main Goal**: Create a self-learning, self-evolving market X-ray system capable of scaling to 1000+ users, opening real trades, and processing signals from all strategies. The system must see the full deposit of the user, including all tokens on the account, and update the deposit after each operation (buy/sell). If there are no trading signals, the system should not make requests to update the deposit.

**Development Approach**: We develop a fully functional system from the start, without using temporary fixes, stubs, or test checks. All code is production-ready and designed to meet the main goal.

**Note**: This project map is automatically updated every second system restart to reflect the latest changes, modules, and roadmap. Additionally, it is manually updated every 3 major system updates to ensure accuracy.

**Development Rule**: Before modifying any existing module, always request its current contents and analyze the dependency chain using the graphical map (`trading_bot_graph.dot`). If necessary, request the contents of all dependent modules in the chain to ensure consistency and avoid introducing new errors.

**Optimization Rule**: During analysis of modules, identify opportunities for optimization (e.g., reducing redundant operations, improving performance, or simplifying logic). Propose and implement optimizations while ensuring consistency across the entire dependency chain by reviewing and updating all affected modules.

## System Configuration and Resources
- **CPUs**: 2x Intel Xeon E5-2697A v4 (32 cores, 64 threads)
  - Used for parallel processing in `symbol_filter.py` and `bot_trading.py` with `ThreadPoolExecutor`.
- **RAM**: 384 GB DDR4
  - Allocated 300 GB for Redis caching (`maxmemory 300gb` in Redis config).
- **Storage**:
  - 2x 480 GB SSD: Used for OS and logs.
  - 1x 4 TB NVMe: Used for historical data storage.
- **Network**: 10 Gbit/s
  - Optimized `EXCHANGE_CONNECTION_SETTINGS.rateLimit` to 500 ms.
- **GPU**: NVIDIA Tesla T4 (16 GB GDDR6, 2560 CUDA cores, 8.1 TFLOPS FP32)
  - Used in `signal_generator_indicators.py` with `cupy` for indicator calculations.
  - Now fully utilized with CUDA 12.1, cuDNN 8.9.7, and PyTorch 2.5.1+cu121 for deep learning tasks in `local_model_api.py` and `retraining_manager.py`.
- **IP and Location**: 45.140.147.187 (Netherlands, nl-arenda.10)

## Module Structure Overview
The system consists of 103 modules, divided into three categories. Detailed module descriptions and dependencies are available in the graph file `trading_bot_graph.dot` and separate module maps:
- **Core Trading Logic**: 16 modules critical for trading operations (see `project_map_modules_core.md`).
- **Supporting Modules**: 9 modules providing essential support functions (see `project_map_modules_supporting.md`).
- **Additional Modules**: 78 modules for extended functionality (see `project_map_modules_additional.md`).

## Known Issues
- **Retrain Manager Data Preparation Failure**: `retraining_manager.py` fails with `Failed to prepare data for signal generation` due to insufficient trade data or data formatting issues. Needs to ensure at least 10 trades are available and properly formatted for ML signal generation.
- **Trade Execution Error**: `bot_trading.py` fails with `'NoneType' object is not subscriptable` due to `execute_trade_signal` returning `None` unexpectedly. Needs to investigate why `trade_executor.execute_trade` returns `None`.
- **Insufficient Deposit**: `trade_executor_signals.py` reports `Insufficient deposit for user 8d99788d-f58f-4fb8-9e4d-c05f177f5405: 0.0 USDT, required minimum 10.0 USDT`. Needs to verify API key permissions or switch to backtesting mode if real funds are unavailable.
- **Import Error in Trading System**: `trade_executor_core.py` fails with `ImportError: cannot import name 'logger_main' from 'utils'`. Needs to correct the import to use `logging_setup.py`.

## Updates
- **2025-03-27**: Updated `trade_executor_core.py` and `bot_trading.py` to fix `risk_calculator` reference by using `deposit_calculator` for drawdown checks.
- **2025-03-27**: Updated `deposit_calculator.py` to support `user_id` in `__init__` and fix logging.
- **2025-03-27**: Updated `bot_trading.py` to remove preliminary deposit check, as it is now handled in `trade_executor_signals.py`.
- **2025-03-27**: Updated `trade_executor_signals.py` to add deposit check before trade execution and cache balance in Redis for 5 minutes. Updated on 2025-03-27 to add fallback to `bot_user_data.py` deposit if exchange fetch fails, and added logging for debugging. Updated on 2025-03-27 to fix `redis_client.get_json` calls by importing functions directly from `redis_client.py`.
- **2025-03-27**: Updated `bot_user_data.py` to add logging for `get_user_deposit` and `get_user_assets` to debug deposit issues. Added test users with deposits for testing.
- **2025-03-27**: Updated `start_trading_all.py` to add a periodic check loop (every 5 minutes) for user deposits and to remove `fetch_balance` call. Updated on 2025-03-27 to reduce check interval to 1 minute. Updated on 2025-03-27 to add timeout and logging for `load_markets_for_exchange`. Updated on 2025-03-27 to fix `redis_client.get_json` calls by importing functions directly from `redis_client.py`.
- **2025-03-27**: Updated `symbol_filter.py` to fix `AttributeError: 'list' object has no attribute 'update'` by converting `problematic_tokens` from list to set after loading from Redis. Added logging for debugging symbol filtering. Updated on 2025-03-27 to add caching of unsupported pairs in Redis. Updated on 2025-03-27 to exclude problematic symbols cached in Redis.
- **2025-03-27**: Updated `strategies.py` to add dynamic parameter calculation based on volatility using `numpy`.
- **2025-03-27**: Updated `trade_pool_core.py` to fix `object NoneType can't be used in 'await' expression` error by removing unnecessary `await` in `add_trade`.
- **2025-03-27**: Updated `redis_initializer.py` to add `get_json` and `set_json` methods for easier JSON handling. Updated on 2025-03-27 to fix circular import with `redis_client.py`. Updated on 2025-03-27 to remove `get_json` and `set_json` methods as they were moved to `redis_client.py`.
- **2025-03-27**: Updated `deposit_calculator.py` to add support for `max_drawdown` parameter in `__init__` to fix `DepositCalculator.__init__() got an unexpected keyword argument 'max_drawdown'` error. Updated on 2025-03-27 to add detailed logging for debugging. Updated on 2025-03-27 to fix `redis_client.get_json` calls by importing functions directly from `redis_client.py` and added price caching in `fetch_price`. Updated on 2025-03-27 to add time synchronization with MEXC server. Updated on 2025-03-27 to disable time sync for MEXC to bypass `InvalidNonce` error.
- **2025-03-27**: Updated `trade_executor_core.py` to initialize `DepositCalculator` with `user_id` in `initialize_deposit`, fixing `Total deposit is 0 for user None` error.
- **2025-03-27**: Updated `bot_user_data.py` to include real user `8d99788d-f58f-4fb8-9e4d-c05f177f5405` for backtesting.
- **2025-03-27**: Updated `config_keys.py` to include real API keys for user `8d99788d-f58f-4fb8-9e4d-c05f177f5405` and made system ready to accept new users at any time.
- **2025-03-27**: Updated `bot_trading.py` to fix `object bool can't be used in 'await' expression` by checking `execute_trade_signal` result before `await`. Updated again on 2025-03-27 to add logging for debugging. Updated on 2025-03-27 to fix `check_drawdown` call by removing `await`. Updated on 2025-03-27 to handle `None` from `execute_trade_signal` and cache problematic symbols in Redis. Updated on 2025-03-27 to fix `redis_client.get_json` calls by importing functions directly from `redis_client.py`.
- **2025-03-27**: Updated `deposit_calculator.py` to calculate deposit including all tokens using intermediate pairs (BTC/ETH), added caching in Redis, and added deposit update after each operation.
- **2025-03-27**: Updated `trade_executor_signals.py` to add logging for debugging `execute_trade` return value.
- **2025-03-27**: Updated `trading_bot_graph.dot` to add dependency `bot_trading -> backtest_cycle`. Updated on 2025-03-27 to add `api_server.py` and its dependency on `logging_setup`. Updated on 2025-03-28 to add dependency `config_keys -> logging_setup`. Updated on 2025-03-28 to remove unused modules: `manual_trade.py`, `async_balance_fetcher.py`, `websocket_manager.py`, `notification_manager.py`, `rate_limiter.py`, `error_handler.py`. Updated on 2025-03-28 to remove unused modules: `performance_metrics.py`, `user_manager.py`. Updated on 2025-03-28 to remove unused modules: `trade_history.py`, `market_data_fetcher.py`. Updated on 2025-03-28 to remove unused module: `exchange_connection_settings.py`. Updated on 2025-03-28 to remove erroneous dependency `json_handler -> logging_setup`.
- **2025-03-27**: Updated `logging_setup.py` to separate logs by level: `INFO` and `WARNING` to `main.log`, `DEBUG` to `debug.log`, `ERROR` to `exceptions.log`. Updated on 2025-03-27 to remove filter for `logger_main` to include `DEBUG` messages in `main.log`.
- **2025-03-27**: Updated `redis_client.py` to add `add_to_problematic_symbols` and `get_problematic_symbols` for caching problematic symbols. Updated on 2025-03-27 to fix circular import with `redis_initializer.py`. Updated on 2025-03-27 to add performance logging for Redis operations. Updated on 2025-03-27 to fix `AttributeError: 'str' object has no attribute 'decode'` in `get_problematic_symbols`.
- **2025-03-27**: Added development rule to always request module contents and analyze dependency chain before modifications.
- **2025-03-27**: Added optimization rule to identify and implement optimizations during module analysis while ensuring consistency across the dependency chain.
- **2025-03-27**: Updated system to utilize GPU (Tesla T4) with CUDA 12.1, cuDNN 8.9.7, and PyTorch 2.5.1+cu121 for deep learning tasks, enabling acceleration in `local_model_api.py` and `retraining_manager.py`.
- **2025-03-27**: Added `api_server.py` to enable direct interaction with the server via FastAPI. Updated on 2025-03-27 to add detailed logging for file operations. Updated on 2025-03-27 to make `write_file` synchronous to avoid async issues. Updated on 2025-03-27 to add token-based authentication.
- **2025-03-27**: Installed `ufw` and opened port 8000 to allow external access to the API server. Successfully tested local API access, but external access still pending due to request formatting issues.
- **2025-03-28**: Confirmed that API server allows reading system files (e.g., `trade_executor_core.py`, `logging_setup.py`), enabling analysis and modification of modules via API.
- **2025-03-28**: Removed unused modules from the system: `manual_trade.py`, `async_balance_fetcher.py`, `websocket_manager.py`, `notification_manager.py`, `rate_limiter.py`, `error_handler.py`. Updated `trading_bot_graph.dot` to remove these modules and their dependencies.
- **2025-03-28**: Removed unused modules from the system: `performance_metrics.py`, `user_manager.py`. Updated `trading_bot_graph.dot` to remove these modules and their dependencies.
- **2025-03-28**: Removed unused modules from the system: `trade_history.py`, `market_data_fetcher.py`. Updated `trading_bot_graph.dot` to remove these modules and their dependencies.
- **2025-03-28**: Replaced Pastebin links with GitHub links in the `Useful Links` section.
- **2025-03-28**: Removed unused module from the system: `exchange_connection_settings.py`. Updated `trading_bot_graph.dot` to remove this module and its dependency.
- **2025-03-28**: Moved audit results to a separate file `project_map_audit_results.md` to reduce the size of `project_map_trading.md`.

## Direct Server Interaction Setup
This section describes the setup for enabling direct interaction with the server, allowing for faster execution of commands, testing, and code updates without manual intervention.

- **Objective**: Enable direct interaction with the server to execute commands, write files, and read files via an API, reducing manual intervention and speeding up development.
- **Implementation**:
  - **Module**: `api_server.py` (added on 2025-03-27)
  - **Dependencies**: Uses `fastapi`, `pydantic`, `subprocess`, `os`, and `logging` for handling API requests, executing commands, and logging.
  - **Endpoints**:
    - `/execute`: Executes a shell command on the server and returns the output.
    - `/write_file`: Writes content to a specified file on the server.
    - `/read_file`: Reads content from a specified file on the server.
  - **Status**: API server is fully functional and accessible locally. Port 8000 opened via `ufw` for external access. Local testing successful, but external file creation still pending due to network access issues.
- **Security Considerations**:
  - **Authentication**: Added token-based authentication with a bearer token (`grok_access_token_2025`).
  - **Access Control**: Port 8000 opened via `ufw`. Plan to restrict API access to specific IP addresses (e.g., using `ufw`).
  - **Command Restrictions**: Plan to limit the types of commands that can be executed to prevent unauthorized actions.
- **Next Steps**:
  - Resolve external access issue by working with support to ensure requests from external IPs reach the server.
  - Add IP-based access restrictions to `ufw` for enhanced security.
  - Test command execution and file reading/writing via external requests.

## Roadmap Parts Overview
The roadmap is divided into several parts, each stored in a separate file:
- **project_map_modules_core.md**: Contains Core Trading Logic modules.
  - **Update**: When core trading modules are modified or new issues arise.
- **project_map_modules_supporting.md**: Contains Supporting Modules.
  - **Update**: When supporting modules are modified or new support features are added.
- **project_map_modules_additional.md**: Contains Additional Modules.
  - **Update**: When additional modules are modified or new features are added.
- **project_map_roadmap_medium_long.md**: Contains Medium-Term and Long-Term roadmap goals.
  - **Update**: When medium-term or long-term goals are updated or completed.
- **trading_bot_graph.dot**: Contains the dependency graph of all modules.
  - **Update**: Every 3 major system updates to ensure accuracy.
- **project_map_audit_results.md**: Contains audit results of all modules.
  - **Update**: When new audit results are added after analyzing modules.

## Roadmap

### Short-Term Goals (1-2 Weeks)
- [x] Fix market loading to occur once per exchange (`start_trading_all.py`).
- [x] Move deposit check to trade execution stage (`trade_executor_signals.py`).
- [x] Fix zero deposit issue in `bot_trading.py`.
- [x] Add logging to `bot_user_data.py` for deposit debugging.
- [x] Fix `symbol_filter.py` error with `problematic_tokens`.
- [x] Fix `DepositCalculator` error with `max_drawdown` in `trade_executor_core.py`.
- [x] Fix `Total deposit is 0 for user None` error by initializing `DepositCalculator` with `user_id`.
- [x] Fix `object bool can't be used in 'await' expression` error in `bot_trading.py` (initial fix for `execute_trade_signal`).
- [x] Fix deposit calculation to include all tokens and update after each operation (`deposit_calculator.py`).
- [x] Integrate `backtest_cycle.py` into `bot_trading.py` for real backtesting.
- [x] Reduce trading cycle interval to 1 minute in `start_trading_all.py`.
- [x] Separate logs by level in `logging_setup.py` for better debugging.
- [x] Fix `object bool can't be used in 'await' expression` error in `bot_trading.py` due to `check_drawdown` (removed `await`).
- [x] Add caching of problematic symbols in `redis_client.py` and `symbol_filter.py`.
- [x] Fix circular import between `redis_client.py` and `redis_initializer.py`.
- [x] Fix market loading issue in `start_trading_all.py` (hangs on `load_markets_for_exchange`).
- [x] Fix `'Redis' object has no attribute 'get_json'` error in `start_trading_all.py`, `bot_trading.py`, `trade_executor_signals.py`, and `deposit_calculator.py` by importing functions directly from `redis_client.py`.
- [x] Enable GPU support for deep learning tasks by upgrading to CUDA 12.1, cuDNN 8.9.7, and PyTorch 2.5.1+cu121.
- [x] Complete setup of `api_server.py` to enable direct server interaction. API server is now functional with local access; external access pending successful resolution of network issues.
- [ ] Fix `'NoneType' object is not subscriptable` error in `bot_trading.py` due to `execute_trade_signal` returning `None`.
- [ ] Fix `retraining_manager.py` warning (`Failed to prepare data for signal generation`).
- [ ] Fix insufficient deposit issue for user `8d99788d-f58f-4fb8-9e4d-c05f177f5405` by verifying API key permissions or switching to backtesting mode.
- [ ] Fix `ImportError: cannot import name 'logger_main' from 'utils'` in `trade_executor_core.py`.
- [ ] Add API rate limit monitoring for MEXC and request pausing when nearing limits.
- [ ] Conduct load testing with 100 users to verify scalability.
- [ ] Implement signal caching in Redis to avoid recalculating signals for unchanged market conditions.
- [ ] Add real-time deposit monitoring and logging for users.
- [ ] Conduct audit of the system to remove unused modules and optimize remaining ones.

## Useful Links
- **project_map_trading.md**: `https://github.com/Mars-proj/project_map_trading.md/blob/main/project_map_trading.md`
- **trading_bot_graph.dot**: `https://github.com/Mars-proj/project_map_trading.md/blob/main/trading_bot_graph.dot`
- **project_map_audit_results.md**: `https://github.com/Mars-proj/project_map_trading.md/blob/main/project_map_audit_results.md`
