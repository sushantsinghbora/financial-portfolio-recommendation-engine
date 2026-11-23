
import streamlit as st
import requests
import pandas as pd

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Financial Portfolio Recommendation Engine",
    page_icon="📊",
    layout="wide"
)
# ------------------------------------------
# LIGHT / DARK THEME TOGGLE
# ------------------------------------------

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True

dark_mode = st.sidebar.toggle(
    "🌙 Dark Mode",
    value=st.session_state.dark_mode,
    key="theme_toggle"
)

st.session_state.dark_mode = dark_mode

if dark_mode:
    background = "#0E1117"
    text_color = "#FAFAFA"
    card_background = "#1E293B"
    button_background = "#2563EB"
    button_text = "#FFFFFF"
else:
    background = "#FFFFFF"
    text_color = "#1F2937"
    card_background = "#F1F5F9"
    button_background = "#1D4ED8"
    button_text = "#FFFFFF"

st.markdown(
    f"""
    <style>

    [data-testid="stAppViewContainer"] {{
        background-color: {background};
        color: {text_color};
    }}

    [data-testid="stHeader"] {{
        background-color: {background};
    }}

    [data-testid="stSidebar"] {{
        background-color: {card_background};
    }}

    h1, h2, h3, p, label {{
        color: {text_color};
    }}

    [data-testid="stMetric"] {{
        background-color: {card_background};
        padding: 15px;
        border-radius: 10px;
    }}

    /* BUTTON STYLING */

    [data-testid="stButton"] button {{
        background-color: {button_background} !important;
        color: {button_text} !important;
        border: 1px solid {button_background} !important;
        border-radius: 8px;
        font-weight: 600;
    }}

    [data-testid="stButton"] button p {{
        color: {button_text} !important;
    }}

    [data-testid="stButton"] button:hover {{
        background-color: #1E40AF !important;
        color: #FFFFFF !important;
        border-color: #1E40AF !important;
    }}

    </style>
    """,
    unsafe_allow_html=True
)

API_URL = "http://127.0.0.1:8000"

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "access_token" not in st.session_state:
    st.session_state.access_token = None

if "user_email" not in st.session_state:
    st.session_state.user_email = ""

# --------------------------------------------------
# BACKEND STATUS
# --------------------------------------------------

try:
    health = requests.get(f"{API_URL}/health", timeout=5)

    if health.ok:
        st.success("FastAPI backend connected")
    else:
        st.error(f"Backend returned HTTP {health.status_code}")

except requests.RequestException:
    st.error("Cannot connect to FastAPI. Start Uvicorn first.")
    st.stop()


# --------------------------------------------------
# SEPARATE LOGIN PAGE
# --------------------------------------------------


# --------------------------------------------------
# RESET PASSWORD PAGE
# --------------------------------------------------

reset_token = st.query_params.get("reset_token")

if reset_token:

    st.title("🔐 Reset Your Password")

    st.caption(
        "Create a new password for your account."
    )

    with st.form("reset_password_form"):

        new_password = st.text_input(
            "New Password",
            type="password"
        )

        confirm_password = st.text_input(
            "Confirm New Password",
            type="password"
        )

        reset_clicked = st.form_submit_button(
            "Reset Password",
            use_container_width=True,
            type="primary"
        )

    if reset_clicked:

        if not new_password or not confirm_password:
            st.warning("Please fill in both password fields.")

        elif new_password != confirm_password:
            st.error("Passwords do not match.")

        elif len(new_password) < 8:
            st.error("Password must contain at least 8 characters.")

        else:
            try:
                response = requests.post(
                    f"{API_URL}/auth/reset-password",
                    json={
                        "token": reset_token,
                        "new_password": new_password
                    },
                    timeout=15
                )

                if response.ok:
                    st.query_params.clear()

                    st.success(
                        "Password reset successful! "
                        "You can now log in using your new password."
                    )

                else:
                    try:
                        error_message = response.json().get(
                            "detail",
                            "Password reset failed."
                        )
                    except ValueError:
                        error_message = "Password reset failed."

                    st.error(error_message)

            except requests.RequestException as error:
                st.error(f"Reset request failed: {error}")

    st.stop()

