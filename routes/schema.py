import sys
sys.path.append('../')
from tornado.web import RequestHandler
from bson import ObjectId
import json 
from function import *
from controller import schemaController
from controller import schemaDataController
from datetime import datetime

groups = []

#PRIMARY VARIABLE - DONT DELETE
define_url = [
    ['add/','add'],
    ['','list'],
    ['count/','count'],
    ['detail/','detail'],
    ['edit/','update'],
    ['delete/','delete']
]

class add(RequestHandler):
  def post(self):    
    data = json.loads(self.request.body)
    print(data)
    sys.stdout.flush()
    if 'schema_code' not in data:
        data['schema_code'] = generateCode();

    insert = schemaController.add(data)    
    if not insert['status']:
        response = {"status":False, "message":"Failed to add", 'data':json.loads(self.request.body)}               
    else:
        response = {'message':'Success','status':True}    
    self.write(response)

class list(RequestHandler):
  def post(self):    
    data = json.loads(self.request.body)
    if 'name' in data:
        data['name'] = {"$regex": data['name']}
    if 'detail' in data:
        data['information.detail'] = {"$regex": data['detail']}
        del data['detail']
    if 'purpose' in data:
        data['information.purpose'] = {"$regex": data['purpose']}
        del data['purpose']
    query = data    
    result = schemaController.find(query)
    if not result['status']:
        response = {"status":False, "message":"Data Not Found",'data':json.loads(self.request.body)}               
    else:
        response = {"status":True, 'message':'Success','data':result['data']}
    self.write(response)

class count(RequestHandler):
  def post(self):    
    data = json.loads(self.request.body)
    if 'name' in data:
        data['name'] = {"$regex": data['name']}
    if 'detail' in data:
        data['information.detail'] = {"$regex": data['detail']}
        del data['detail']
    if 'purpose' in data:
        data['information.purpose'] = {"$regex": data['purpose']}
        del data['purpose']
    query = data
    if "id" in query :
        try:
            query["_id"] = ObjectId(query["id"])
            del query["id"]
        except:
            del query["id"]
    query = data
    result = schemaController.find(query)
    if not result['status']:
        response = {"status":False, "message":"Data Not Found",'data':0}               
    else:
        response = {"status":True, 'message':'Success','data':len(result['data'])}
    self.write(response)

class detail(RequestHandler):
  def post(self):    
    data = json.loads(self.request.body)
    query = data
    result = schemaController.findOne(query)    
    if not result['status']:
        response = {"status":False, "message":"Data Not Found",'data':json.loads(self.request.body)}               
    else:
        response = {"status":True, 'message':'Success','data':result['data']}
    self.write(response)

class update(RequestHandler):
  def post(self):        
    data = json.loads(self.request.body)
    if 'id' not in data:
        response = {"status":False, "message":"Id Not Found",'data':json.loads(self.request.body)}               
        self.write(response)
        return

    try:
        query = {"_id":ObjectId(data["id"])}
    except:
        response = {"status":False, "message":"Wrong id",'data':json.loads(self.request.body)}               
        self.write(response) 
        return

    if 'schema_code' in data:
        if checkSchemaCode(data['schema_code'],query['_id']):
            response = {"status":False, "message":"Schema Code is exits",'data':json.loads(self.request.body)} 
            self.write(response)
            return

    result = schemaController.findOne(query)
    if not result['status']:
        response = {"status":False, "message":"Data Not Found",'data':json.loads(self.request.body)}               
    else:
        update = schemaController.update(query,data)
        if not update['status']:
            response = {"status":False, "message":"Failed to update","data":json.loads(self.request.body)}
        else:
            response = {"status":True, 'message':'Update Success'}
    self.write(response)

class delete(RequestHandler):
  def post(self):        
    data = json.loads(self.request.body)
    if 'id' not in data:
        response = {"status":False, "message":"Id Not Found",'data':json.loads(self.request.body)}               
        self.write(response)
        return

    try:
        query = {"_id":ObjectId(data["id"])}
    except:
        response = {"status":False, "message":"Wrong id",'data':json.loads(self.request.body)}               
        self.write(response) 
        return
    
    result = schemaController.findOne(query)
    if not result['status']:
        response = {"status":False, "message":"Data Not Found",'data':json.loads(self.request.body)}            
    else:
        delete = schemaController.delete(query)
        if not delete['status']:
            response = {"status":False, "message":"Failed to delete","data":json.loads(self.request.body)}
        else:
            response = {"status":True, 'message':'Delete Success'}
    self.write(response)

