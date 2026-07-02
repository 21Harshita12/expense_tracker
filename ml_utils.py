import pandas as pd
import numpy as np
class LinearRegression:
    """
    A lightweight, pure-numpy drop-in replacement for scikit-learn's LinearRegression
    to bypass DLL load blocks on systems with strict application control policies.
    """
    def __init__(self):
        self.coef_ = None
        self.intercept_ = None

    def fit(self, X, y):
        X_flat = X.flatten()
        n = len(X_flat)
        if n == 0:
            self.coef_ = np.array([0.0])
            self.intercept_ = 0.0
            return self
            
        x_mean = np.mean(X_flat)
        y_mean = np.mean(y)
        
        numerator = np.sum((X_flat - x_mean) * (y - y_mean))
        denominator = np.sum((X_flat - x_mean) ** 2)
        
        if denominator == 0:
            slope = 0.0
        else:
            slope = numerator / denominator
            
        self.coef_ = np.array([slope])
        self.intercept_ = y_mean - slope * x_mean
        return self

    def predict(self, X):
        X_flat = X.flatten()
        return self.coef_[0] * X_flat + self.intercept_

    def score(self, X, y):
        y_pred = self.predict(X)
        y_mean = np.mean(y)
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - y_mean) ** 2)
        if ss_tot == 0:
            return 1.0
        return 1.0 - (ss_res / ss_tot)

from datetime import datetime, timedelta

def forecast_expenses(df_expenses: pd.DataFrame, months_to_predict: int = 3):
    """
    Predicts total monthly expenses for future months using scikit-learn Linear Regression.
    
    Parameters:
    - df_expenses: Pandas DataFrame containing historical expenses with columns ['amount', 'date']
    - months_to_predict: Number of months to forecast in the future
    
    Returns:
    - Dict with forecasting status, historical series, predictions series, and metrics.
    """
    if df_expenses.empty:
        return {
            "status": "no_data",
            "message": "No expense records found. Please add some expenses or generate mock data to use the forecasting model."
        }
    
    # 1. Prepare data
    df = df_expenses.copy()
    df['date'] = pd.to_datetime(df['date'])
    
    # Group by year-month and sum the expenses
    monthly_data = df.groupby(df['date'].dt.to_period('M'))['amount'].sum().reset_index()
    monthly_data = monthly_data.sort_values('date').reset_index(drop=True)
    
    # Check if there's enough data for time series forecasting
    n_months = len(monthly_data)
    if n_months < 3:
        return {
            "status": "insufficient_data",
            "message": f"Historical data only covers {n_months} month(s). The machine learning model requires at least 3 months of history to forecast trends.",
            "data_count": n_months
        }
    
    # 2. Build feature matrix and target vector
    # Feature X is the sequential month index (0, 1, 2...)
    X = np.arange(n_months).reshape(-1, 1)
    y = monthly_data['amount'].values
    
    # 3. Fit Linear Regression
    model = LinearRegression()
    model.fit(X, y)
    
    # Make historical predictions to calculate errors / standard deviation
    y_pred_hist = model.predict(X)
    residuals = y - y_pred_hist
    std_err = np.std(residuals) if len(residuals) > 1 else 0.0
    
    # Calculate R-squared for model evaluation
    r_squared = model.score(X, y)
    
    # 4. Predict future months
    future_indices = np.arange(n_months, n_months + months_to_predict).reshape(-1, 1)
    predictions = model.predict(future_indices)
    
    # Create future date periods
    last_period = monthly_data['date'].iloc[-1]
    future_periods = []
    for i in range(1, months_to_predict + 1):
        # Adding months to period
        future_period = last_period + i
        future_periods.append(future_period)
        
    # Build prediction DataFrame
    pred_records = []
    for idx, (period, val) in enumerate(zip(future_periods, predictions)):
        # Calculate bound limits for visual intervals
        lower_bound = max(0.0, val - 1.96 * std_err)  # 95% approximate interval
        upper_bound = val + 1.96 * std_err
        
        pred_records.append({
            "Month": str(period),
            "Predicted Expense": round(val, 2),
            "Lower Bound": round(lower_bound, 2),
            "Upper Bound": round(upper_bound, 2)
        })
        
    df_pred = pd.DataFrame(pred_records)
    
    # Convert historical to strings for charts matching
    historical_records = []
    for idx, row in monthly_data.iterrows():
        historical_records.append({
            "Month": str(row['date']),
            "Actual Expense": round(row['amount'], 2)
        })
    df_hist = pd.DataFrame(historical_records)
    
    # Calculate average historical expense & trend indicator
    avg_expense = round(np.mean(y), 2)
    slope = model.coef_[0]
    trend = "increasing" if slope > 5.0 else ("decreasing" if slope < -5.0 else "stable")
    
    return {
        "status": "success",
        "historical": df_hist,
        "predictions": df_pred,
        "metrics": {
            "r_squared": round(r_squared, 4),
            "std_error": round(std_err, 2),
            "slope": round(slope, 2),
            "average_expense": avg_expense,
            "trend": trend
        }
    }

