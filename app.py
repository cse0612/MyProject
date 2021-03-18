# render_template은 flask가 사이트의 내용을 HTML기반으로 표현하기 위해 사용된다
# post로 입력된 데이터를 실제 사용하기 위해서는 request를 사용한다
from flask import Flask, session, flash, render_template, url_for, request, redirect
import mysql.connector
from datetime import date
from models import Database  # models.py
import sys, os



# Flask 인스턴스 생성
app = Flask(__name__) 
#message Flash, Session 기능을 사용하기 위해서는 SECRET_KEY를 반드시 설정 
app.secret_key = b'1234asdfasfd'    # secret_key는 서버 app의 config에 저장


# Request Root 
@app.route('/')          
# Request Home
@app.route("/home")
def home(): 
  if "id" in session:
    db = Database()
    query = "SELECT id, img_src, comment From post WHERE id_user=%s"
    sql_rows = db.executeAll(query, (session['id'],))
    return render_template('index.html', data=sql_rows)
  else:
    return render_template("index.html")

# def index():
#   if "id" in session:
#     db = Database()
#     query = "SELECT id, img_src, comment From post WHERE id_user=%s"
#     sql_rows = db.executeAll(query, (session['id'],))
#     return render_template('index.html', data=sql_rows)
#   else:
#     return render_template("index.html")

# Request Post Link
@app.route('/post')      
def post(): 
  if "id" in session:
    return render_template('post.html', id=request.args.get('id'), img_src=request.args.get('img_src'), comment=request.args.get('comment'))
  else:
    flash("로그인 후 이용가능합니다")
    return render_template('login.html')

# Upload Post & Image File
@app.route('/upload_post', methods = ['GET', 'POST'])
def upload_post():
  if request.method == 'POST': # POST 방식 (캡슐 및 큰데이터 전송시 사용)
    comment = request.form['comment']
    f = request.files['imgfile']
    img_src ="./static/img/"+f.filename
    print("f.filename >>>>" + f.filename, file=sys.stderr) 
    
    # File Upload 
    if f.filename:  # 새 업로드 파일이 있다면
      if os.path.exists(img_src): # 기존파일체크후
        os.remove(img_src)  # 기존파일삭제
      f.save('./static/img/' + f.filename)   # 파일저장 ==> flask 파일route방식 static 사용
      #f.save('./static/img/' + secure_filename(img_src)))  # 암호화
    else:  # 업로드파일 없을경우
      if request.form['old_img']:
        f.filename = request.form['old_img']  # 기존 이미지파일명 사용
      else:
        flash("업로드할 이미지파일을 다시 선택하세요")
        return redirect(url_for('home'))
    # DB Update
    db = Database()
    if request.form['id']:  # update 
      query = "UPDATE post SET img_src=%s, comment=%s WHERE id=%s"
      db.execute_db(query, [f.filename, comment, request.form['id']])
    else: # new registry
      query = "INSERT INTO post (img_src, comment, id_user) VALUES(%s, %s, %s)"
      db.execute_db(query, [f.filename, comment, session['id']])
    db.conn.close()
    flash('포스트 등록되었습니다')
    return redirect(url_for('home'))

# Request login Link
@app.route('/login')
def login():
  return render_template('login.html')

# Login submit 
@app.route('/check_login', methods=['POST']) 
def check_login():
  if request.method == 'POST':  
    member_id = request.form['id']
    member_pw = request.form["pw"]
    # 입력유무 체크
    if member_id == "" or member_pw == "":
      flash("[빈값입력오류] \\n입력이 잘못되었습니다. 다시 로그인하세요")
      return render_template("login.html")
    # login checking 
    db = Database()
    query = "SELECT id, pw, name, auth FROM user WHERE id = %s and pw = %s"
    rows = db.executeAll(query, (member_id, member_pw))
    for (id, pw, name, auth) in rows:
      member_id = id
      member_name = name
      member_auth = auth

    if len(rows) == 0:
      db.conn.close()
      flash('아이디와 비밀번호가 틀렸습니다!')
      return render_template("login.html")
    else:
      # log info in session 
      session['id'] = member_id       
      session['name'] = member_name
      session['auth'] = member_auth   # admin session  (admin == 1)
      db.conn.close()
      return redirect(url_for('home'))

