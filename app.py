from flask import Flask, render_template, request, redirect, url_for, flash
import csv
import random
import os

app = Flask(__name__)
app.secret_key = "a-very-secret-key"

NAMES_FILE = "names.txt"
ASSIGNED_FILE = "assigned.csv"


def load_names():
    if not os.path.exists(NAMES_FILE):
        return {}

    with open(NAMES_FILE, "r", encoding="utf-8-sig", errors="ignore") as f:
        names = [n.strip() for n in f if n.strip()]

    # Return a dictionary: lowercase → original
    return {name.lower(): name for name in names}


def load_assigned():
    assigned = {}
    if not os.path.exists(ASSIGNED_FILE):
        return assigned

    with open(ASSIGNED_FILE, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) == 2:
                giver, receiver = row
                assigned[giver.lower()] = receiver  # Normalize giver to lowercase

    return assigned


def save_assignment(giver, receiver):
    with open(ASSIGNED_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([giver, receiver])


@app.route("/", methods=["GET", "POST"])
def index():
    names_dict = load_names()           # { "disha": "Disha", "rajiv": "Rajiv", ... }
    assigned = load_assigned()          # { "disha": "John", ... }

    if request.method == "POST":
        giver = request.form.get("giver", "").strip()
        giver_lower = giver.lower()     # Normalized for matching

        if giver_lower == "":
            flash("Please enter your name", "error")
            return redirect(url_for("index"))

        if giver_lower not in names_dict:
            flash("Your name is not in the participant list.", "error")
            return redirect(url_for("index"))

        real_giver = names_dict[giver_lower]   # Proper casing ("Disha")

        # Already assigned?
        if giver_lower in assigned:
            receiver = assigned[giver_lower]
            return render_template("result.html", giver=real_giver, receiver=receiver, already=True)

        # Determine available receivers
        taken = set(assigned.values())
        all_names = list(names_dict.values())

        possible = [n for n in all_names if n not in taken and n.lower() != giver_lower]

        if not possible:
            flash("No valid names left to assign!", "error")
            return redirect(url_for("index"))

        receiver = random.choice(possible)

        # Save using original-giver-name and original-receiver-name
        save_assignment(real_giver, receiver)

        return render_template("result.html", giver=real_giver, receiver=receiver, already=False)

    return render_template("index.html")


# 🚀 START THE FLASK SERVER
if __name__ == "__main__":
    app.run(debug=True)