class getdata(RequestHandler):
  def post(self,code):    
    data = json.loads(self.request.body)
    print(data)
    response = ""
    query = {"schema_code":code}
    schemaData = schemaController.findOne(query)
    if not schemaData['status']:
        response = {"status":False, "message":"Device Not Found",'data':json.loads(self.request.body)}               
    else:
        schemaData = schemaData['data']
        collection = 'schema_data_'+schemaData['schema_code']
        
        if response == "":
            limit =  None
            skip = None
            sort = ('date_add_auto',-1)
            if 'limit' in data:
                limit = data['limit']
                del data['limit']
                if 'page_number' in data:
                    page_num = data['page_number']
                    del data['page_number']
                else:
                    page_num = 1
                skip = limit * (page_num - 1)
            if 'skip' in data:
                skip = data['skip']
                del data['skip']
            if 'sort' in data:
                sort = (data['sort']['field'],data['sort']['type'])            
            if 'date' in data:
                date_time_str = str(data['date'])
                datesrc_str = datetime.strptime(date_time_str+" 00:00",'%Y-%m-%d %H:%M')
                datesrc_end = datetime.strptime(date_time_str+" 23:59",'%Y-%m-%d %H:%M')
                data['date_add_auto'] = {"$gte":datesrc_str, "$lt":datesrc_end }
                del data['date']
            if 'date_start' in data and 'date_end' in data:
                date_time_str = str(data['date_start'])
                date_time_end = str(data['date_end'])
                datesrc_str = datetime.strptime(date_time_str+" 00:00",'%Y-%m-%d %H:%M')
                datesrc_end = datetime.strptime(date_time_end+" 23:59",'%Y-%m-%d %H:%M')
                data['date_add_auto'] = {"$gte":datesrc_str, "$lt":datesrc_end }
                del data['date_start']
                del data['date_end']
            query = data
            query["schema_code"] = device
            exclude = {'raw_message':0}
            print(query)
            result = schemaDataController.find(collection,query,exclude,limit,skip,sort)
            if not result['status']:
                response = {"status":False, "message":"Data Not Found",'data':json.loads(self.request.body)}               
            else:
                response = {"status":True, 'message':'Success','data':result['data']}
    self.write(response)

class countdata(RequestHandler):
  def post(self,device):    
    data = json.loads(self.request.body)
    print(data)
    response = ""
    query = {"schema_code":code}
    schemaData = schemaController.findOne(query)
    if not schemaData['status']:
        response = {"status":False, "message":"Device Not Found",'data':json.loads(self.request.body)}               
    else:
        schemaData = schemaData['data']
        collection = 'schema_data_'+schemaData['schema_code']
        
        if response == "":
            limit =  None
            skip = None
            sort = ('date_add_auto',-1)
            if 'limit' in data:
                limit = data['limit']
                del data['limit']
                if 'page_number' in data:
                    page_num = data['page_number']
                    del data['page_number']
                else:
                    page_num = 1
                skip = limit * (page_num - 1)
            if 'skip' in data:
                skip = data['skip']
                del data['skip']
            if 'sort' in data:
                sort = (data['sort']['field'],data['sort']['type'])            
            if 'date' in data:
                date_time_str = str(data['date'])
                datesrc_str = datetime.strptime(date_time_str+" 00:00",'%Y-%m-%d %H:%M')
                datesrc_end = datetime.strptime(date_time_str+" 23:59",'%Y-%m-%d %H:%M')
                data['date_add_auto'] = {"$gte":datesrc_str, "$lt":datesrc_end }
                del data['date']
            if 'date_start' in data and 'date_end' in data:
                date_time_str = str(data['date_start'])
                date_time_end = str(data['date_end'])
                datesrc_str = datetime.strptime(date_time_str+" 00:00",'%Y-%m-%d %H:%M')
                datesrc_end = datetime.strptime(date_time_end+" 23:59",'%Y-%m-%d %H:%M')
                data['date_add_auto'] = {"$gte":datesrc_str, "$lt":datesrc_end }
                del data['date_start']
                del data['date_end']
            query = data
            query["schema_code"] = device
            exclude = {'raw_message':0}
            print(query)
            result = schemaDataController.find(collection,query,exclude,limit,skip,sort)
            if not result['status']:
                response = {"status":False, "message":"Data Not Found",'data':json.loads(self.request.body)}               
            else:
                response = {"status":True, 'message':'Success','data':len(result['data'])}
    self.write(response)

def generateCode(code=""):
    if code == "":
        code = cloud9Lib.randomStringLower(6)
    else:
        code = code+"-"+cloud9Lib.randomStringLower(6)
    #check if exist
    query = {"schema_code":code}
    result = schemaController.findOne(query)
    if result['status']:
        return generateCode(code)
    else:
        return code

def checkSchemaCode(code,execpt=""):
    if execpt:
        query = {"schema_code":code,"_id":{ '$ne' : execpt } }
        result = schemaController.findOne(query)
    else:
        query = {"schema_code":code}
        result = schemaController.findOne(query)
    print(result)
    if result['status']:
        return True
    else:
        return False