import flask
import codeforces_wrapper
import requests



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
    response = requests.get(PROBLEM_SET_LINK)
    
    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        problem_set = response.json()["result"]["problems"]
        
        # Assuming you have some other data structure to assign to questions
        questions = {"problems": problem_set}

        # Use jsonify to serialize the dictionary as JSON and return it as the response
        return flask.jsonify(questions)
    else:
        # If the request was not successful, return an error message
        return flask.jsonify({"error": "Failed to fetch problem set"}), response.status_code
    

if __name__ == '__main__':
    app.run(debug=True)


