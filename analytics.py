# analytics.py
# Pandas-powered analytics engine for Finance Dashboard

import pandas as pd
import numpy as np
from datetime import datetime

def get_dataframe(expenses):
    """Convert list of expense dicts to a Pandas DataFrame"""
    if not expenses:
        return pd.DataFrame()
    
    df = pd.DataFrame(expenses)
    df['expense_date'] = pd.to_datetime(df['expense_date'])
    df['month'] = df['expense_date'].dt.to_period('M').astype(str)
    df['amount'] = pd.to_numeric(df['amount'])
    return df

def category_breakdown(expenses):
    """Total spending per category"""
    df = get_dataframe(expenses)
    if df.empty:
        return []
    
    breakdown = df.groupby('category')['amount'].sum().reset_index()
    breakdown = breakdown.sort_values('amount', ascending=False)
    return breakdown.to_dict(orient='records')

def monthly_trend(expenses):
    """Total spending per month"""
    df = get_dataframe(expenses)
    if df.empty:
        return []
    
    trend = df.groupby('month')['amount'].sum().reset_index()
    trend = trend.sort_values('month')
    return trend.to_dict(orient='records')

def summary_stats(expenses):
    """Key summary numbers for dashboard cards"""
    df = get_dataframe(expenses)
    if df.empty:
        return {}

    total = float(df['amount'].sum())
    average = float(df['amount'].mean())
    highest = df.loc[df['amount'].idxmax()]
    current_month = datetime.now().strftime('%Y-%m')
    monthly = df[df['month'] == current_month]['amount'].sum()

    return {
        'total_spent':     round(total, 2),
        'average_expense': round(average, 2),
        'highest_expense': {
            'title':  highest['title'],
            'amount': round(float(highest['amount']), 2)
        },
        'this_month': round(float(monthly), 2)
    }

def ai_insights(expenses):
    """Rule-based spending suggestions"""
    df = get_dataframe(expenses)
    if df.empty:
        return []

    insights = []
    total = df['amount'].sum()

    # Category percentages
    cat = df.groupby('category')['amount'].sum()
    cat_pct = (cat / total * 100).round(1)

    for category, pct in cat_pct.items():
        if category == 'Food & Dining' and pct > 35:
            insights.append({
                'type': 'warning',
                'icon': '🍔',
                'message': f'You spent {pct}% on Food & Dining. Try cooking at home more often to save money.'
            })
        elif category == 'Entertainment' and pct > 20:
            insights.append({
                'type': 'warning',
                'icon': '🎬',
                'message': f'Entertainment is {pct}% of spending. Consider reviewing subscriptions.'
            })
        elif category == 'Education' and pct > 5:
            insights.append({
                'type': 'positive',
                'icon': '📚',
                'message': f'Great! You are investing {pct}% in Education. Keep it up!'
            })
        elif category == 'Health' and pct > 15:
            insights.append({
                'type': 'info',
                'icon': '💊',
                'message': f'Health spending is at {pct}%. Make sure these are necessary expenses.'
            })
        elif category == 'Shopping' and pct > 25:
            insights.append({
                'type': 'warning',
                'icon': '🛍️',
                'message': f'Shopping is {pct}% of your budget. Try the 24-hour rule before buying.'
            })

    # Monthly trend insight
    monthly = df.groupby('month')['amount'].sum()
    if len(monthly) >= 2:
        last_two = monthly.iloc[-2:]
        change = ((last_two.iloc[-1] - last_two.iloc[-2]) / last_two.iloc[-2] * 100).round(1)
        if change > 20:
            insights.append({
                'type': 'warning',
                'icon': '📈',
                'message': f'Your spending increased by {change}% compared to last month!'
            })
        elif change < -10:
            insights.append({
                'type': 'positive',
                'icon': '📉',
                'message': f'Great job! Your spending dropped by {abs(change)}% vs last month.'
            })

    if not insights:
        insights.append({
            'type': 'positive',
            'icon': '✅',
            'message': 'Your spending looks balanced! Keep tracking to stay on top.'
        })

    return insights