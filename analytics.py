"""
Analytics and prediction functions
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression

def predict_future_expenses(df, days_ahead=30):
    """Predict future expenses using linear regression"""
    if df.empty or len(df) < 7:
        return None, "Need at least 7 days of data for predictions"
    
    df_sorted = df.sort_values('date')
    df_sorted['days'] = (df_sorted['date'] - df_sorted['date'].min()).dt.days
    
    daily_expenses = df_sorted.groupby('days')['amount'].sum().reset_index()
    
    if len(daily_expenses) < 3:
        return None, "Need more data points for accurate predictions"
    
    X = daily_expenses['days'].values.reshape(-1, 1)
    y = daily_expenses['amount'].values
    
    model = LinearRegression()
    model.fit(X, y)
    
    last_day = daily_expenses['days'].max()
    future_days = np.array(range(last_day + 1, last_day + days_ahead + 1)).reshape(-1, 1)
    predictions = model.predict(future_days)
    
    # Ensure no negative predictions
    predictions = np.maximum(predictions, 0)
    
    future_dates = [df['date'].max() + timedelta(days=i) for i in range(1, days_ahead + 1)]
    prediction_df = pd.DataFrame({
        'date': future_dates,
        'predicted_amount': predictions
    })
    
    total_predicted = predictions.sum()
    avg_daily = predictions.mean()
    
    spoken_text = f"Based on your spending patterns, I predict you'll spend {total_predicted:.2f} dollars over the next {days_ahead} days. That's an average of {avg_daily:.2f} dollars per day."
    
    return prediction_df, spoken_text

def generate_insights(df):
    """Generate text insights from expense data"""
    insights = []
    
    if df.empty:
        return ["No expenses recorded yet. Start tracking to get insights!"]
    
    total = df['amount'].sum()
    insights.append(f"💰 **Total Spending**: ${total:,.2f}")
    
    avg_transaction = df['amount'].mean()
    insights.append(f"📊 **Average Transaction**: ${avg_transaction:.2f}")
    
    # Top category
    category_spending = df.groupby('category')['amount'].sum().sort_values(ascending=False)
    if not category_spending.empty:
        top_category = category_spending.index[0]
        top_amount = category_spending.values[0]
        percentage = (top_amount / total) * 100
        insights.append(f"🏆 **Top Category**: {top_category} (${top_amount:,.2f} - {percentage:.1f}%)")
    
    # Entry method breakdown
    if 'entry_method' in df.columns:
        entry_counts = df['entry_method'].value_counts()
        insights.append(f"📝 **Entry Methods**: Manual: {entry_counts.get('manual', 0)}, Voice: {entry_counts.get('voice', 0)}, OCR: {entry_counts.get('ocr', 0)}")
    
    # Spending trend
    if len(df) >= 14:
        df_sorted = df.sort_values('date')
        first_week = df_sorted.head(7)['amount'].sum()
        last_week = df_sorted.tail(7)['amount'].sum()
        if first_week > 0:
            change = ((last_week - first_week) / first_week) * 100
            trend = "📈 increasing" if change > 0 else "📉 decreasing"
            insights.append(f"**Spending Trend**: {trend} by {abs(change):.1f}%")
    
    return insights

def generate_report(df):
    """Generate comprehensive text report"""
    if df.empty:
        return "No data available for report generation."
    
    report = "# 📊 EXPENSE REPORT\n\n"
    report += f"**Report Generated**: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}\n\n"
    
    report += "## Summary\n"
    report += f"- **Total Transactions**: {len(df)}\n"
    report += f"- **Total Amount**: ${df['amount'].sum():,.2f}\n"
    report += f"- **Average Transaction**: ${df['amount'].mean():.2f}\n"
    report += f"- **Largest Transaction**: ${df['amount'].max():.2f}\n"
    report += f"- **Smallest Transaction**: ${df['amount'].min():.2f}\n\n"
    
    if 'entry_method' in df.columns:
        report += "## Entry Methods\n"
        entry_counts = df['entry_method'].value_counts()
        for method, count in entry_counts.items():
            report += f"- **{method.title()}**: {count} transactions\n"
        report += "\n"
    
    report += "## Category Breakdown\n"
    category_stats = df.groupby('category')['amount'].agg(['sum', 'count', 'mean'])
    for category, row in category_stats.iterrows():
        report += f"- **{category}**: ${row['sum']:,.2f} ({int(row['count'])} transactions, avg ${row['mean']:.2f})\n"
    
    report += "\n## Monthly Trend\n"
    df['month'] = pd.to_datetime(df['date']).dt.to_period('M')
    monthly = df.groupby('month')['amount'].sum()
    for month, amount in monthly.items():
        report += f"- **{month}**: ${amount:,.2f}\n"
    
    return report

def generate_spoken_insights(df):
    """Generate insights optimized for voice"""
    insights = []
    
    if df.empty:
        return ["No expenses recorded yet."]
    
    total = df['amount'].sum()
    
    # Top category
    category_spending = df.groupby('category')['amount'].sum().sort_values(ascending=False)
    if not category_spending.empty:
        top_category = category_spending.index[0]
        top_amount = category_spending.values[0]
        percentage = (top_amount / total) * 100
        insights.append(f"Your highest spending category is {top_category} with {top_amount:.2f} dollars, representing {percentage:.1f} percent of total expenses.")
    
    # Current month summary
    current_month = datetime.now().month
    month_expenses = df[df['date'].dt.month == current_month]
    if not month_expenses.empty:
        month_total = month_expenses['amount'].sum()
        count = len(month_expenses)
        insights.append(f"This month you've spent {month_total:.2f} dollars across {count} transactions.")
    
    return insights