if not st.session_state.access_token:

    st.markdown(
        """
        <style>
        .login-hero {
            padding: 55px 35px;
            min-height: 390px;
            background: linear-gradient(135deg, #172554, #1D4ED8);
            border-radius: 18px;
            color: white;
        }

        .login-hero h1 {
            color: white !important;
            font-size: 34px;
        }

        .login-hero p {
            color: #DBEAFE !important;
            font-size: 16px;
        }

        .login-caption {
            color: #93C5FD !important;
            font-weight: 600;
            letter-spacing: 2px;
        }

        .login-card {
            padding: 25px;
            border: 1px solid #64748B;
            border-radius: 18px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.write("")
    st.write("")

    left_col, right_col = st.columns([1.2, 1], gap="large")

    with left_col:
        st.markdown(
            """
            <div class="login-hero">
                <p class="login-caption">SMART INVESTING PLATFORM</p>
                <h1>Financial Portfolio
                Recommendation Engine</h1>
                <p>
                    Analyze your investments, understand market risks,
                    and make data-driven portfolio decisions.
                </p>
                <br>
                <p>📊 Portfolio Analytics</p>
                <p>📈 Historical Backtesting</p>
                <p>⚖️ Risk Optimization</p>
                <p>🎯 Intelligent Asset Allocation</p>
            </div>
            """,
            unsafe_allow_html=True
        )

 
    with right_col:
        st.write("")
        st.write("")

        page_choice = st.radio(
            "Choose an option",
            ["Login", "Create Account", "Forgot Password"],
            horizontal=True
        )

        # --------------------------------------------------
        # LOGIN
        # --------------------------------------------------

        if page_choice == "Login":

            st.markdown("## Welcome 👋")
            st.caption("Sign in to access your investment dashboard.")

            show_password = st.checkbox(
                "Show Password",
                key="show_login_password"
            )

            with st.form("login_form"):

                email = st.text_input(
                    "Email Address",
                    placeholder="Enter your email",
                    key="login_email"
                )

                password = st.text_input(
                    "Password",
                    type="default" if show_password else "password",
                    placeholder="Enter your password",
                    key="login_password"
                )

                login_clicked = st.form_submit_button(
                    "Sign In",
                    use_container_width=True,
                    type="primary"
                )

            if login_clicked:

                if not email or not password:
                    st.warning("Please enter both email and password.")

                else:
                    try:
                        response = requests.post(
                            f"{API_URL}/auth/login",
                            data={
                                "username": email.strip(),
                                "password": password
                            },
                            timeout=15
                        )

                        if response.ok:
                            login_data = response.json()
                            token = login_data.get("access_token")

                            if token:
                                st.session_state.access_token = token
                                st.session_state.user_email = email.strip()
                                st.rerun()

                            else:
                                st.error("Access token missing.")

                        else:
                            st.error("Login failed. Check your credentials.")
                            st.code(response.text)

                    except requests.RequestException as error:
                        st.error(f"Login request failed: {error}")

        # --------------------------------------------------
        # FORGOT PASSWORD
        # --------------------------------------------------

        elif page_choice == "Forgot Password":

            st.markdown("## Forgot Your Password? 🔑")

            st.caption(
                "Enter your registered email to receive a password reset link."
            )

            with st.form("forgot_password_form"):

                reset_email = st.text_input(
                    "Email Address",
                    placeholder="Enter your registered email"
                )

                forgot_clicked = st.form_submit_button(
                    "Send Reset Link",
                    use_container_width=True,
                    type="primary"
                )

            if forgot_clicked:

                if not reset_email:
                    st.warning("Please enter your email address.")

                else:
                    try:
                        response = requests.post(
                            f"{API_URL}/auth/forgot-password",
                            json={"email": reset_email.strip()},
                            timeout=20
                        )

                        if response.ok:
                            st.success(
                                response.json().get(
                                    "message",
                                    "If this email is registered, a reset link will be sent."
                                )
                            )

                        else:
                            st.error(
                                f"Request failed (HTTP {response.status_code})"
                            )
                            st.code(response.text)

                    except requests.RequestException as error:
                        st.error(f"Request failed: {error}")

        # --------------------------------------------------
        # CREATE ACCOUNT
        # --------------------------------------------------

        else:

            st.markdown("## Create Your Account 🚀")
            st.caption("Join us and start managing your investments.")

            show_password = st.checkbox(
                "Show Password",
                key="show_register_password"
            )

            with st.form("register_form"):

                username = st.text_input(
                    "Username",
                    placeholder="Choose a username"
                )

                email = st.text_input(
                    "Email Address",
                    placeholder="Enter your valid email"
                )

                password = st.text_input(
                    "Password",
                    type="default" if show_password else "password"
                )

                confirm_password = st.text_input(
                    "Confirm Password",
                    type="default" if show_password else "password"
                )

                register_clicked = st.form_submit_button(
                    "Create Account",
                    use_container_width=True,
                    type="primary"
                )

            if register_clicked:

                if not username or not email or not password or not confirm_password:
                    st.warning("Please fill in all fields.")

                elif password != confirm_password:
                    st.error("Passwords do not match.")

                else:
                    try:
                        response = requests.post(
                            f"{API_URL}/auth/register",
                            json={
                                "username": username.strip(),
                                "email": email.strip(),
                                "password": password
                            },
                            timeout=15
                        )

                        if response.ok:

                            st.success(
                                "Account created successfully! "
                                "Please select Login."
                            )

                        else:

                            st.error(
                                f"Registration failed (HTTP {response.status_code})"
                            )

                            st.code(response.text)

                    except requests.RequestException as error:
                        st.error(
                            f"Registration request failed: {error}"
                        )

    st.stop()


else:

    st.sidebar.success(
        f"Logged in: {st.session_state.user_email}"
    )

    if st.sidebar.button("Logout"):
        st.session_state.access_token = None
        st.session_state.user_email = ""
        st.rerun()

    st.title("📊 Financial Portfolio Recommendation Engine")

    st.markdown(
        """
        <p style="color: #9CA3AF; font-size: 16px;">
            Intelligent Investment Analysis |
            Portfolio Optimization | Risk Management
        </p>
        """,
        unsafe_allow_html=True
    )

    st.divider()

# --------------------------------------------------
# PORTFOLIO CONTROLS
# --------------------------------------------------

st.sidebar.divider()
st.sidebar.header("Portfolio Controls")

portfolio_id = st.sidebar.number_input(
    "Portfolio ID",
    min_value=1,
    value=5,
    step=1
)

risk_profile = st.sidebar.selectbox(
    "Risk Profile",
    ["conservative", "moderate", "aggressive"],
    index=1
)

# --------------------------------------------------
# PORTFOLIO ANALYSIS
# --------------------------------------------------

st.header("Portfolio Analysis")

if not st.session_state.access_token:

    st.info(
        "Log in using the sidebar to load your portfolio analytics."
    )

else:

    if st.button("Analyze Portfolio", type="primary"):

        with st.spinner(
            "Fetching portfolio analytics and recommendations..."
        ):

            try:
                response = requests.post(
                    f"{API_URL}/recommendation/portfolio",
                    json={
                        "portfolio_id": int(portfolio_id),
                        "risk_profile": risk_profile
                    },
                    headers={
                        "Authorization": (
                            f"Bearer {st.session_state.access_token}"
                        )
                    },
                    timeout=120
                )

                if response.status_code == 401:
                    st.error(
                        "Session expired or token invalid. "
                        "Please log in again."
                    )
                    st.session_state.access_token = None
                    st.session_state.user_email = ""
                    st.rerun()

                elif response.status_code == 403:
                    st.error("Access forbidden for this account.")

                elif response.status_code == 404:
                    st.error("Portfolio not found for your account.")

                elif response.ok:
                    st.session_state.portfolio_result = response.json()
                    st.success("Portfolio analysis completed!")

                else:
                    st.error(
                        f"API error ({response.status_code})"
                    )
                    st.code(response.text)

            except requests.RequestException as error:
                st.error(f"Could not retrieve portfolio: {error}")

# --------------------------------------------------
# DISPLAY PORTFOLIO RESULTS
# --------------------------------------------------

result = st.session_state.get("portfolio_result")

if result:

    st.subheader(
        result.get("portfolio_name", "Portfolio Results")
    )

    st.caption(
        f"Portfolio ID: {result.get('portfolio_id', 'N/A')}"
    )

    analytics = result.get("portfolio_analytics", {})
    recommendation = result.get("recommendation", {})

    # ----------------------------------------------
    # CURRENT PORTFOLIO METRICS
    # ----------------------------------------------

    if analytics:

        st.header("📈 Portfolio Overview")

        st.caption(
            "Monitor your investment performance and risk indicators."
        )

        st.divider()

        st.subheader("Current Portfolio Metrics")

        metric1, metric2, metric3, metric4 = st.columns(4)

        metric1.metric(
            "Portfolio Value",
            f"{analytics.get('total_portfolio_value', 0):,.2f}"
        )

        metric2.metric(
            "Annual Return",
            f"{analytics.get('annual_return_percentage', 0):.2f}%"
        )

        metric3.metric(
            "Annual Volatility",
            f"{analytics.get('annual_volatility_percentage', 0):.2f}%"
        )

        metric4.metric(
            "Sharpe Ratio",
            f"{analytics.get('sharpe_ratio', 0):.3f}"
        )

        st.divider()

        # ------------------------------------------
        # HOLDINGS ANALYSIS
        # ------------------------------------------

        holdings = analytics.get("holdings", [])

        if holdings:

            st.header("📊 Holdings Analysis")

            st.caption(
                "View your assets and understand their contribution to your portfolio."
            )

            st.divider()

            holdings_df = pd.DataFrame(holdings)

            st.dataframe(
                holdings_df,
                use_container_width=True
            )

            if (
                "symbol" in holdings_df.columns
                and "weight_percentage" in holdings_df.columns
            ):

                chart_df = holdings_df.set_index("symbol")[
                    "weight_percentage"
                ]

                st.bar_chart(
                    chart_df,
                    height=350
                )
        # ------------------------------------------
        # CORRELATION HEATMAP
        # ------------------------------------------

        correlation_matrix = analytics.get(
            "correlation_matrix"
        )

        if (
            isinstance(correlation_matrix, dict)
            and correlation_matrix
        ):

            st.divider()

            st.header("🔗 Risk & Diversification Analysis")

            st.caption(
                "Understand how your selected stocks move in relation to each other."
            )

            st.subheader("📊 Stock Correlation Heatmap")

            correlation_df = pd.DataFrame(correlation_matrix)

            st.caption(
                "Values range from -1 to +1. Positive values indicate "
                "stocks tend to move together; negative values indicate "
                "opposite movements."
            )

            st.dataframe(
                correlation_df.style
                .format("{:.2f}")
                .background_gradient(
                    cmap="RdYlGn",
                    vmin=-1,
                    vmax=1
                ),
                use_container_width=True
            )

        else:
            st.info(
                "Correlation matrix is missing or empty. "
                "Check the complete API response."
            )

    # ----------------------------------------------
    # RECOMMENDED PORTFOLIO ALLOCATION
    # ----------------------------------------------

    if recommendation:

        st.divider()
        st.subheader("Recommended Portfolio Allocation")

        allocation = recommendation.get(
            "recommended_allocation", {}
        )

        if allocation:

            allocation_df = pd.DataFrame(
                list(allocation.items()),
                columns=["Stock", "Allocation (%)"]
            )

            st.dataframe(
                allocation_df,
                use_container_width=True
            )

            st.bar_chart(
                allocation_df.set_index("Stock")
            )

        # ------------------------------------------
        # OPTIMIZATION METRICS
        # ------------------------------------------

        metrics = recommendation.get(
            "optimization_metrics", {}
        )

        if metrics:

            st.subheader("Optimization Metrics")

            c1, c2, c3 = st.columns(3)

            c1.metric(
                "Expected Return",
                f"{metrics.get('expected_return', 0):.2f}%"
            )

            c2.metric(
                "Expected Volatility",
                f"{metrics.get('expected_volatility', 0):.2f}%"
            )

            c3.metric(
                "Expected Sharpe Ratio",
                f"{metrics.get('sharpe_ratio', 0):.3f}"
            )

    with st.expander("View complete API response"):
        st.json(result)


# ==================================================
# BACKTESTING & STRATEGY COMPARISON
# ==================================================
st.divider()

st.header("📈 Historical Performance & Strategy Evaluation")

st.caption(
    "Evaluate investment strategies using historical market data "
    "and compare their risk-adjusted performance."
)

if not st.session_state.access_token:

    st.info(
        "Please log in to use backtesting and strategy comparison."
    )

elif not st.session_state.get("portfolio_result"):

    st.info(
        "Analyze your portfolio first, then run backtesting."
    )

else:

    backtest_col, comparison_col = st.columns(2)

    # ----------------------------------------------
    # RUN BACKTEST
    # ----------------------------------------------

    with backtest_col:

        if st.button("Run Backtest", type="primary"):

            with st.spinner("Running out-of-sample backtest..."):

                try:
                    response = requests.post(
                        f"{API_URL}/recommendation/portfolio/backtest",
                        json={
                            "portfolio_id": int(portfolio_id),
                            "risk_profile": risk_profile
                        },
                        headers={
                            "Authorization": (
                                f"Bearer {st.session_state.access_token}"
                            )
                        },
                        timeout=180
                    )

                    if response.ok:

                        st.session_state.backtest_result = (
                            response.json()
                        )

                        st.success("Backtest completed!")

                    else:

                        st.error(
                            f"Backtest failed: HTTP {response.status_code}"
                        )

                        st.code(response.text)

                except requests.RequestException as error:
                    st.error(f"Backtest request failed: {error}")

    # ----------------------------------------------
    # COMPARE STRATEGIES
    # ----------------------------------------------

    with comparison_col:

        if st.button("Compare Strategies"):

            with st.spinner("Comparing portfolio strategies..."):

                try:
                    response = requests.post(
                        f"{API_URL}/recommendation/portfolio/compare-strategies",
                        json={
                            "portfolio_id": int(portfolio_id),
                            "risk_profile": risk_profile
                        },
                        headers={
                            "Authorization": (
                                f"Bearer {st.session_state.access_token}"
                            )
                        },
                        timeout=240
                    )

                    if response.ok:

                        st.session_state.strategy_comparison_result = (
                            response.json()
                        )

                        st.success(
                            "Strategy comparison completed!"
                        )

                    else:

                        st.error(
                            "Strategy comparison failed: "
                            f"HTTP {response.status_code}"
                        )

                        st.code(response.text)

                except requests.RequestException as error:
                    st.error(f"Comparison request failed: {error}")

    # ----------------------------------------------
    # DISPLAY BACKTEST RESULTS
    # ----------------------------------------------

    backtest_data = st.session_state.get("backtest_result")

    if backtest_data:

        st.header("📉 Out-of-Sample Backtesting Results")

        st.caption(
            "Evaluate how your portfolio strategy performed "
            "on historical data that was not used for training."
        )

        st.divider()

        backtest = backtest_data.get("backtest", {})

        performance = backtest.get(
            "out_of_sample_performance", {}
        )

        if performance:

            c1, c2, c3, c4, c5 = st.columns(5)

            c1.metric(
                "Cumulative Return",
                f"{performance.get('cumulative_return', 0):.2f}%"
            )

            c2.metric(
                "Annualized Return",
                f"{performance.get('annualized_return', 0):.2f}%"
            )

            c3.metric(
                "Annualized Volatility",
                f"{performance.get('annualized_volatility', 0):.2f}%"
            )

            c4.metric(
                "Sharpe Ratio",
                f"{performance.get('sharpe_ratio', 0):.3f}"
            )

            c5.metric(
                "Maximum Drawdown",
                f"{performance.get('maximum_drawdown', 0):.2f}%"
            )

        st.write(
            "**Training period:**",
            backtest.get("training_period")
        )

        st.write(
            "**Testing period:**",
            backtest.get("testing_period")
        )

        st.write("**Recommended allocation:**")

        st.json(
            backtest.get("recommended_allocation", {})
        )

        with st.expander("View complete backtest response"):
            st.json(backtest_data)

        # ------------------------------------------
        # CUMULATIVE PORTFOLIO PERFORMANCE CHART
        # ------------------------------------------

        cumulative_data = performance.get(
            "cumulative_returns", []
        )

        if cumulative_data:

            st.divider()
            st.subheader("📈 Cumulative Portfolio Performance")

            cumulative_df = pd.DataFrame(cumulative_data)

            if (
                "date" in cumulative_df.columns
                and "cumulative_return" in cumulative_df.columns
            ):

                cumulative_df["date"] = pd.to_datetime(
                    cumulative_df["date"],
                    errors="coerce"
                )

                cumulative_df["cumulative_return"] = pd.to_numeric(
                    cumulative_df["cumulative_return"],
                    errors="coerce"
                )

                cumulative_df = (
                    cumulative_df
                    .dropna(subset=["date", "cumulative_return"])
                    .sort_values("date")
                    .set_index("date")
                )

                if not cumulative_df.empty:

                    st.line_chart(
                        cumulative_df["cumulative_return"],
                        y_label="Cumulative Return (%)",
                        x_label="Date"
                    )

                    st.caption(
                        "Historical cumulative returns during the testing "
                        "period. Past performance does not guarantee "
                        "future results."
                    )

                else:
                    st.warning(
                        "The cumulative return data contains no valid "
                        "dates or values."
                    )

            else:
                st.warning(
                    "The API returned cumulative data in an unexpected "
                    "format. Check the complete backtest response."
                )

        else:
            st.info(
                "Cumulative return history is unavailable. "
                "Run the backtest again to refresh the results."
            )

# ==================================================
# DISPLAY STRATEGY COMPARISON RESULTS
# ==================================================

comparison_data = st.session_state.get(
    "strategy_comparison_result"
)

if comparison_data:

    st.divider()
    st.header("⚖️ Investment Strategy Comparison")

    st.caption(
        "Compare conservative, moderate, aggressive, and "
        "equal-weight strategies using risk and return metrics."
    )
    summary = comparison_data.get("summary", [])

    if summary:

        comparison_df = pd.DataFrame(summary)

        st.dataframe(
            comparison_df,
            use_container_width=True,
            hide_index=True
        )

        st.caption(
            "All strategies are evaluated on the same historical test "
            "period. Returns and risk metrics are historical, not "
            "guaranteed future performance."
        )

        # ------------------------------------------
        # ANNUALIZED RETURN
        # ------------------------------------------

        if "annualized_return" in comparison_df.columns:

            st.subheader("Annualized Return Comparison")

            st.bar_chart(
                comparison_df.set_index("strategy")[
                    "annualized_return"
                ]
            )

        # ------------------------------------------
        # ANNUALIZED VOLATILITY
        # ------------------------------------------

        if "annualized_volatility" in comparison_df.columns:

            st.subheader("Annualized Volatility Comparison")

            st.bar_chart(
                comparison_df.set_index("strategy")[
                    "annualized_volatility"
                ]
            )

        # ------------------------------------------
        # SHARPE RATIO
        # ------------------------------------------

        if "sharpe_ratio" in comparison_df.columns:

            st.subheader("Sharpe Ratio Comparison")

            st.bar_chart(
                comparison_df.set_index("strategy")[
                    "sharpe_ratio"
                ]
            )

        # ------------------------------------------
        # MAXIMUM DRAWDOWN
        # ------------------------------------------

        if "maximum_drawdown" in comparison_df.columns:

            st.subheader("Maximum Drawdown Comparison")

            st.bar_chart(
                comparison_df.set_index("strategy")[
                    "maximum_drawdown"
                ]
            )

    st.write(
        "**Training period:**",
        comparison_data.get("training_period")
    )

    st.write(
        "**Testing period:**",
        comparison_data.get("testing_period")
    )

    with st.expander("View complete strategy comparison response"):
        st.json(comparison_data)

    # ----------------------------------------------
    # STRATEGY VS BENCHMARK GROWTH CHART
    # ----------------------------------------------

    comparison_results = comparison_data.get(
        "comparison", {}
    )


    strategies = comparison_results.get(
        "strategies", {}
    )


    if strategies:

        st.divider()
        st.subheader("📈 Strategy vs Benchmark Performance")

        strategy_chart_data = {}

        for strategy_name, strategy_data in strategies.items():

            performance = strategy_data.get(
                "test_performance", {}
            )

            cumulative_data = performance.get(
                "cumulative_returns", []
            )

            if cumulative_data:

                strategy_df = pd.DataFrame(cumulative_data)

                if (
                    "date" in strategy_df.columns
                    and "cumulative_return" in strategy_df.columns
                ):
                    strategy_df["date"] = pd.to_datetime(
                        strategy_df["date"], errors="coerce"
                    )

                    strategy_df["cumulative_return"] = pd.to_numeric(
                        strategy_df["cumulative_return"], errors="coerce"
                    )

                    strategy_df = (
                        strategy_df
                        .dropna(subset=["date", "cumulative_return"])
                        .sort_values("date")
                        .set_index("date")
                    )

                    if not strategy_df.empty:
                        strategy_chart_data[strategy_name] = (
                            strategy_df["cumulative_return"]
                        )

        if strategy_chart_data:

            strategy_chart_df = pd.DataFrame(strategy_chart_data)

            st.line_chart(
                strategy_chart_df,
                y_label="Cumulative Return (%)",
                x_label="Date"
            )

            st.caption(
                "Compares conservative, moderate, aggressive "
                "and equal-weight benchmark performance over "
                "the same historical testing period. "
                "Past performance does not guarantee future results."
            )

        else:
            st.warning(
                "Cumulative performance history is unavailable "
                "for strategy comparison."
            )


# ==================================================
# EFFICIENT FRONTIER VISUALIZATION
# ==================================================

st.header("📊 Efficient Frontier & Portfolio Optimization")

st.caption(
    "Explore the relationship between investment risk and "
    "expected returns to identify an optimal portfolio."
)

st.divider()

if st.button("Generate Efficient Frontier"):

    try:

        response = requests.post(
            f"{API_URL}/recommendation/portfolio/efficient-frontier",
            json={
                "portfolio_id": portfolio_id,
                "risk_profile": risk_profile
            },
            headers={
                "Authorization": f"Bearer {st.session_state.access_token}"
            },
            timeout=180
        )

        if response.status_code == 200:

            efficient_data = response.json()["efficient_frontier"]

            st.session_state["efficient_frontier_result"] = (
                efficient_data
            )

            st.success(
                "Efficient Frontier generated successfully!"
            )

        else:
            st.error(
                f"API Error: {response.status_code} - "
                f"{response.text}"
            )

    except requests.exceptions.RequestException as error:

        st.error(
            f"Unable to generate Efficient Frontier: {error}"
        )


# ==================================================
# DISPLAY EFFICIENT FRONTIER RESULTS
# ==================================================

efficient_data = st.session_state.get(
    "efficient_frontier_result"
)

if efficient_data:

    simulations = pd.DataFrame(
        efficient_data["simulations"]
    )

    optimal = efficient_data["optimal_portfolio"]

    st.subheader("Optimal Portfolio Metrics")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Expected Annual Return",
        f"{optimal['expected_return'] * 100:.2f}%"
    )

    col2.metric(
        "Expected Annual Risk",
        f"{optimal['expected_volatility'] * 100:.2f}%"
    )

    col3.metric(
        "Sharpe Ratio",
        f"{optimal['sharpe_ratio']:.3f}"
    )

    # ------------------------------------------
    # RISK VS RETURN SCATTER PLOT
    # ------------------------------------------

    st.subheader("Risk vs Expected Return")

    st.caption(
        "Each point represents one simulated portfolio. "
        "The highlighted point represents the portfolio "
        "with the highest simulated Sharpe ratio."
    )


    # Prepare simulated portfolio data
    chart_data = simulations[
        ["risk", "return", "sharpe"]
    ].copy()

    chart_data["risk"] *= 100
    chart_data["return"] *= 100

    # Calculate the optimal portfolio coordinates
    optimal_risk = optimal["expected_volatility"] * 100
    optimal_return = optimal["expected_return"] * 100


    # ------------------------------------------
    # SIMULATED PORTFOLIOS + EFFICIENT FRONTIER
    # ------------------------------------------

    st.subheader("Efficient Frontier Curve")

    # Simulated portfolios
    st.scatter_chart(
        chart_data,
        x="risk",
        y="return",
        color="sharpe"
    )

    # Efficient frontier coordinates
    frontier_df = pd.DataFrame(
        efficient_data["efficient_frontier"]
    )

    if not frontier_df.empty:

        frontier_df["risk"] *= 100
        frontier_df["return"] *= 100

        frontier_df = frontier_df.rename(
            columns={
                "risk": "Risk (%)",
                "return": "Expected Return (%)"
            }
        )

        st.line_chart(
            frontier_df.set_index("Risk (%)"),
            y="Expected Return (%)"
        )

    else:
        st.warning(
            "Efficient Frontier curve could not be generated."
        )


    # Highlight the optimal portfolio separately
    optimal_chart_data = pd.DataFrame({
        "Risk": [optimal_risk],
        "Expected Return": [optimal_return]
    })

    st.subheader("Maximum Sharpe Ratio Portfolio")

    st.scatter_chart(
        optimal_chart_data,
        x="Risk",
        y="Expected Return"
    )

    st.metric(
        "Optimal Portfolio Risk",
        f"{optimal_risk:.2f}%"
    )

    st.metric(
        "Optimal Portfolio Expected Return",
        f"{optimal_return:.2f}%"
    )


    # ------------------------------------------
    # OPTIMAL PORTFOLIO ALLOCATION
    # ------------------------------------------

    st.subheader("Optimal Portfolio Allocation")

    allocation_df = pd.DataFrame(
        list(optimal["weights"].items()),
        columns=["Stock", "Weight"]
    )

    allocation_df["Allocation (%)"] = (
        allocation_df["Weight"] * 100
    )

    st.bar_chart(
        allocation_df.set_index("Stock")[
            "Allocation (%)"
        ]
    )

    st.dataframe(
        allocation_df[
            ["Stock", "Allocation (%)"]
        ].round(2),
        use_container_width=True
    )

    st.caption(
        "The optimal portfolio is selected from the "
        "simulated portfolios based on the highest "
        "Sharpe ratio. These are historical estimates, "
        "not guaranteed future returns."
    )


