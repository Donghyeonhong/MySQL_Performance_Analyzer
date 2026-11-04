from flask import Flask, render_template
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from Automation import db_connection


app = Flask(__name__)

@app.route("/")
def index():
    conn = None
    cursor = None
    try:
        conn = db_connection.get_db_connection_analysis()
        cursor = conn.cursor()
        print("analysis_db 연결 성공")
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
