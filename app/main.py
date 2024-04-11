import flask
import codeforces_wrapper
import requests
from pymongo.mongo_client import MongoClient
from pymongo.errors import ConnectionFailure
from pymongo.server_api import ServerApi
import os
from dotenv import load_dotenv

load_dotenv()
MONGO_DB_URL = os.getenv("MONGO_DB_URL")

app = flask.Flask(__name__)
PROBLEM_LINK = 'https://codeforces.com/problemset/problem/'
PROBLEM_SET_LINK = 'https://codeforces.com/api/problemset.problems'








@app.route('/getquestion', methods=['GET'])
def home():
    problem_id = flask.request.args['id']
    problem_code = flask.request.args['problem']
    print(f'{PROBLEM_LINK}{problem_id}/{problem_code}')
    problem = codeforces_wrapper.parse_problem(f'{PROBLEM_LINK}{problem_id}/{problem_code} ')
    return flask.jsonify(problem)


@app.route('/getproblemset',methods=['GET'])
def problems():

    try:
        client = MongoClient(MONGO_DB_URL)
        db = client.get_database("Problems")

        collection = db.Problems
        
        response = requests.get(PROBLEM_SET_LINK)
        
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            problem_set = response.json()["result"]
            problem_statistics = problem_set["problemStatistics"]
            problem_details = problem_set["problems"]

            for i in range(0,len(problem_statistics)):
                if problem_statistics[i]["solvedCount"] > 10000:
                    difficulty = "easy"
                elif problem_statistics[i]["solvedCount"] < 5000:
                    difficulty = "hard"
                else:
                    difficulty = "medium"

                problem_id = str(problem_details[i]["contestId"]) + problem_details[i]["index"]

                problem = {"problem_id":problem_id,"tags":problem_details[i]["tags"],"difficulty":difficulty}

                present = collection.find_one(problem)
                if(present):
                    break
                else:
                    collection.insert_one(problem)
            
            # Assuming you have some other data structure to assign to questions
            questions = {"problems": problem_set}
            
            # Use jsonify to serialize the dictionary as JSON and return it as the response
            return flask.jsonify(questions)
        else:
            # If the request was not successful, return an error message
            return flask.jsonify({"error": "Failed to fetch problem set"}), response.status_code
    
    except ConnectionFailure as e:
        print("Failed to connect to MongoDB:", e)
    except Exception as e:
        print("An error occurred:", e)

@app.route('/activateuser', methods=['POST'])
def activate_user():

    data = flask.request.json   # Assuming data is sent as JSON
    number = data['number']
    difficulty = data['difficulty']

    try:
        client = MongoClient(MONGO_DB_URL)
        db = client.get_database("Problems")

        collection = db.Users

        user = {"mobile_number":number,"difficulty":difficulty,"questions_attempted":[],"status":"active"}
        present = collection.find_one({"mobile_number":number})

        if present:
            if(present["status"]=="inactive"):
                document_id = present["_id"]
                query = {'_id':document_id}
                update = {'$set':{'status':'active'}}
                collection.update_one(query, update)

                return flask.jsonify({"message":"User activated"})
            
            else:
                return flask.jsonify({"message":"User already exist and active"})
        
        else:
            collection.insert_one(user)
            return flask.jsonify({"message":"User added"})

    except ConnectionFailure as e:
        print("Failed to connect to MongoDB:", e)
    
    except Exception as e:
        print("An error occurred:", e)


@app.route('/deactivateuser', methods=['POST'])
def deactivate_user():
    data = flask.request.json   # Assuming data is sent as JSON
    number = data['number']

    try:
        client = MongoClient(MONGO_DB_URL)
        db = client.get_database("Problems")
        collection = db.Users

        user = {"mobile_number":number}
        present = collection.find_one(user)

        if present:
            if(present["status"]=="inactive"):
                return flask.jsonify({"message":"User already deactivated"})
            
            else:
                document_id = present["_id"]
                query = {'_id':document_id}
                update = {'$set':{'status':'inactive'}}
                collection.update_one(query, update)

                return flask.jsonify({"message":"User deactivated"})
        
        else:
            return flask.jsonify({"message":"User not found"})

    except ConnectionFailure as e:
        print("Failed to connect to MongoDB:", e)
    
    except Exception as e:
        print("An error occurred:", e)




if __name__ == '__main__':
    app.run(debug=True)


