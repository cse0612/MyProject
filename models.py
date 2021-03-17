import mysql.connector
import sys

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
    print("query >>>>"+query, file=sys.stderr) 
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
    row_count = len(self.executeAll(query, (find_id,))) # return value : row 개수 
    return row_count 

  def execute_db(self, query, args={}):
    '''
    name : SQL Execute
    args : SQL query, args
    '''
    print("query >>>>"+query, file=sys.stderr) 
    self.cursor.execute(query, args)
    self.conn.commit()
    return u'새 포스트 등록되었습니다.'

  def delete_member(self, query, users_id):
    '''
    name : delete SQL method
    args : users id array
    '''
    for id in users_id:
      self.cursor.execute(query, (id,))
      self.conn.commit()
    return u'회원 삭제했습니다.'

  
# if __name__=='__main__': 
# 다른파일에 Module로 import될때는 실행되지 않고 
# 해당파일을 직접 호출했을때만 특정로직을 실행하고 싶을때 사용
if __name__=='__main__':
  db = Database()
  result = db.search_duplicate('root')
  print('result: %d' %result)
