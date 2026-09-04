from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key-auruda'
socketio = SocketIO(app, cors_allowed_origins="*")

# 임시 메모리 데이터베이스 (게시글 저장)
posts = [
    {
        'id': 1,
        'region': '남',
        'author': '익명(남)',
        'content': '북한 친구들은 요즘 어떤 음악 자주 들어?',
        'likes': 3
    }
]

# 1. 메인 페이지
@app.route('/')
def index():
    return render_template('index.html')

# 2. 게시판 API
@app.route('/api/posts', methods=['GET'])
def get_posts():
    return jsonify(posts)

@app.route('/api/posts', methods=['POST'])
def create_post():
    data = request.json
    region = data.get('region', '남')
    content = data.get('content', '')
    
    new_post = {
        'id': len(posts) + 1,
        'region': region,
        'author': f"익명({'북' if region == '북' else '남'})",
        'content': content,
        'likes': 0
    }
    posts.insert(0, new_post)
    return jsonify(new_post), 201

# 3. 실시간 소켓 채팅
@socketio.on('joinChat')
def handle_join(data):
    # data: {'nickname': '...', 'region': '남/북'}
    nickname = data.get('nickname')
    region = data.get('region')
    region_label = '북측' if region == '북' else '남측'
    emit('systemMessage', f"{nickname}({region_label}) 님이 입장하셨습니다.", broadcast=True)

@socketio.on('chatMessage')
def handle_message(data):
    # data: {'nickname': '...', 'region': '남/북', 'text': '...'}
    emit('message', data, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