# Logout 
@app.route('/logout')      
def logout(): 
  session.pop('id', None)    # Session id 메모리주소값 = 빈값으로 대체
  session.pop('name', None) 
  session.pop('auth', None) 
  flash('로그아웃되었습니다')
  return redirect(url_for('home'))
    
# Join & Update Member page Request
@app.route('/member', methods=['POST', 'GET'])
def member():
  if 'id' in session:   
    db = Database() 
    query = "SELECT * FROM user WHERE id = %s"
    rows = db.executeAll(query, (session['id'],))
    db.conn.close()
    return render_template('up_member.html', rows=rows) # 수정페이지 이동
  else: 
    return render_template('member.html') # 등록페이지 이동

# Update member_info 
@app.route('/update_member', methods=['POST', 'GET'])
def update_member():
  if request.method == 'POST':
    # member_date = date.today()  # 오늘날짜 in <from datetime import date>
    db = Database()
    query = "UPDATE user SET pw = %s, name=%s, email=%s WHERE id=%s"
    db.execute_db(query, [request.form['pw'], request.form['name'], request.form['email'], request.form['id']])
    db.conn.close()
    # print(f"query>>> {query}")
    flash('회원 수정이 완료되었습니다.')
    return redirect(url_for('home'))

# Registry new member
@app.route('/new_member', methods=['POST', 'GET'])
def new_member():
  if request.method == 'POST':
    db = Database()
    # return value >>  중복된 ID값 Query 
    row_count = db.search_duplicate(request.form['id']) 
    if row_count >= 1: # DB에 같은 값이 존재할경우
      flash('중복된 아이디가 존재합니다')
      db.conn.close()
      return redirect(url_for('member'))
    else:
      query = "INSERT INTO user (id, pw, name, email) VALUES (%s, %s, %s, %s)"
      db.execute_db(query, [request.form['id'], request.form['pw'], request.form['name'], request.form['email']])
      db.conn.close()
      flash('회원등록을 완료했습니다')
      return redirect(url_for('home'))

# Delete member
@app.route("/del_member", methods=['POST', 'GET'])
def del_member():
  if request.method == "POST":
    users_id = request.form.getlist("userid")  # 선택된 userid값들을 배열로 가져오기
    db = Database()
    query = "DELETE FROM user WHERE id=%s"
    db.delete_member(query, (users_id))
    db.conn.close()
    flash('회원삭제를 완료했습니다')
    return redirect(url_for('admin'))

# Delete Uploaded image file
@app.route("/del_image", methods=['POST', 'GET'])
def del_image():
  post_id = request.args.get('id')
  filename = request.args.get('img_src')
  comment = request.args.get('comment')
  if post_id:
    img_src ="./static/img/"+filename
    if os.path.exists(img_src):
      os.remove(img_src)
    else:
      flash("The file does not exist")
    db = Database()
    query = "UPDATE post SET img_src='' WHERE id = %s"
    db.execute_db(query, (post_id,))
    db.conn.close()
    return redirect(url_for('post', id=post_id, comment=comment))

# Admin page request
@app.route('/admin')
def admin():
  db = Database() 
  name = request.args.get('name')
  if name:
    query = "SELECT id, name, email FROM user WHERE name = %s"
    rows = db.executeAll(query, (name,))
  else:
    query = "SELECT id, name, email FROM user"
    rows = db.executeAll(query)
  db.conn.close()
  return render_template('admin.html', rows=rows)

# Search request
@app.route('/search', methods=['GET'])
def search():
  name = request.args.get('name')
  if name:
    return redirect(url_for('admin', name=name))
  else:
    flash("검색할 이름을 입력해주세요")
    return redirect(url_for('admin'))


if __name__=='__main__':
# 개발용 웹서버 실행(디버깅모드)
  app.run(host='127.0.0.1', port=5000, debug=True) 
