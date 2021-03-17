# render_template은 flask가 사이트의 내용을 HTML기반으로 표현하기 위해 사용된다
# post로 입력된 데이터를 실제 사용하기 위해서는 request를 사용한다
from flask import Flask, session, flash, render_template, url_for, request, redirect
import mysql.connector
from datetime import date
from class_sql import Database  # class_sql.py

# Flask 인스턴스 생성
app = Flask(__name__) 
app.secret_key = b'1234asdfasfd'  #message Flash, Session 기능을 사용하기 위해서는 SECRET_KEY를 반드시 설정

@app.route('/')          # Home 
def home(): 
  if session['id']:
    db = Database()
    query = "SELECT id, img_src, comment, id_user From post WHERE id_user=%s"
    sql_rows = db.executeAll(query, (session['id'],))
    return render_template('index.html', id=session['id'], data=sql_rows)
  else:
    return render_template("index.html")

@app.route("/home")
def index():
  if session['id']:
    db = Database()
    query = "SELECT id, img_src, comment, id_user From post WHERE id_user=%s"
    sql_rows = db.executeAll(query, (session['id'],))
    return render_template('index.html', id=session['id'], data=sql_rows)
  else:
    return render_template("index.html")


@app.route('/post')      # Post Page
def post(): 
  return render_template('post.html')

# 포스트 & 파일 업로드 처리
@app.route('/upload_post', methods = ['GET', 'POST'])
def upload_post():
  if request.method == 'POST':
    comment = request.form['comment']
    f = request.files['imgfile']
    img_src = f.filename
    f.save('./static/img/' + f.filename) #저장할 경로 + 파일명
    #f.save('./uploads/' + secure_filename(f.filename))
    # db에 저장
    db = Database()
    db.insert_post(img_src, comment, session['id'])
    query = "SELECT id, img_src, comment, id_user From post WHERE id_user=%s"
    sql_rows = db.executeAll(query, (session['id'],))
    db.conn.disconnect()
    flash('포스트등록되었습니다')
    return render_template('index.html', id=session['id'], data=sql_rows)
	#else:
		#return render_template('page_not_found.html')

# 로그인 화면
@app.route('/login')
def login():
  return render_template('login.html')

# 로그인 체크 처리
@app.route('/check_login', methods=['POST'])  # 메소드로 POST 사용
def check_login():
  if request.method == 'POST':
    member_id = request.form['id']
    member_pw = request.form['pw']

    # 입력유무 체크
    if len(member_id) ==  0 or len(member_pw) == 0:
      error_msg = u'아이디와 비밀번호를 다시 입력해주세요!'
      return error_msg
    
    # db 인스턴스 생성 :  pymysql > Database() Class
    db = Database()
    query = "SELECT id, pw, name FROM user WHERE id = %s and pw = %s"
    # method in class_sql.py - executeAll(query, args) 
    rows= db.executeAll(query, (member_id, member_pw))
    for cols in rows:
      member_id = cols[0]
      member_name = cols[2]

    if len(rows) ==  0:
      flash('아이디와 비밀번호가 틀렸습니다!')
      return render_template("login.html")
    else:
      query = "SELECT id, img_src, comment, id_user From post WHERE id_user=%s"
      sql_rows = db.executeAll(query, (member_id,))
      session['id'] = member_id       # session에 저장
      session['name'] = member_name
      return render_template('index.html', id=member_id, data=sql_rows)
    db.conn.disconnect()
    

@app.route('/logout')      # 로그아웃기능
def logout(): 
  session.pop('id', None)   # Session id값=빈값 넣어주면 됨
  flash('로그아웃되었습니다')
  return render_template('index.html')

    
# 회원가입 및 수정 페이지 렌더링
# ****** 디버깅체크사항 - id값 확인해보기, 메소드 처리 확인
@app.route('/member', methods=['POST', 'GET'])
def member():
  return_id = request.args.get("id")
  if return_id:   # 수정ID가 있으면 수정페이지로 이동
    db = Database() # db 인스턴스 생성
    query = "SELECT * FROM user WHERE id = %s"
    rows = db.executeAll(query, (return_id,))
    db.conn.disconnect()
    return render_template('up_member.html', rows=rows)
  else: # 없으면 등록페이지로 이동
    return render_template('member.html')

# 회원가입 및 수정 처리
@app.route('/update_member', methods=['POST', 'GET'])
def update_member():
  if request.method == 'POST':
    member_id = request.form['id']
    member_pw = request.form['pw']
    member_name = request.form['name']
    member_email = request.form['email']
    # member_date = date.today()  # 오늘날짜 in <from datetime import date>
    # print(f"member_id:{member_id}")
    db = Database()
    if request.form['status'] != "":  # 수정
      db.update_member(member_id, member_pw, member_name, member_email)
      query = "SELECT id, img_src, comment, id_user From post WHERE id_user=%s"
      sql_rows = db.executeAll(query, (member_id,))
      flash('회원 수정이 완료되었습니다.')
      return render_template('index.html', id=member_id, data=sql_rows)
    else: # 신규
      row_count = db.search_duplicate(member_id) # id로 조회
      if row_count >= 1: # DB에 같은 값이 존재할경우
        flash('중복된 아이디가 존재합니다')
        return render_template("member.html")
      else:
        db.insert_member(member_id, member_pw, member_name, member_email)
        flash('회원등록을 완료했습니다')
        return render_template("index.html")
    db.conn.disconnect()

# 회원삭제
@app.route("/del_member")
def del_member():
  '''
  name:member_delete
  args:id
  '''
  member_id = request.args.get("id")
  db = Database()
  db.delete_member(member_id)
  flash('회원탈퇴를 완료했습니다')
  session.pop('id', None)   
  return render_template('index.html')

@app.route("/member_list")
def member_list():
  '''
  name:member_list
  args:id
  '''
  member_id = request.args.get("id")
  db = Database()
  query = "SELECT * FROM user where id=%s"
  rows = db.executeAll(query, (member_id,))
  return render_template('mem_list.html', name=session['name'], rows=rows)

# 비번링크
@app.route("/find_password")
def find_password():
  return render_template('find_password.html')

# 비번조회
@app.route("/find_member")
def find_member():
  
  member_id = request.args.get("id")
  member_name = request.args.get("name")
  
  db = Database() 
  query = "SELECT * FROM user WHERE id=%s and name=%s"
  rows= db.executeAll(query, (member_id,member_name))
  db.conn.disconnect()
  if rows:
    for cols in rows:
      id = cols[0]
      pwd = cols[1]
    
    return render_template('find_password.html', id=id, pw=pwd)
  else:
    flash('정보가 일치하지 않습니다 다시 조회하세요')
    return render_template('find_password.html')

if __name__=='__main__':
# 개발용 웹서버 실행(디버깅모드)
  app.run(host='127.0.0.1', port=5000, debug=True)  

