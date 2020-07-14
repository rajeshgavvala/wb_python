from flask import Flask
from flask import jsonify
from flask import request
from flask_pymongo import PyMongo 
from flask.templating import render_template

import string
import random
import secrets
from datetime import datetime
from dateutil.relativedelta import relativedelta


app = Flask(__name__)

# Database
app.config['MONGO_DBNAME'] = 'user_products'
app.config['MONGO_URI'] = 'mongodb://localhost:28018/user_products'
mongo = PyMongo(app)

# Documents
_issue = mongo.db.issues
_product = mongo.db.productUser
_feedback = mongo.db.productFeedback
_warranty = mongo.db.productWarranty
_addProduct = mongo.db.addProductByAdmin 

# Global Variables
timeNow = datetime.today()



#----------------------------------------------#
# WelCome Message
#----------------------------------------------#
@app.route('/')
def welcome_message():
    message = {
        'wb_digi_app': 'v1.0',
        'status': '200',
        'message': 'Welcome to the wb Digital Application'
    }
    # Making the message looks good
    resp = jsonify(message)
    # Returning the object
    return resp

#----------------------------------------------#
# Register ProductUser by Admin
#----------------------------------------------#
@app.route('/admin/productUser/insert', methods=['POST','GET'])
def product_user_register():
    if request.method == 'POST':
        existing_userEmail = _product.find_one({'_id' : request.form['productUserEmail']})
        existing_userMobile = _product.find_one({'productUserMobile' : request.form['productUserMobile']})
        productCode = request.form['productCode']
        pType = "".join(productCode[0:2]+productCode[-2:])

        existing_productType = _warranty.find_one({'_id' : pType})
        warranty = datetime.today()+relativedelta(months=int(existing_productType['productTypeWarranty']))
        warranty_till = warranty.strftime("%Y-%m-%d")
                
        if((existing_userEmail==None) and (existing_userMobile == None)):
            _product.insert({'_id' : request.form['productUserEmail'],
            'productUserMobile' : request.form['productUserMobile'],
            'myProducts' : [{
                'pType': pType,
                'productCode':productCode,
                'purchasedOn':timeNow.strftime("%Y-%m-%d"),
                'warrantTill':warranty_till}]})
            return 'product user added sucessfully'
        elif(existing_userEmail!=None):
            existsEmail = _product.find({'_id': request.form['productUserEmail']})
            _product.update({'_id': request.form['productUserEmail']},
            {"$addToSet": { "myProducts": 
            {'pType': pType,
            'productCode':productCode,
            'purchasedOn':timeNow.strftime("%Y-%m-%d"),
            'warrantTill':warranty_till}}})

            return 'product added sucessfully'
        else:
            return 'problem to add the product/user!'
                    
    return render_template('register.html')


#----------------------------------------------#
# Warranty by Admin
#----------------------------------------------#
@app.route('/admin/typeWarranty/insert', methods=['POST','GET'])
def product_type_warranty():
    if request.method == 'POST':
        existing_productType = _warranty.find_one({'_id' : request.form['productType']})
        existing_productTypeWarranty = _warranty.find_one({'productTypeWarranty' : request.form['productTypeWarranty']})
    
        if((existing_productType==None)):
            _warranty.insert({'_id' : request.form['productType'],
            'productTypeWarranty' : request.form['productTypeWarranty']})
            return 'productType/warranty! added sucessfully'

        elif(existing_productType!=None):
            existsproductType = _warranty.find({'_id': request.form['productType']})
            _warranty.update({'_id': request.form['productType']},
            {"$set": {'productTypeWarranty':request.form['productTypeWarranty']}})
            return 'productType warranty added sucessfully'
        else:
            return 'problem to add the productType/warranty!'
                    
    return render_template('warranty.html')

#----------------------------------------------#
# product activate by admin
#----------------------------------------------#
@app.route('/admin/product/purchase', methods=['POST','GET'])
def product_admin_add():
    if request.method == 'POST':
        existing_productType = _addProduct.find_one({'_id' : request.form['productCode']})
        existing_productTypeWarranty = _addProduct.find_one({'purchasedOn' : request.form['purchasedOn']})
    
        if((existing_productType==None)):
            _addProduct.insert({'_id' : request.form['productCode'],
            'purchasedOn' : request.form['purchasedOn']})
            return 'productCode added sucessfully'

        elif(existing_productType!=None):
            existsproductType = _addProduct.find({'_id': request.form['productCode']})
            _addProduct.update({'_id': request.form['productCode']},
            {"$set": {'purchasedOn':request.form['purchasedOn']}})
            return 'productUpdated sucessfully'
        else:
            return 'problem to add the productCode'
                    
    return render_template('addProduct.html')

#----------------------------------------------#
# user product added
#----------------------------------------------#
@app.route('/user/product/add', methods=['POST'])
def add_product_user():
  output = []
  existing_productCode = _addProduct.find_one({'_id' : request.form['id']})

  
  return jsonify({'issues' : output})