def load_env_key():
    import os
    # 1. Try OS environment (Streamlit Cloud maps secrets here automatically)
    key = os.getenv("GEMINI_API_KEY")
    if key:
        return key
        
    # 2. Try Streamlit Secrets framework fallback
    try:
        import streamlit as st
        if "GEMINI_API_KEY" in st.secrets:
            return st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass
        
    # 3. Try reading local .env file in workspace
    try:
        env_path = os.path.join(os.path.dirname(__file__), ".env")
        if os.path.exists(env_path):
            with open(env_path, "r") as f:
                for line in f:
                    if line.startswith("GEMINI_API_KEY="):
                        return line.split("=", 1)[1].strip()
    except Exception:
        pass
    return None

def call_gemini_api(url, payload, headers, max_retries=3, backoff_factor=1.5):
    import urllib.request
    import urllib.error
    import json
    import time
    
    last_err = None
    for attempt in range(max_retries):
        req = urllib.request.Request(
            url, 
            data=json.dumps(payload).encode("utf-8"), 
            headers=headers,
            method="POST"
        )
        try:
            with urllib.request.urlopen(req) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            last_err = e
            if e.code in [429, 500, 502, 503, 504]:
                time.sleep(backoff_factor ** attempt)
                continue
            else:
                raise e
        except Exception as e:
            last_err = e
            time.sleep(backoff_factor ** attempt)
            continue
            
    if last_err:
        raise last_err

