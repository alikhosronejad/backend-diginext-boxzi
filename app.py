from flask import Flask, request, jsonify
from datetime import datetime
from collections import defaultdict

app = Flask(__name__)

users = defaultdict(lambda: {"followers": set(), "following": set()})
followers_count_daily = defaultdict(list)

def record_daily_followers_count():
    today = datetime.now().strftime('%Y-%m-%d')
    for user, data in users.items():
        count = len(data["followers"])
        if followers_count_daily[user] and followers_count_daily[user][-1]['date'] == today:
            followers_count_daily[user][-1]['count'] = count
        else:
            followers_count_daily[user].append({"date": today, "count": count})

@app.route('/follow', methods=['POST'])
def follow():
    data = request.json
    follower = data['follower']
    followee = data['followee']

    if follower == followee:
        return jsonify({"error": "User cannot follow themselves"}), 400

    users[follower]["following"].add(followee)
    users[followee]["followers"].add(follower)
    record_daily_followers_count()

    return jsonify({"message": f"{follower} is now following {followee}"}), 200

@app.route('/unfollow', methods=['POST'])
def unfollow():
    data = request.json
    follower = data['follower']
    followee = data['followee']

    users[follower]["following"].discard(followee)
    users[followee]["followers"].discard(follower)
    record_daily_followers_count()

    return jsonify({"message": f"{follower} has unfollowed {followee}"}), 200

@app.route('/followers/<username>', methods=['GET'])
def get_followers(username):
    today = datetime.now().strftime('%Y-%m-%d')
    if followers_count_daily[username] and followers_count_daily[username][-1]['date'] != today:
        record_daily_followers_count()
    return jsonify(followers_count_daily[username]), 200

@app.route('/common-followers', methods=['GET'])
def common_followers():
    user1 = request.args.get('user1')
    user2 = request.args.get('user2')

    if user1 not in users or user2 not in users:
        return jsonify({"error": "One or both users not found"}), 404

    common = users[user1]["followers"].intersection(users[user2]["followers"])
    return jsonify(list(common)), 200

if __name__ == '__main__':
    app.run(debug=True)
