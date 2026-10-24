from flask import Flask, render_template, request, redirect
import json, os
from datetime import date
import calendar

app = Flask(__name__)
FILE = "members.json"

def load():
    if os.path.exists(FILE):
        try:
            with open(FILE) as f:
                data = json.load(f)
                for i, m in enumerate(data):
                    m["id"] = i  # 🔥 ASLI NUMBER SAVE KAR DIYA
                    if "attendance" not in m or isinstance(m["attendance"], str):
                        m["attendance"] = {}
                    if "status" not in m:
                        m["status"] = "PENDING"
                return data
        except:
            return []
    return []

def save(d):
    # id save nahi karna - extra field hata de
    for m in d:
        if "id" in m:
            del m["id"]
    with open(FILE,"w") as f:
        json.dump(d,f)

@app.route("/")
def home():
    all_members = load()
    q = request.args.get("q","")
    search_result = []
    if q:
        search_result = [m for m in all_members if q.lower() in m['name'].lower() or q in m['phone']]
    total = sum(int(m['fees']) for m in all_members if m['status']=="PAID")
    pending = sum(1 for m in all_members if m['status']=="PENDING")
    return render_template("gym.html", members=all_members, search_result=search_result, q=q, total=total, pending=pending, count=len(all_members))

@app.route("/add", methods=["POST"])
def add():
    m = load()
    m.append({
        "name": request.form["name"],
        "phone": request.form["phone"],
        "plan": request.form["plan"],
        "fees": request.form["fees"],
        "status":"PENDING",
        "attendance": {}
    })
    save(m)
    return redirect("/")

@app.route("/paid/<int:id>")
def paid(id):
    m = load()
    if id < len(m):
        m[id]["status"] = "PAID" if m[id]["status"]=="PENDING" else "PENDING"
        save(m)
    return redirect("/")

@app.route("/delete/<int:id>")
def delete(id):
    m = load()
    if id < len(m):
        m.pop(id)
        save(m)
    return redirect("/")

@app.route("/member/<int:id>")
def member(id):
    all_m = load()
    if id >= len(all_m):
        return redirect("/")  # 🔥 GALAT ID HO TO WAPAS HOME PE
    m = all_m[id]
    att = m.get("attendance", {})
    if isinstance(att, str):
        att = {}
    today = date.today()
    year = today.year
    month = today.month
    days_in_month = calendar.monthrange(year, month)[1]
    present = 0
    absent = 0
    daily = []
    for d in range(1, days_in_month+1):
        dt = f"{year}-{month:02d}-{d:02d}"
        status = att.get(dt, "-")
        if status == "P":
            present += 1
        elif status == "A":
            absent += 1
        daily.append({"date": dt, "day": d, "status": status})
    return render_template("member.html", m=m, id=id, present=present, absent=absent, daily=daily, month_name=calendar.month_name[month], year=year)

@app.route("/mark/<int:id>/<date_str>/<status>")
def mark(id, date_str, status):
    m = load()
    if id < len(m):
        if "attendance" not in m[id] or isinstance(m[id]["attendance"], str):
            m[id]["attendance"] = {}
        m[id]["attendance"][date_str] = status
        save(m)
    return redirect(f"/member/{id}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
