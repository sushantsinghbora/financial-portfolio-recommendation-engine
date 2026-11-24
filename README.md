# Financial Portfolio Recommendation Engine

A Data Science-based financial portfolio analytics and recommendation system that helps investors analyze stock portfolios, evaluate investment risks, and optimize asset allocation using historical market data.

## Project Overview

The Financial Portfolio Recommendation Engine is a web-based application developed using Python, FastAPI, and Streamlit.

It analyzes stock market data and provides portfolio insights using statistical analysis, financial metrics, and mathematical optimization.

The system allows users to manage their portfolios, evaluate risk and returns, compare investment strategies, and explore optimized portfolio allocations based on different risk profiles.

## Key Features

- **User Authentication:** Secure registration and login using JWT authentication.
- **Portfolio Management:** Create portfolios and manage stock holdings.
- **Portfolio Analytics:** Calculate portfolio value, annualized return, volatility, and Sharpe ratio.
- **Risk Analysis:** Evaluate investment risk using statistical measures.
- **Correlation Analysis:** Analyze relationships between different stocks using correlation matrices and heatmaps.
- **Portfolio Optimization:** Generate optimized asset allocations based on conservative, moderate, and aggressive risk profiles.
- **Backtesting:** Evaluate investment strategies using historical stock market data.
- **Strategy Comparison:** Compare portfolio strategies based on return, volatility, Sharpe ratio, and maximum drawdown.
- **Efficient Frontier:** Visualize risk-return combinations using portfolio simulations.

## Technology Stack

| Category | Technologies |
|---|---|
| Programming Language | Python |
| Backend | FastAPI |
| Dashboard | Streamlit |
| Data Processing | Pandas, NumPy |
| Optimization | SciPy |
| Data Visualization | Matplotlib |
| Market Data | yfinance |
| Database | SQLite |
| ORM | SQLAlchemy |
| Authentication | JWT |

## System Architecture

1. The user interacts with the Streamlit dashboard.
2. Streamlit communicates with the FastAPI backend through REST APIs.
3. FastAPI handles authentication and portfolio-related requests.
4. Portfolio holdings are retrieved from the SQLite database.
5. Historical stock market data is fetched using yfinance.
6. Pandas and NumPy process financial datasets.
7. SciPy performs portfolio optimization.
8. The backend returns analytical results to Streamlit.
9. Streamlit displays portfolio metrics, recommendations, and visualizations.

## Portfolio Risk Profiles

The application supports three risk profiles:

| Risk Profile | Maximum Allocation per Stock | Risk Aversion |
|---|---:|---:|
| Conservative | 25% | 2.0 |
| Moderate | 40% | 1.0 |
| Aggressive | 60% | 0.25 |

These parameters represent the application's configured optimization preferences.

## Financial Metrics

The application evaluates portfolios using:

- Portfolio Return
- Portfolio Volatility
- Sharpe Ratio
- Correlation
- Maximum Drawdown
- Expected Portfolio Return
- Expected Portfolio Risk

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/sushantsinghbora/financial-portfolio-recommendation-engine.git
```

### 2. Navigate to the project directory

```bash
cd financial-portfolio-recommendation-engine
```

### 3. Create a virtual environment

```bash
python -m venv venv
```

### 4. Activate the virtual environment

Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

### 6. Configure environment variables

Create the required `.env` file using the configuration expected by the backend.

Never upload actual passwords, secret keys, or API credentials to GitHub.

### 7. Run the FastAPI backend

From the project root, use the backend's actual application entry point. For example, if the FastAPI instance is in `backend/app/main.py`:

```bash
uvicorn app.main:app --reload --app-dir backend
```

### 8. Run the Streamlit dashboard

Open another terminal from the project root:

```bash
streamlit run dashboard/app.py
```

## Project Limitations

- Recommendations depend on historical market data and mathematical assumptions.
- Historical performance does not guarantee future returns.
- Market conditions can change unexpectedly.
- The application is intended for educational and analytical purposes, not guaranteed investment advice.

## Future Improvements

- Deploy the application to a cloud platform.
- Add additional financial assets and market data sources.
- Improve portfolio optimization techniques.
- Integrate more advanced predictive analytics.
- Enhance dashboard design and reporting.

## Author

**Sushant Bora**

- GitHub: https://github.com/sushantsinghbora

## Disclaimer

This project is developed for educational and analytical purposes. It does not provide guaranteed financial returns or professional investment advice. 

