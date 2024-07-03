from flask import Blueprint,jsonify,render_template,request
from database_Mongodb.connection_db import investment_db
from werkzeug.utils import secure_filename
from bson import ObjectId
from pymongo.errors import PyMongoError
import os
import time



# Database 
plan_db = investment_db['plan_list']
party_db = investment_db['party_list']
collection_db = investment_db['collection_list']
monthly_db = investment_db['monthly_list']



#  Create New BluePrint
party_list_bp = Blueprint("party_list_bp",
                          __name__,
                          url_prefix="/",
                          template_folder="templates",
                          static_folder="static")



@party_list_bp.route('/partys', methods=['GET', 'POST'])
def party_data_view():
    
    plan_list = list(plan_db.find())
    
    print("List of plans ::->", plan_list)
    
    return render_template("party_list.html", plans=plan_list)




@party_list_bp.route('/api/party_data', methods=['GET','POST'])
def party_datatable() :
    query = {}
    sort_quiry = {}
    # Searching Product
    print("Search Party ::->",request.form.get('search[value]', ''))
    
    if request.form.get('search[value]', ''):
        query = {"party_name": {"$regex": request.form.get('search[value]', ''), "$options": "i"}}
        
    try:
        if request.form["columns[0][search][value]"] != "":
            query = {"party_name": {'$regex': request.form["columns[0][search][value]"], "$options": "i"}}
    except KeyError:
        pass
    
    try :
        if request.form["columns[1][search][value]"] != "" :
            query['mobile_no'] = {'$regex' : request.form["columns[1][search][value]"], "$options" :"i"}
    except KeyError:
        pass
    
    try :
        if request.form["columns[2][search][value]"] != "" :
            print("Id ::->",request.form["columns[2][search][value]"])
            query = {'collection.objid' : ObjectId(request.form["columns[2][search][value]"])}
    except Exception as e :
        print("Plan Error ::->",e)

    if request.form['order[0][column]'] == '0' : 
        if request.form['order[0][dir]'] == 'asc' :
            sort_quiry = {'party_name' : 1}
        else :
            sort_quiry = {'party_name' : -1}
            
    if request.form['order[0][column]'] == '3' :
        if request.form['order[0][dir]'] == 'asc' :
            sort_quiry = {'collection_amount' : 1}
        else :
            sort_quiry = {'collection_amount' : -1}
    
    if request.form['order[0][column]'] == '4' :
        if request.form['order[0][dir]'] == 'asc' :
            sort_quiry = {'withdraw_amount' : 1}
        else :
            sort_quiry = {'withdraw_amount' : -1}
    
    print("Sort Query is ::->",query)
    
    
    finding = list(party_db.aggregate([
        {'$lookup' : {
            'from' : 'collection_list',
            'let' : {'id' : '$_id'},
            'pipeline' : [{'$match' : {'$expr' : {'$eq' : ['$party_name', '$$id' ]}}},{
                '$lookup' : {
                    'from' : 'plan_list',
                    'localField' : 'plan_name',
                    'foreignField' : '_id',
                    'as' : 'plans'
                }},
                {'$unwind' : '$plans'},
                {'$group' : {'_id' : '$plans.plan_name',
                             'objid': {'$first': '$plans._id'},
                             'amount' : {'$sum' : '$amount'}}}],
            
            'as' : 'collection' }},
        
        {'$lookup' : {
            'from' : 'withdrawal_list',
            'let' : {'id' : '$_id'},
            'pipeline' : [{'$match' : {'$expr' : {'$eq' : ['$party_name', '$$id']}}},{
                '$lookup' : {
                    'from' : 'plan_list',
                    'localField' : 'plan_name',
                    'foreignField' : '_id',
                    'as' : 'plans'
                }},
                {'$unwind' : '$plans'},
                {'$group' : {'_id' : '$plans.plan_name',
                            'amount' : {'$sum' : '$amount'}}}],
            'as' : 'withdraw'}},
        
        {
        '$addFields' : {'collection_amount' : {'$sum' : '$collection.amount'},
                        'withdraw_amount' : {'$sum' : '$withdraw.amount'},
                        'planns' : {'$concatArrays' : ['$collection._id']}
                        }},
        
        {"$sort" : sort_quiry},
        {"$match": query},
        {"$skip" : int(request.form.get('start', 0))},
        {'$limit' : int(request.form.get('length',10))},
    ]))

    # print("Data ::->",finding)
    
    data_dict = []
    for data in finding :
        result = {
            'party_name': data['party_name'],
            'mobile_no': data['mobile_no'],
            'plans': data['planns'],
            'collection_amount': data['collection_amount'],
            'withdraw_amount': data['withdraw_amount'],
            'total_investment' : int(data['collection_amount'] - int(data['withdraw_amount'])),
            'plan_collections': []
        }
        for plan in data['planns']:
            for item in data['collection']:
                if item['_id'] == plan:
                    result['plan_collections'].append({'plan': plan, 'amount': item['amount']})
                
        data_dict.append(result)
    
    # for final in data_dict :
        # print("Final Data is ::->",final)
        
    total_product = party_db.estimated_document_count()
    
    print("Total Product Count is ::->",total_product)
        
    data = {
        "iTotalDisplayRecords" : total_product,
        "aaData" : data_dict,
        "iTotalRecord" : total_product/int(request.form['length'])
    }

    
    from database_Mongodb.connection_db import investment_db

    # DataBase
    plan_db = investment_db['plan_list']
    party_db_demo = investment_db['party_list']
    collection_db = investment_db['collection_list']
    users_db = investment_db['users']
    role_manage_db = investment_db['role_manage']
    withdrowal_db = investment_db['withdrawal_list']



    # finding = party_db_demo.aggregate([
    #     {'$lookup' : {
    #         'from' : 'collection_list',
    #         'let' : {'id' : '$_id'},
    #         'pipeline' : [{'$match' : {'$expr' : {'$eq' : ['$party_name', '$$id']}}}],
    #         'as' : 'user_collection'
    #     }},
    #     {
    #     '$addFields': {
    #         'total_amount': {
    #             '$sum': '$user_collection.amount'
    #         }
    #     }
    # },
    #     # {'$skip': 1},
    #     {'$limit': 10}
    # ])
    
    
    
    # finding = party_db_demo.aggregate([
    #      {
    #     '$lookup': {
    #         'from': 'collection_list',
    #         'let': {'id': '$_id'},
    #         'pipeline': [
    #             {'$match': {'$expr': {'$eq': ['$party_name', '$$id']}}},
    #             {
    #                 '$lookup': {
    #                     'from': 'plan_list',
    #                     'localField': 'plan_name',  # field from collection_list
    #                     'foreignField': '_id',  # field from plan_list
    #                     'as': 'plan_details'
    #                 }
    #             },
    #             {'$unwind': '$plan_details'},  # Unwind to get the plan details as a single object
    #             {
    #                 '$match': {'plan_details.plan_name': 'Silver'}
    #             },
    #         ],
    #         'as': 'user_collection'
    #     }
    # },
    # {'$limit': 5}
    # ])

    
    # finding = withdrowal_db.aggregate([
    #     {'$match' : {"plan_name" : ObjectId('6607daf6c4da87b0c8c3ada1')}}
        
    # ])
    
    finding = withdrowal_db.aggregate([
        {
            '$lookup': {
                'from': "party_list",
                'localField': "party_name",
                'foreignField': "_id",
                'as': "party_details"
            }
        },
        {
            '$lookup' : {
                'from' : "plan_list",
                'localField' : "plan_name",
                'foreignField' : "_id",
                'as' : "Plan_Details"
            }
        },
        {
            '$unwind': "$Plan_Details"  # Unwind the Plan_Details array to filter based on plan_type
        },
        {
            '$match': {
                'Plan_Details.plan_type': 'Fix'  # Add your filter criteria here
            }
        },
        {'$limit' : 5}
    ])

    for find in finding :
        print("Find Data is or ::->",find)
        
    
    return jsonify(data)




