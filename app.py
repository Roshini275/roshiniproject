from flask import Flask, request, jsonify
import pandas as pd
import matplotlib.pyplot as plt
import io, base64
from datetime import datetime

app = Flask(__name__)

# store expenses in memory
expenses = []
next_id = 1

# Utility: parse date
def parse_date(text):
    try:
        return datetime.strptime(text, "%Y-%m-%d").date()
    except:
        return datetime.today().date()

# Utility: assign range
def get_range(amount):
    if amount < 1000: return "0-1000"
    elif amount < 2000: return "1000-2000"
    elif amount < 5000: return "2000-5000"
    else: return "5000+"

# Utility: generate chart and return base64 string
def generate_chart(chart_type="pie"):
    if not expenses:
        return None

    df = pd.DataFrame(expenses)

    fig, ax = plt.subplots()

    if chart_type == "pie":
        df.groupby("category")["amount"].sum().plot.pie(autopct="%.1f%%", ax=ax)
        ax.set_ylabel("")
        ax.set_title("Expenses by Category")
    elif chart_type == "bar":
        df.groupby("category")["amount"].sum().plot(kind="bar", ax=ax)
        ax.set_ylabel("Amount Spent")
        ax.set_title("Expenses by Category (Bar Chart)")
    elif chart_type == "line":
        df.groupby("date")["amount"].sum().plot(kind="line", marker="o", ax=ax)
        ax.set_ylabel("Daily Spending")
        ax.set_title("Spending Trend")

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    chart_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    buf.close()
    return chart_base64

# 🟢 Chat route
@app.route("/chat", methods=["POST"])
def chat():
    global next_id
    msg = request.json["message"]

    # Check if user wants graph directly
    if "bar" in msg.lower():
        chart = generate_chart("bar")
        return jsonify({"reply": "📊 Here’s your bar chart!", "chart": chart})
    elif "line" in msg.lower():
        chart = generate_chart("line")
        return jsonify({"reply": "📈 Here’s your spending trend!", "chart": chart})

    # extract amount
    words = msg.split()
    amount = None
    for w in words:
        try:
            amount = float(w)
            break
        except:
            continue

    # detect category
    category = "Other"
    if "food" in msg.lower(): category = "Food"
    elif "travel" in msg.lower(): category = "Travel"
    elif "bill" in msg.lower(): category = "Bills"
    elif "shop" in msg.lower() or "amazon" in msg.lower(): category = "Shopping"
    elif "medicine" in msg.lower() or "health" in msg.lower(): category = "Healthcare"

    # extract date (or default today)
    date = datetime.today().date()
    for w in words:
        try:
            date = datetime.strptime(w, "%Y-%m-%d").date()
            break
        except:
            continue

    if amount:
        expenses.append({
            "id": next_id,
            "message": msg,
            "amount": amount,
            "category": category,
            "date": str(date),
            "range": get_range(amount)
        })
        next_id += 1

    # Generate updated pie chart
    chart = generate_chart("pie")
    reply = f"Got it ✅ Logged ₹{amount} under {category} on {date}."

    return jsonify({"reply": reply, "expenses": expenses, "chart": chart})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)