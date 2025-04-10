import streamlit as st
import sqlite3
import subprocess
import datetime

# -------------------------------
# SQLite Setup (NO FEEDBACK)
# -------------------------------
def init_db():
    conn = sqlite3.connect("farming_memory.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS interactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        agent TEXT,
        user_input TEXT,
        response TEXT
    )''')
    conn.commit()
    conn.close()

def save_to_db(agent, user_input, response):
    conn = sqlite3.connect("farming_memory.db")
    c = conn.cursor()
    c.execute("INSERT INTO interactions (timestamp, agent, user_input, response) VALUES (?, ?, ?, ?)",
              (datetime.datetime.now(), agent, user_input, response))
    conn.commit()
    conn.close()

# -------------------------------
# Call Ollama for agent response
# -------------------------------
def query_ollama(prompt, model="mistral"):
    try:
        result = subprocess.run(
            ["ollama", "run", model],
            input=prompt.encode(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        output = result.stdout.decode()
        return output.strip()
    except Exception as e:
        return f"⚠️ Error querying Ollama: {str(e)}"

# -------------------------------
# Streamlit UI
# -------------------------------
st.set_page_config(page_title="AgroIntelli - Smart Farming Assistant", layout="centered")
st.title("🌾 AgroIntelli")
st.subheader("Your AI-powered agricultural advisor 🤖")
st.markdown("Provide basic info about your farm to receive smart, sustainable suggestions.")

with st.form("farmer_input_form"):
    land_type = st.selectbox("🌱 Land Type", ["Loamy", "Clay", "Sandy"])
    crop_preference = st.text_input("🌾 Preferred Crop", "Rice")
    budget = st.number_input("💰 Budget (INR)", min_value=1000, step=500)
    submit = st.form_submit_button("Get Advice")

if submit:
    user_input = f"My land type is {land_type}. I prefer growing {crop_preference}. My budget is {budget} INR."

    st.markdown("### 🤖 AI Agents Responding...")

    # Farmer Advisor Agent
    farmer_prompt = f"You are an expert agricultural advisor. Given the land type '{land_type}', crop preference '{crop_preference}', and a budget of ₹{budget}, suggest a sustainable farming plan."
    farmer_response = query_ollama(farmer_prompt)
    st.success("👨‍🌾 Farmer Advisor:\n" + farmer_response)

    # Weather Agent
    weather_prompt = "You are a weather forecasting agent. Provide a forecast for the next 7 days and advice on sowing or irrigation based on moderate rainfall conditions."
    weather_response = query_ollama(weather_prompt)
    st.info("🌦 Weather Agent:\n" + weather_response)

    # Market Agent
    market_prompt = f"You are a market analysis agent. Based on the current season and regional demand, suggest if growing '{crop_preference}' is profitable."
    market_response = query_ollama(market_prompt)
    st.warning("📈 Market Agent:\n" + market_response)

    # ✅ Summary Box
    summary_prompt = f"Summarize the advice for a farmer with {land_type} land, growing {crop_preference}, and a budget of ₹{budget}. Include market outlook, irrigation tips, and profitability."
    summary_response = query_ollama(summary_prompt)
    st.markdown("**Summary:**")
    st.write(summary_response)

    # Save to DB without feedback
    save_to_db("FarmingAgents", user_input, summary_response)

    # 📄 Download Button
    report_text = f"""
    AgroIntelli Report
    ======================
    📅 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}

    🌱 Land Type: {land_type}
    🌾 Crop: {crop_preference}
    💰 Budget: ₹{budget}

    👨‍🌾 Farmer Advisor:
    {farmer_response}

    🌦 Weather Forecast:
    {weather_response}

    📈 Market Outlook:
    {market_response}

    📌 Summary:
    {summary_response}
    """
    st.download_button("Download Report", report_text, file_name="AgroIntelli_Report.txt")

# -------------------------------
# View Past Interactions
# -------------------------------
st.markdown("## View Past Interactions")
if st.button("Show History"):
    conn = sqlite3.connect("farming_memory.db")
    c = conn.cursor()
    c.execute("SELECT timestamp, agent, user_input, response FROM interactions ORDER BY timestamp DESC LIMIT 5")
    rows = c.fetchall()
    conn.close()

    for row in rows:
        st.markdown(f"""
        **🕒 {row[0]}**  
        **Agent:** {row[1]}  
        **Input:** {row[2]}  
        **Response:** {row[3]}  
        ---
        """)

# 🔄 Initialize DB
init_db()
