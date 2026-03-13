"""
Smart Expense Tracker Pro - Main Application
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from PIL import Image

# Import custom modules
from database import DatabaseManager
from ocr_scanner import ReceiptScanner
from voice_assistant import VoiceAssistant
from voice_entry import VoiceDataEntry
from analytics import predict_future_expenses, generate_insights, generate_report, generate_spoken_insights
from config import CATEGORIES, PAYMENT_METHODS, DEFAULT_VOICE_SPEED, DEFAULT_VOICE_VOLUME

# Page configuration
st.set_page_config(
    page_title="Smart Expense Tracker Pro",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .insight-box {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        margin: 10px 0;
    }
    .upload-box {
        border: 2px dashed #1f77b4;
        padding: 30px;
        border-radius: 10px;
        text-align: center;
        background-color: #f8f9fa;
    }
    .speaking-indicator {
        background-color: #4CAF50;
        color: white;
        padding: 10px;
        border-radius: 5px;
        text-align: center;
        animation: pulse 1.5s infinite;
    }
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    .success-box {
        background-color: #d4edda;
        border-left: 5px solid #28a745;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'db' not in st.session_state:
    st.session_state.db = DatabaseManager()
if 'voice_speed' not in st.session_state:
    st.session_state.voice_speed = DEFAULT_VOICE_SPEED
if 'voice_volume' not in st.session_state:
    st.session_state.voice_volume = DEFAULT_VOICE_VOLUME
if 'is_speaking' not in st.session_state:
    st.session_state.is_speaking = False
if 'auto_speak' not in st.session_state:
    st.session_state.auto_speak = False

def main():
    st.markdown('<h1 class="main-header">💰 Smart Expense Tracker Pro</h1>', unsafe_allow_html=True)
    
    # Initialize components
    voice_assistant = VoiceAssistant(st.session_state.voice_speed, st.session_state.voice_volume)
    receipt_scanner = ReceiptScanner()
    voice_entry = VoiceDataEntry(voice_assistant)
    db = st.session_state.db
    
    # Sidebar
    with st.sidebar:
        st.header("🎯 Navigation")
        page = st.radio("Go to", [
            "📊 Dashboard", 
            "➕ Add Expense", 
            "📷 Scan Receipt",
            "🎤 Voice Entry",
            "🤖 Voice Assistant", 
            "🔮 Predictions", 
            "📄 Reports", 
            "⚙️ Settings"
        ])
        
        st.markdown("---")
        
        # Voice Settings
        st.header("🔊 Voice Settings")
        voice_speed = st.slider("Speech Speed", 100, 200, st.session_state.voice_speed)
        voice_volume = st.slider("Volume", 0.0, 1.0, st.session_state.voice_volume, 0.1)
        
        if voice_speed != st.session_state.voice_speed or voice_volume != st.session_state.voice_volume:
            st.session_state.voice_speed = voice_speed
            st.session_state.voice_volume = voice_volume
            voice_assistant.set_voice_properties(voice_speed, voice_volume)
        
        st.markdown("---")
        
        # Database Stats
        st.header("📊 Database Stats")
        stats = db.get_stats()
        st.metric("Total Expenses", stats['total_expenses'])
        st.metric("Total Amount", f"${stats['total_amount']:,.2f}")
        
        st.markdown("---")
        
        # Data Export
        st.header("💾 Export Data")
        if st.button("📥 Download CSV"):
            df = db.get_all_expenses()
            if not df.empty:
                csv = df.to_csv(index=False)
                st.download_button(
                    label="💾 Download",
                    data=csv,
                    file_name=f"expenses_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            else:
                st.warning("No data to export")
    
    # Get expenses from database
    df = db.get_all_expenses()
    
    # Route to pages
    if page == "📊 Dashboard":
        show_dashboard(df, voice_assistant, db)
    elif page == "➕ Add Expense":
        show_add_expense(db, voice_assistant)
    elif page == "📷 Scan Receipt":
        show_scan_receipt(db, receipt_scanner, voice_assistant)
    elif page == "🎤 Voice Entry":
        show_voice_entry(db, voice_entry, voice_assistant)
    elif page == "🤖 Voice Assistant":
        show_voice_assistant(df, voice_assistant)
    elif page == "🔮 Predictions":
        show_predictions(df, voice_assistant)
    elif page == "📄 Reports":
        show_reports(df, voice_assistant)
    elif page == "⚙️ Settings":
        show_settings(db, voice_assistant)

def show_dashboard(df, voice_assistant, db):
    """Dashboard page"""
    st.header("📊 Dashboard")
    
    if df.empty:
        st.info("👋 Welcome! Start by adding your first expense using manual entry, voice, or receipt scanning.")
        st.markdown("""
        ### Quick Start Guide:
        1. **Manual Entry**: Click "➕ Add Expense" to enter data via form
        2. **Voice Entry**: Click "🎤 Voice Entry" to speak your expense
        3. **Scan Receipt**: Click "📷 Scan Receipt" to upload a receipt image
        """)
    else:
        # Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total = df['amount'].sum()
            st.metric("Total Spending", f"${total:,.2f}")
        
        with col2:
            this_month = df[pd.to_datetime(df['date']).dt.month == datetime.now().month]['amount'].sum()
            st.metric("This Month", f"${this_month:,.2f}")
        
        with col3:
            avg = df['amount'].mean()
            st.metric("Avg Transaction", f"${avg:.2f}")
        
        with col4:
            transactions = len(df)
            st.metric("Transactions", transactions)
        
        st.markdown("---")
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Spending by Category")
            category_data = df.groupby('category')['amount'].sum().reset_index()
            fig = px.pie(category_data, values='amount', names='category',
                       title='Category Distribution', hole=0.4,
                       color_discrete_sequence=px.colors.qualitative.Set3)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("📝 Entry Methods")
            if 'entry_method' in df.columns:
                entry_data = df.groupby('entry_method')['amount'].sum().reset_index()
                fig = px.bar(entry_data, x='entry_method', y='amount',
                           title='Expenses by Entry Method',
                           color='amount', color_continuous_scale='Viridis')
                st.plotly_chart(fig, use_container_width=True)
        
        # Timeline
        st.subheader("📅 Spending Timeline")
        daily_spending = df.groupby('date')['amount'].sum().reset_index()
        fig = px.line(daily_spending, x='date', y='amount',
                     title='Daily Spending Trend', markers=True)
        fig.update_traces(line_color='#1f77b4')
        st.plotly_chart(fig, use_container_width=True)
        
        # Insights
        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader("💡 Insights")
        with col2:
            if st.button("🔊 Speak Insights"):
                insights = generate_spoken_insights(df)
                for insight in insights:
                    voice_assistant.speak(insight)
        
        insights = generate_insights(df)
        for insight in insights:
            st.markdown(f'<div class="insight-box">{insight}</div>', unsafe_allow_html=True)
        
        # Recent Transactions
        st.subheader("📜 Recent Transactions")
        recent = df.sort_values('timestamp', ascending=False).head(10)
        
        for idx, row in recent.iterrows():
            col1, col2, col3, col4, col5, col6 = st.columns([2, 2, 1, 2, 2, 1])
            with col1:
                st.write(str(row['date'])[:10])
            with col2:
                st.write(row['category'])
            with col3:
                st.write(f"${row['amount']:.2f}")
            with col4:
                desc = str(row['description'])[:30] if row['description'] else ''
                st.write(desc)
            with col5:
                st.write(row.get('entry_method', 'manual'))
            with col6:
                if st.button("🗑️", key=f"del_{row['id']}"):
                    db.delete_expense(row['id'])
                    st.rerun()

def show_add_expense(db, voice_assistant):
    """Manual expense entry page"""
    st.header("➕ Add New Expense (Manual)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        date = st.date_input("Date", datetime.now())
        category = st.selectbox("Category", CATEGORIES)
        amount = st.number_input("Amount ($)", min_value=0.01, step=0.01, format="%.2f")
    
    with col2:
        payment_method = st.selectbox("Payment Method", PAYMENT_METHODS)
        description = st.text_area("Description", placeholder="e.g., Lunch at cafe")
    
    if st.button("💾 Add Expense", type="primary"):
        if amount > 0:
            expense_id = db.add_expense(
                date=date,
                category=category,
                amount=amount,
                description=description,
                payment_method=payment_method,
                entry_method='manual'
            )
            st.success("✅ Expense added successfully!")
            voice_assistant.speak(f"Expense of {amount:.2f} dollars added to {category}")
            st.balloons()
        else:
            st.error("Please enter a valid amount")

def show_scan_receipt(db, receipt_scanner, voice_assistant):
    """OCR receipt scanning page"""
    st.header("📷 Scan Receipt (OCR)")
    
    st.markdown("""
    <div class="upload-box">
        <h3>📸 Upload Receipt Image</h3>
        <p>Supported formats: JPG, PNG, JPEG</p>
        <p>For best results, ensure the receipt is well-lit and flat</p>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("Choose a receipt image", type=['jpg', 'png', 'jpeg'])
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.image(image, caption='Uploaded Receipt', use_container_width=True)
        
        with col2:
            st.subheader("🔍 Processing...")
            
            with st.spinner("Scanning receipt..."):
                text = receipt_scanner.extract_text(image)
                data = receipt_scanner.parse_receipt(text)
            
            st.success("✅ Receipt scanned!")
            
            st.subheader("Extracted Data")
            
            date = st.date_input("Date", value=data['date'])
            category = st.selectbox("Category", CATEGORIES,
                                   index=CATEGORIES.index(data['category']) if data['category'] in CATEGORIES else 0)
            
            amount = st.number_input("Amount ($)", 
                                    value=float(data['amount']) if data['amount'] else 0.0,
                                    min_value=0.01, step=0.01, format="%.2f")
            
            description = st.text_input("Description", 
                                       value=data['merchant'] if data['merchant'] else '')
            
            payment_method = st.selectbox("Payment Method", PAYMENT_METHODS)
            
            with st.expander("📄 View Raw OCR Text"):
                st.text(text)
            
            if st.button("💾 Save Expense", type="primary"):
                if amount > 0:
                    expense_id = db.add_expense(
                        date=date,
                        category=category,
                        amount=amount,
                        description=description,
                        payment_method=payment_method,
                        entry_method='ocr'
                    )
                    
                    receipt_path = receipt_scanner.save_receipt_image(image, expense_id)
                    db.update_expense(expense_id, receipt_image_path=receipt_path)
                    
                    st.success("✅ Expense saved with receipt image!")
                    voice_assistant.speak(f"Receipt scanned and expense of {amount:.2f} dollars added")
                    st.balloons()
                else:
                    st.error("Please verify the amount")

