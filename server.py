from flask import Flask


app = Flask(
    title = 'MBT'
)

@app.route('/api/1.0/auth')
def index():
    return 'Hello world'

if __name__ == '__main__':
    app.run(debug=False)