#----------------------------------------------#
# Get all listed issues
#----------------------------------------------#
@app.route('/user/issue/listIssues', methods=['POST','GET'])
def get_all_userIssues():
  output = []

  if request.method == 'POST':
        email = request.json['id']
        print(email)
        exits_email = _issue.find_one({'_id':email})
        print(exits_email)

        if(exits_email!=None):
            output.append(exits_email['issues'])
            '''
            for s in _issue.find():
                output.append({'issueId' : s['issueId'], 
                'date' : s['date'],
                'location' : s['location'],
                'image' : s['image'],
                'description' : s['description']
                })
            '''

  
  return jsonify({'issues' : output})


#----------------------------------------------#
# Get list of all user orders
#----------------------------------------------#
@app.route('/user/order/getOrders', methods=['POST','GET'])
def get_all_userOrders():
    output = []
    if request.method == 'POST':
        email_id = request.json['id']
        print(email_id)
        exits_emailId = _product.find_one({'_id':email_id})
        

        if(exits_emailId!=None):
            output.append(exits_emailId['myProducts'])
        #print(output[0])

    return jsonify({'orders' : output[0]})

    

#----------------------------------------------#
# Insert user feedback
#----------------------------------------------#
@app.route('/user/feedback/insert', methods=['POST'])
def insert_feedback():
    if request.method == 'POST':
        pType = request.json['pType']
        rate = request.json['rate']
        review = request.json['review']

        #print(pType,rate,review)

        exists_pType = _feedback.find_one({'_id':pType})
        #print(exists_pType)

        if(exists_pType==None):
            insertFeedback=_feedback.insert({'_id' : pType,'rate_review' : [{'rate': rate,'review':review}]})
            return jsonify({'result' : 'feed created sucessfully'})
        elif(exists_pType!=None):
            updateFeedback =_feedback.update({'_id': pType},
                {"$addToSet": { "rate_review": {'rate': rate,'review':review}}})
            return jsonify({'result' : 'feed added sucessfully'})

    return jsonify({'result' : 'feedback added sucessfully'})


#----------------------------------------------#
# Insert Issue
#----------------------------------------------#
@app.route('/user/issue/insert', methods=['POST'])
def insert_issue():
    if request.method == 'POST':
        userId=request.json['userId']
        productId=request.json['productId']
        issueId=request.json['issueId']
        date=request.json['date']
        location= request.json['location']
        image=request.json['image']
        description= request.json['description']

        exists_productId = _issue.find_one({'_id':userId})
        print(exists_productId)
        print(userId)

        if(exists_productId==None):
            insertIssue= _issue.insert({
            '_id' : userId,
            'issues' : [{'issueId':issueId,'productId':productId,
                'date': date,
                'location': location,
                'image': image,
                'description': description}]})
            return jsonify({'result' : 'issue created sucessfully'})
        
        elif(exists_productId!=None):
            updateIssue= _issue.update({'_id': userId},
                {"$addToSet": { "issues": {
                    'issueId':issueId,
                    'productId':productId,
                    'date': date,
                    'location': location,
                    'image': image,
                    'description': description}}})
           
            return jsonify({'result' : 'issue updated sucessfully'})
        
    return jsonify({'result' : 'isuue added sucessfully'})


#----------------------------------------------#
# Activate warranty by retailer
#----------------------------------------------#
@app.route('/retailer/warranty/activate', methods=['POST'])
def activate_warranty():
    if request.method == 'POST':
        email = request.json['email']
        mobilNumber    = request.json['mobile']
        productCode = request.json['productCode']
        purchasedOn = request.json['purchasedOn']

        exits_productCode = _product.find_one({'myProducts.productCode':{'$eq':productCode}})
        
        pType = "".join(productCode[0:2]+productCode[-2:])
        existing_productType = _warranty.find_one({'_id' : pType})
        warranty = datetime.today()+relativedelta(months=int(existing_productType['productTypeWarranty']))
        warranty_till = warranty.strftime("%Y-%m-%d")

        if(exits_productCode==None):
            existing_userEmail = _product.find_one({'_id' : email})
            existing_userMobile = _product.find_one({'_id' : mobilNumber})
            

            if((existing_userEmail==None) and (existing_userMobile==None)):
                activateWarranty = _product.insert({
                '_id':email,
                'productUserMobile':mobilNumber,
                'myProducts' : [{
                        'pType':pType,
                        'productCode' : productCode,
                        'purchasedOn' : purchasedOn,
                        'warrantTill' : warranty_till}]})
                return jsonify({'result' : 'product added sucessfully'})

            elif(existing_userEmail!=None):
                existsEmail = _product.find({'_id': email})
                _product.update({'_id': email},
                {"$addToSet": { "myProducts": {
                    'pType':pType,
                    'productCode': productCode,
                    'purchasedOn':purchasedOn,
                    'warrantTill' : warranty_till}}})
                return jsonify({'result' : 'product added sucessfully'})
            else:
                return jsonify({'result' : 'problem to activate product warranty!'})
        else:
            return jsonify({'result' : 'productCode already exists!'})
                


if __name__ == '__main__':
    #app.run(debug=True, host='0.0.0.0')
    from waitress import serve
    serve(app, host="0.0.0.0", port=5000)













'''

    product_find = _product.find_one({'_id': activateWarranty })

    output = {'email' : product_find['_id'],
    'mobilNumber' : product_find['mobile'],
    'myProducts' : [{
                'pId':product_find['pId'],
                'productCode' : product_find['productCode'],
                'purchasedOn' : product_find['purchasedOn']}]}

    return jsonify({'result' : output})
'''