def show_voice_entry(db, voice_entry, voice_assistant):
    """Voice-based expense entry page"""
    st.header("🎤 Voice Expense Entry")
    
    st.info("""
    **How it works:**
    1. Click the button below
    2. Answer the voice prompts clearly
    3. Review the collected data
    4. Confirm and save
    
    **Tips:**
    - Speak clearly at normal pace
    - Say numbers naturally (e.g., "fifteen dollars and fifty cents")
    - For categories, just say the main word (e.g., "food" or "shopping")
    """)
    
    if st.button("🎤 Start Voice Entry", type="primary", use_container_width=True):
        with st.spinner("🎙️ Listening..."):
            expense_data = voice_entry.collect_expense_by_voice()
        
        if expense_data and expense_data['amount']:
            st.success("✅ Voice data collected!")
            
            st.subheader("📝 Review Your Expense")
            
            col1, col2 = st.columns(2)
            
            with col1:
                date = st.date_input("Date", value=expense_data['date'])
                category = st.selectbox("Category", CATEGORIES,
                                       index=CATEGORIES.index(expense_data['category']) if expense_data['category'] in CATEGORIES else 0)
                amount = st.number_input("Amount ($)", value=expense_data['amount'], min_value=0.01, format="%.2f")
            
            with col2:
                payment_method = st.selectbox("Payment Method", PAYMENT_METHODS,
                                             index=PAYMENT_METHODS.index(expense_data['payment_method']) if expense_data['payment_method'] in PAYMENT_METHODS else 0)
                description = st.text_area("Description", value=expense_data['description'])
            
            if st.button("💾 Confirm & Save", type="primary"):
                db.add_expense(
                    date=date,
                    category=category,
                    amount=amount,
                    description=description,
                    payment_method=payment_method,
                    entry_method='voice'
                )
                st.success("✅ Expense saved!")
                voice_assistant.speak(f"Expense of {amount:.2f} dollars saved successfully")
                st.balloons()
        else:
            st.error("❌ Could not collect expense data. Please try manual entry.")