def generate_gemini_financial_advice(financial_data: dict) -> str:
    """
    Calls the Gemini API to get personalized AI financial advice.
    """
    import urllib.request
    import urllib.error
    import json
    
    api_key = load_env_key()
    if not api_key:
        return "⚠️ **AI Coaching API Key Missing**: Please configure `GEMINI_API_KEY` in your `.env` file to enable AI features."
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    
    # Structure the prompt
    prompt = f"""
You are WealthFlow's AI Financial Coach. Analyze the following personal financial summary for the user and provide actionable, encouraging, and highly specific financial coaching:

Financial Metrics:
- Average Monthly Income: {financial_data.get('avg_income', 0.0)}
- Average Monthly Expenses: {financial_data.get('avg_expenses', 0.0)}
- Net Monthly Savings: {financial_data.get('net_savings', 0.0)}
- Savings Rate: {financial_data.get('savings_rate', 0.0):.1f}%
- Linear Spending Trend (Slope): {financial_data.get('slope', 0.0):+,.2f} per month (from Linear Regression forecast)
- Future Expense Forecast for Next Month: {financial_data.get('forecast_next_month', 0.0)}

Category Spending Details:
{financial_data.get('category_summary_text', 'No category budgets set.')}

Overspent Categories this Month:
{financial_data.get('overspent_summary_text', 'No categories overspent. Excellent job!')}

Provide a structured, premium, and professional coaching report in markdown format. Use icons, headings, bullet points, and bold text. Keep it concise (2-3 paragraphs max) and highly actionable. Include:
1. A brief overall financial health evaluation.
2. Direct advice regarding their overspent categories or low savings rate.
3. Analysis of their ML spending trend and how to mitigate future spending risk.
"""
    
    payload = {
        "contents": [{
            "parts": [{
                "text": prompt
            }]
        }]
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        res_data = call_gemini_api(url, payload, headers)
        return res_data["candidates"][0]["content"]["parts"][0]["text"]
    except urllib.error.HTTPError as e:
        try:
            err_body = e.read().decode("utf-8")
            err_json = json.loads(err_body)
            error_msg = err_json.get("error", {}).get("message", "Unknown HTTP error")
        except Exception:
            error_msg = f"HTTP error {e.code}"
        return f"⚠️ **AI Coaching Temporarily Unavailable**: {error_msg}"
    except Exception as e:
        return f"⚠️ **AI Coaching Temporarily Unavailable**: {str(e)}"

def parse_receipt_image(image_bytes, mime_type, api_key=None) -> dict:
    """
    Sends receipt image bytes to Gemini API and gets parsed expense details.
    """
    import urllib.request
    import urllib.error
    import json
    import base64
    from datetime import date
    
    if not api_key:
        api_key = load_env_key()
    if not api_key:
        return {"status": "error", "message": "Gemini API Key is missing. Please configure GEMINI_API_KEY in your .env file."}
        
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    
    try:
        encoded_image = base64.b64encode(image_bytes).decode('utf-8')
    except Exception as e:
        return {"status": "error", "message": f"Failed to encode image: {str(e)}"}
    
    prompt = f"""
    Analyze this receipt or invoice image. Extract:
    1. The total amount spent (as a number/float, without currency symbols).
    2. The category of spending. Choose ONLY from: Food, Entertainment, Education, Shopping, Bills & Utilities, Other. Use 'Other' if it doesn't fit any of the first five.
    3. A brief description (merchant name/vendor and major item purchased, e.g. "Starbucks - Coffee").
    4. The transaction date in 'YYYY-MM-DD' format. If no date is found on the receipt, use today's date: {date.today().strftime('%Y-%m-%d')}.
    
    Return a JSON object matching this schema:
    {{
        "amount": float,
        "category": string,
        "description": string,
        "date": string
    }}
    """
    
    payload = {
        "contents": [{
            "parts": [
                {"text": prompt},
                {
                    "inlineData": {
                        "mimeType": mime_type,
                        "data": encoded_image
                    }
                }
            ]
        }],
        "generationConfig": {
            "responseMimeType": "application/json"
        }
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        res_data = call_gemini_api(url, payload, headers)
        text_response = res_data["candidates"][0]["content"]["parts"][0]["text"]
        return {
            "status": "success",
            "data": json.loads(text_response)
        }
    except urllib.error.HTTPError as e:
        try:
            err_body = e.read().decode("utf-8")
            err_json = json.loads(err_body)
            error_msg = err_json.get("error", {}).get("message", "Unknown HTTP error")
        except Exception:
            error_msg = f"HTTP error {e.code}"
        return {"status": "error", "message": error_msg}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def get_historical_financial_summary(df_expenses: pd.DataFrame, df_income: pd.DataFrame, budgets: dict) -> dict:
    """
    Summarizes multi-month historical transaction records for Gemini analysis.
    """
    if df_expenses.empty and df_income.empty:
        return {"status": "no_data"}
        
    # Copy dataframes and convert dates
    df_exp = df_expenses.copy()
    df_inc = df_income.copy()
    
    if not df_exp.empty:
        df_exp['date'] = pd.to_datetime(df_exp['date'])
        df_exp['Month'] = df_exp['date'].dt.to_period('M').astype(str)
    else:
        df_exp['Month'] = pd.Series(dtype=str)
        
    if not df_inc.empty:
        df_inc['date'] = pd.to_datetime(df_inc['date'])
        df_inc['Month'] = df_inc['date'].dt.to_period('M').astype(str)
    else:
        df_inc['Month'] = pd.Series(dtype=str)
        
    # Get sorted list of all months present
    all_months = sorted(list(set(df_exp['Month'].unique()) | set(df_inc['Month'].unique())))
    
    months_data = []
    category_totals = {}
    
    for month in all_months:
        # Month totals
        month_inc = df_inc[df_inc['Month'] == month]['amount'].sum() if not df_inc.empty else 0.0
        month_exp = df_exp[df_exp['Month'] == month]['amount'].sum() if not df_exp.empty else 0.0
        net_savings = month_inc - month_exp
        savings_rate = (net_savings / month_inc * 100) if month_inc > 0 else 0.0
        
        # Category breakdown for this month
        month_categories = {}
        if not df_exp.empty:
            m_exp = df_exp[df_exp['Month'] == month]
            cat_grouped = m_exp.groupby('category')['amount'].sum().to_dict()
            for cat, amt in cat_grouped.items():
                month_categories[cat] = round(amt, 2)
                # Add to overall category totals
                category_totals[cat] = category_totals.get(cat, []) + [amt]
                
        months_data.append({
            "month": month,
            "income": round(month_inc, 2),
            "expenses": round(month_exp, 2),
            "net_savings": round(net_savings, 2),
            "savings_rate": round(savings_rate, 1),
            "categories": month_categories
        })
        
    # Compute average category spendings
    category_averages = {}
    for cat, amts in category_totals.items():
        category_averages[cat] = round(sum(amts) / len(amts) if amts else 0.0, 2)
        
    return {
        "status": "success",
        "months_data": months_data,
        "category_averages": category_averages,
        "current_budgets": budgets
    }

def generate_personalized_coaching(summary: dict) -> str:
    """
    Calls the Gemini API to get personalized multi-month coaching and budgeting suggestions.
    """
    import urllib.request
    import urllib.error
    import json
    
    api_key = load_env_key()
    if not api_key:
        return "⚠️ **AI Coaching API Key Missing**: Please configure `GEMINI_API_KEY` in your `.env` file to chat with Gemini."
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    
    # Structure prompt with historical data
    prompt = f"""
You are WealthFlow's Senior AI Financial Advisor and Budgeting Coach.
Analyze the following multi-month personal financial summary for the user and provide a professional, deeply personalized, and highly actionable financial coaching report.

### FINANCIAL HISTORY BY MONTH:
"""
    for m in summary["months_data"]:
        prompt += f"- **Month {m['month']}**:\n"
        prompt += f"  - Total Income: ₹{m['income']:,}\n"
        prompt += f"  - Total Expenses: ₹{m['expenses']:,}\n"
        prompt += f"  - Net Savings: ₹{m['net_savings']:,} (Savings Rate: {m['savings_rate']}%)\n"
        if m["categories"]:
            prompt += f"  - Spending Breakdown: " + ", ".join([f"{cat}: ₹{amt:,}" for cat, amt in m["categories"].items()]) + "\n"
        else:
            prompt += f"  - Spending Breakdown: No category data recorded.\n"
            
    prompt += "\n### HISTORICAL CATEGORY AVERAGES (Per Month):\n"
    for cat, avg in summary["category_averages"].items():
        prompt += f"- {cat}: Average ₹{avg:,} per month\n"
        
    prompt += "\n### CURRENT SET MONTHLY BUDGETS:\n"
    for cat, b_limit in summary["current_budgets"].items():
        prompt += f"- {cat}: Budget limit ₹{b_limit:,}\n"
        
    prompt += """
### COACHING REPORT GUIDELINES:
1. **Overall Health Analysis**: Analyze the trend over all months. Is the savings rate improving, stable, or dropping? Is income growing faster than spending (or vice versa)? Give them an overall grade (e.g. A, B-, C+).
2. **Category Deep Dive & Overspending**: Compare their *Historical Category Averages* to their *Current Set Monthly Budgets*. Pinpoint exactly which category limits are unrealistic (average spending is higher than budget) and where they are consistently overspending.
3. **Specific Budgeting Recommendations**: Suggest *revised budget limits* for each category to match reality while ensuring they meet a target savings rate of at least 20%. Give concrete values like: "Increase Food budget from ₹X to ₹Y, but decrease Shopping limit from ₹A to ₹B."
4. **Action Plan**: Outline 3 actionable milestones for the next 30 days.

Provide a premium, inspiring, and cleanly formatted report in Markdown. Use bullet points, bold highlights, subheadings, and icons to make it highly engaging and professional.
"""

    payload = {
        "contents": [{
            "parts": [{
                "text": prompt
            }]
        }]
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        res_data = call_gemini_api(url, payload, headers)
        return res_data["candidates"][0]["content"]["parts"][0]["text"]
    except urllib.error.HTTPError as e:
        try:
            err_body = e.read().decode("utf-8")
            err_json = json.loads(err_body)
            error_msg = err_json.get("error", {}).get("message", "Unknown HTTP error")
        except Exception:
            error_msg = f"HTTP error {e.code}"
        return f"⚠️ **AI Coaching Temporarily Unavailable**: {error_msg}"
    except Exception as e:
        return f"⚠️ **AI Coaching Temporarily Unavailable**: {str(e)}"


def ask_gemini_custom_question(summary: dict, user_question: str, chat_history: list = None) -> str:
    """
    Calls the Gemini API to answer a user's question, passing prior chat history to preserve conversational memory.
    """
    import urllib.request
    import urllib.error
    import json
    
    api_key = load_env_key()
    if not api_key:
        return "⚠️ **AI Coaching API Key Missing**: Please configure `GEMINI_API_KEY` in your `.env` file to chat with Gemini."
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    
    # Structure historical context
    history_context = ""
    for m in summary.get("months_data", []):
        history_context += f"- **Month {m['month']}**:\n"
        history_context += f"  - Total Income: ₹{m['income']:,}\n"
        history_context += f"  - Total Expenses: ₹{m['expenses']:,}\n"
        history_context += f"  - Net Savings: ₹{m['net_savings']:,} (Savings Rate: {m['savings_rate']}%)\n"
        if m["categories"]:
            history_context += f"  - Spending Breakdown: " + ", ".join([f"{cat}: ₹{amt:,}" for cat, amt in m["categories"].items()]) + "\n"
        else:
            history_context += f"  - Spending Breakdown: No category data recorded.\n"
            
    averages_context = ""
    for cat, avg in summary.get("category_averages", {}).items():
        averages_context += f"- {cat}: Average ₹{avg:,} per month\n"
        
    budgets_context = ""
    for cat, b_limit in summary.get("current_budgets", {}).items():
        budgets_context += f"- {cat}: Budget limit ₹{b_limit:,}\n"
        
    system_prompt = f"""
You are WealthFlow's Senior AI Financial Advisor and Personal Budgeting Coach.
You are having an interactive conversation with the user. Answer their questions with clear, actionable advice using their personal financial history context below.

### USER'S FINANCIAL HISTORY BY MONTH:
{history_context}

### USER'S HISTORICAL CATEGORY AVERAGES (Per Month):
{averages_context}

### USER'S CURRENT MONTHLY BUDGET LIMITS:
{budgets_context}

Please provide a highly professional, encouraging, and clear response in markdown format.
Keep your response concise, specific, and focused on helping the user address their query using their real transaction statistics.
"""

    # Build the contents payload for multi-turn history
    contents_payload = []
    if chat_history:
        for msg in chat_history:
            # Skip welcome / introductory assistant messages to guarantee history starts with a user turn
            if "Welcome to your AI Financial Coach" in msg["content"] or "Meet Your Wealth Advisor" in msg["content"]:
                continue
            role = "model" if msg["role"] == "assistant" else "user"
            contents_payload.append({
                "role": role,
                "parts": [{"text": msg["content"]}]
            })
            
    # Append the new user question
    contents_payload.append({
        "role": "user",
        "parts": [{"text": user_question}]
    })

    payload = {
        "contents": contents_payload,
        "systemInstruction": {
            "parts": [{"text": system_prompt}]
        }
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        res_data = call_gemini_api(url, payload, headers)
        return res_data["candidates"][0]["content"]["parts"][0]["text"]
    except urllib.error.HTTPError as e:
        try:
            err_body = e.read().decode("utf-8")
            err_json = json.loads(err_body)
            error_msg = err_json.get("error", {}).get("message", "Unknown HTTP error")
        except Exception:
            error_msg = f"HTTP error {e.code}"
        return f"⚠️ **AI Coach temporarily unable to answer**: {error_msg}"
    except Exception as e:
        return f"⚠️ **AI Coach temporarily unable to answer**: {str(e)}"


def forecast_expenses_daily(df_expenses: pd.DataFrame, days_to_predict: int = 10):
    """
    Predicts total daily expenses for future days using a Linear Regression model.
    """
    if df_expenses.empty:
        return {
            "status": "no_data",
            "message": "No expense records found. Please add some expenses to use the forecasting model."
        }
    
    # 1. Prepare data
    df = df_expenses.copy()
    df['date'] = pd.to_datetime(df['date'])
    
    # Group by date and sum the expenses
    daily_data = df.groupby('date')['amount'].sum().reset_index()
    daily_data = daily_data.sort_values('date').reset_index(drop=True)
    
    # Reindex to fill date gaps with 0.0
    if not daily_data.empty:
        daily_data = daily_data.set_index('date').asfreq('D', fill_value=0.0).reset_index()
    
    n_days = len(daily_data)
    if n_days < 7:
        return {
            "status": "insufficient_data",
            "message": f"Historical expense dates cover only {n_days} day(s). The model requires at least 7 days of history to forecast daily trends.",
            "data_count": n_days
        }
        
    # 2. Build X & y
    X = np.arange(n_days).reshape(-1, 1)
    y = daily_data['amount'].values
    
    # 3. Fit Linear Regression
    model = LinearRegression()
    model.fit(X, y)
    
    y_pred_hist = model.predict(X)
    residuals = y - y_pred_hist
    std_err = np.std(residuals) if len(residuals) > 1 else 0.0
    r_squared = model.score(X, y)
    
    # 4. Predict future days
    future_indices = np.arange(n_days, n_days + days_to_predict).reshape(-1, 1)
    predictions = model.predict(future_indices)
    
    last_date = daily_data['date'].iloc[-1]
    future_dates = [last_date + timedelta(days=i) for i in range(1, days_to_predict + 1)]
    
    pred_records = []
    for idx, (dt, val) in enumerate(zip(future_dates, predictions)):
        lower_bound = max(0.0, val - 1.96 * std_err)
        upper_bound = val + 1.96 * std_err
        
        pred_records.append({
            "Date": dt.strftime("%Y-%m-%d"),
            "Predicted Expense": round(val, 2),
            "Lower Bound": round(lower_bound, 2),
            "Upper Bound": round(upper_bound, 2)
        })
    df_pred = pd.DataFrame(pred_records)
    
    historical_records = []
    for idx, row in daily_data.iterrows():
        historical_records.append({
            "Date": row['date'].strftime("%Y-%m-%d"),
            "Actual Expense": round(row['amount'], 2)
        })
    df_hist = pd.DataFrame(historical_records)
    
    avg_expense = round(np.mean(y), 2)
    slope = model.coef_[0]
    trend = "increasing" if slope > 0.5 else ("decreasing" if slope < -0.5 else "stable")
    
    return {
        "status": "success",
        "historical": df_hist,
        "predictions": df_pred,
        "metrics": {
            "r_squared": round(r_squared, 4),
            "std_error": round(std_err, 2),
            "slope": round(slope, 2),
            "average_expense": avg_expense,
            "trend": trend
        }
    }




