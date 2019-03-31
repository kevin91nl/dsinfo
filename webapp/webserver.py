from flask import Flask, render_template

app = Flask(__name__, static_url_path='/static')


@app.route("/")
def render_root():
    return render_template('base.html')


if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(host='0.0.0.0')
