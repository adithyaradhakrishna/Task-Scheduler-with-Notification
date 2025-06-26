from flask import Flask, request, redirect, render_template_string
import sqlite3
import string

# Initialize app
app = Flask(__name__)

# Base62 characters for encoding/decoding
BASE62 = string.digits + string.ascii_letters

# Connect to database (auto-create if not exists)
conn = sqlite3.connect('urls.db', check_same_thread=False)
c = conn.cursor()
c.execute('''
    CREATE TABLE IF NOT EXISTS urls (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT NOT NULL
    )
''')
conn.commit()

# Encoding function: int → short string
def encode(num):
    s = ""
    while num > 0:
        s = BASE62[num % 62] + s
        num //= 62
    return s or "0"

# Decoding function: short string → int
def decode(short_code):
    num = 0
    for c in short_code:
        if c not in BASE62:
            raise ValueError("Invalid short code")
        num = num * 62 + BASE62.index(c)
    return num

# Main page (input form)
@app.route('/', methods=['GET', 'POST'])
def index():
    short_url = None
    if request.method == 'POST':
        long_url = request.form['long_url']
        c.execute("INSERT INTO urls (url) VALUES (?)", (long_url,))
        conn.commit()
        url_id = c.lastrowid
        short_url = request.host_url + encode(url_id)
    return render_template_string('''
        <h2>URL Shortener</h2>
        <form method="post">
            <input type="text" name="long_url" placeholder="Enter URL" size="50" required>
            <input type="submit" value="Shorten">
        </form>
        {% if short_url %}
            <p>Short URL: <a href="{{ short_url }}">{{ short_url }}</a></p>
        {% endif %}
    ''', short_url=short_url)

# Redirect from short → long URL
@app.route('/<short_code>')
def redirect_short_url(short_code):
    try:
        url_id = decode(short_code)
        c.execute("SELECT url FROM urls WHERE id=?", (url_id,))
        result = c.fetchone()
        if result:
            return redirect(result[0])
        else:
            return "Invalid short URL", 404
    except Exception as e:
        return f"Error: {str(e)}", 400

# Ignore favicon.ico errors
@app.route('/favicon.ico')
def favicon():
    return '', 204

# Run the app
if __name__ == '__main__':
    app.run(debug=True)

