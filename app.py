import os
from flask import Flask, request, render_template
from twitter_app import get_followers, update_weekly_and_hourly_stats
app = Flask(__name__, template_folder="templates")


@app.route('/', methods=['POST', 'GET'])
def index():
    weekly_status = {}
    hourly_status = {}
    username = None
    if request.method == 'POST':
        username = request.form.get('username')
        tweets_time = get_followers(username)
        weekly_status = update_weekly_and_hourly_stats(tweets_time)
        # import ipdb;ipdb.set_trace()
        # print weekly_status, hourly_status
    return render_template("index.html",
                           weekly_status=weekly_status,
                           username=username)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', threaded=True, port=port)