def show_voice_assistant(df, voice_assistant):
    """Voice assistant command page"""
    st.header("🤖 AI Voice Assistant")
    
    if st.session_state.is_speaking:
        st.markdown('<div class="speaking-indicator">🔊 Speaking...</div>', unsafe_allow_html=True)
    
    st.info("""
    **Voice Commands:**
    - "Add expense" - Start voice expense entry
    - "Scan receipt" - Upload receipt to scan
    - "Read report" - Full expense report
    - "Total spending" - Hear total
    - "Spending by category" - Category breakdown
    - "This month" - Current month summary
    - "Help" - See all commands
    """)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🎤 Voice Command", type="primary", use_container_width=True):
            with st.spinner("Listening..."):
                command = voice_assistant.listen()
                
                if command in ["timeout", "could not understand", "service unavailable"]:
                    st.error(f"❌ {command.replace('_', ' ').title()}")
                else:
                    st.success(f"✅ You said: *{command}*")
                    
                    action, response = voice_assistant.process_voice_command(command, df)
                    
                    st.markdown(f"**Assistant:** {response}")
                    voice_assistant.speak(response)
    
    with col2:
        if st.button("📊 Read Summary", use_container_width=True):
            if not df.empty:
                total = df['amount'].sum()
                count = len(df)
                avg = df['amount'].mean()
                text = f"You have {count} transactions totaling {total:.2f} dollars with an average of {avg:.2f} dollars per transaction"
                voice_assistant.speak(text)
            else:
                voice_assistant.speak("No expenses recorded yet")
    
    with col3:
        if st.button("💡 Read Insights", use_container_width=True):
            if not df.empty:
                insights = generate_spoken_insights(df)
                for insight in insights:
                    voice_assistant.speak(insight)
            else:
                voice_assistant.speak("No data available for insights")

