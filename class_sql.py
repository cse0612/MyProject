import mysql.connector

class Database():
  def __init__(self):
    '''
    name : init method
    args : none
    return : none
    '''
  
    dbconfig={'host':'127.0.0.1','user':'root','password':'irf9z34n','database':'MyPythonProject'}
    self.conn=mysql.connector.connect(**dbconfig)
    self.cursor = self.conn.cursor()

  def executeAll(self, query, args={}):
    '''
    name : sql 실행
    args : query, data
    return : rows values
    '''
    self.cursor.execute(query, args)
    rows = self.cursor.fetchall()
    print('query-result:', rows)
    return rows

  def search_duplicate(self, find_id):
    '''
    name : id 체크
    args : id
    return : rows length
    '''
    query = "SELECT * FROM user WHERE id=%s"
    #query = "SELECT * FROM user WHERE id = %(id)s"  # 같은 sql 문법
    #cursor.execute(query, {'id':member_id})           # args : dic datatype
    row_count = len(self.executeAll(query, (find_id,))) # query문 실행
    return row_count 

  def insert_member(self, member_id, member_pw, member_name, member_email):
    '''
    name : insert SQL method
    args : fields values
    return : message, etc
    '''
    query = "INSERT INTO user (id, pw, name, email) VALUES (%s, %s, %s, %s)"
    self.cursor.execute(query, (member_id, member_pw, member_name, member_email))
    self.conn.commit()
    return u'회원가입 완성했습니다. 다시 로그인해주세요'

  def update_member(self, member_id, member_pw, member_name, member_email):
    '''
    name : update SQL method
    args : fields values
    return : message, etc
    '''
    query = "UPDATE user SET pw = %s, name=%s, email=%s WHERE id=%s"
    self.cursor.execute(query, [member_pw, member_name, member_email, member_id])
    self.conn.commit()
    return u'회원 수정했습니다. 다시 로그인해주세요'


  def delete_member(self, member_id):
    '''
    name : delete SQL method
    args : member_id
    return : message, etc
    '''
    query = "DELETE FROM user WHERE id=%s"
    self.cursor.execute(query, (member_id,))
    self.conn.commit()
    return u'회원 삭제했습니다.'


  def insert_post(self, img_src, comment, id_user):
    '''
    name : insert SQL in post table 
    args : id, img_src, comment
    return : message
    '''
    query = "INSERT INTO post (img_src, comment, id_user) VALUES(%s, %s, %s)"
    self.cursor.execute(query, (img_src, comment, id_user))
    self.conn.commit()
    return u'새 포스트 등록되었습니다.'

# if __name__=='__main__': 
# 다른파일에 Module로 import될때는 실행되지 않고 
# 해당파일을 직접 호출했을때만 특정로직을 실행하고 싶을때 사용
if __name__=='__main__':
  db = Database()
  result = db.search_duplicate('root')
  print('result: %d' %result)