def show_predictions(df, voice_assistant):
    """Predictions page"""
    st.header("🔮 Expense Predictions")
    
    if df.empty or len(df) < 7:
        st.warning("⚠️ Need at least 7 days of expense data for predictions")
        st.info("Add more expenses to see predictions!")
    else:
        days_ahead = st.slider("Predict for next (days)", 7, 90, 30)
        
        pred_df, pred_text = predict_future_expenses(df, days_ahead)
        
        if pred_df is not None:
            st.success(pred_text)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📈 Prediction Chart")
                fig = px.line(pred_df, x='date', y='predicted_amount',
                            title=f'Predicted Spending (Next {days_ahead} Days)',
                            markers=True)
                fig.update_traces(line_color='#ff4b4b')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader("📊 Summary")
                total_pred = pred_df['predicted_amount'].sum()
                avg_pred = pred_df['predicted_amount'].mean()
                
                st.metric("Total Predicted", f"${total_pred:,.2f}")
                st.metric("Daily Average", f"${avg_pred:.2f}")
                
                if st.button("🔊 Speak Prediction"):
                    voice_assistant.speak(pred_text)

def show_reports(df, voice_assistant):
    """Reports page"""
    st.header("📄 Reports")
    
    if df.empty:
        st.info("No data available for reports. Start adding expenses!")
    else:
        report = generate_report(df)
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(report)
        with col2:
            st.download_button(
                label="📥 Download",
                data=report,
                file_name=f"expense_report_{datetime.now().strftime('%Y%m%d')}.md",
                mime="text/markdown"
            )
            if st.button("🔊 Read Report"):
                voice_assistant.speak(report[:500])  # First 500 chars

def show_settings(db, voice_assistant):
    """Settings page"""
    st.header("⚙️ Settings")
    
    tab1, tab2 = st.tabs(["💰 Budget Settings", "📊 Database Info"])
    
    with tab1:
        st.subheader("Set Monthly Budgets")
        
        budgets = db.get_budgets()
        
        for category in CATEGORIES:
            col1, col2 = st.columns([3, 1])
            with col1:
                budget = st.number_input(f"{category}", 
                                        min_value=0.0, 
                                        value=float(budgets.get(category, 0)),
                                        key=f"budget_{category}",
                                        format="%.2f")
            with col2:
                if st.button("💾", key=f"save_{category}"):
                    db.set_budget(category, budget)
                    st.success("✅")
    
    with tab2:
        stats = db.get_stats()
        st.metric("Total Records", stats['total_expenses'])
        st.metric("Total Amount", f"${stats['total_amount']:,.2f}")
        st.info("Database file: expenses.db")

if __name__ == "__main__":
    main()