from flask import Flask, request, render_template, jsonify
from urllib.parse import unquote
import requests
import json
import re
import itertools

app = Flask(__name__)


class foodFunc():
    food_list_json = ''


@app.before_first_request
def food_file_func():
    foodFunc.food_list_json = json.load(open("food.json", 'r'))


@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('index.html')

  
"""def badCharHeuristic(string, size): 
    badChar = [-1]*256
    for i in range(size): 
        badChar[ord(string[i])] = i; 
    return badChar 
  

def boyer_search(ing_name):
    suggestion = []
    final = []
    pos = []
    for item in foodFunc.food_list_json.keys():
        m = len(ing_name)
        n = len(item) 
        badChar = badCharHeuristic(ing_name, m)  
        s = 0
        while(s <= n-m): 
            j = m-1
            while j>=0 and ing_name[j] == item[s+j]: 
                j -= 1
            if j<0: 
                suggestion.append(item)
                pos.append(s)
                s += (m-badChar[ord(item[s+m])] if s+m<n else 1) 
            else: 
                s += max(1, j-badChar[ord(item[s+j])])
    for i in range(len(pos)):
        p = pos.index(min(pos))
        pos.pop(p)
        final.append(suggestion[p])
        if i >= 10:
            break
    return final"""


def fuzzyfinder(ing_name):
    suggestions = []
    count = 0
    pattern = '.*?'.join(ing_name)   # Converts 'djm' to 'd.*?j.*?m'
    regex = re.compile(pattern)  # Compiles a regex.
    for item in foodFunc.food_list_json:
        match = regex.search(item.lower())   # Checks if the current item matches the regex.
        if match:
            suggestions.append((len(match.group()), match.start(), item))
        count += 1
    return [x for _, _, x in sorted(suggestions)]


def get_data(items, amounts):
    ingridients_dict = []
    for i in zip(items, amounts):
        ingridient = {}
        try:
            try:
                name_ = i[0]
                fdcid = foodFunc.food_list_json[name_]
            except:
                name_ = boyer_search(i[0])[0]
                fdcid = foodFunc.food_list_json[name_]
            amt_ = int(i[1])            
            ingridient["name"] = name_
            ingridient["amount"] = amt_
            ingridient["fdcid"] = fdcid
            ingridient["error"] = "null"
            print("everything fine")
        except Exception as e:
            ingridient["name"] = i[0]
            ingridient["error"] = "yes"
            print(e)

        ingridients_dict.append(ingridient)

    fdcids = ','.join([str(i["fdcid"]) for i in ingridients_dict if i["error"] == "null"])
    return ingridients_dict, fdcids


@app.route("/fetch", methods=['POST'])
def fetch():
    recipe_name = request.values.get('recipe-name')
    serving = request.values.get('serving')
    size_ = request.values.get('size_')
    ing_amounts = request.form.getlist('amount')[1:]
    ing_name = request.form.getlist('ing-name')[1:]
    data_fetched, fdcids = get_data(ing_name, ing_amounts)

    results_dict = {}
    results_dict["recipe_name"] = recipe_name
    results_dict["servings"] = serving
    results_dict["serving_size"] = size_
    print(fdcids)
    page = requests.get('https://api.nal.usda.gov/fdc/v1/foods?fdcIds='+fdcids+'&api_key=').json()
    ingridients = []
    nutrients = {}
    
    page_num = 0
    proceed = 0
    for i in range(len(data_fetched)):
        name_ = ing_name[i]
        ing = {}
        ing["name_original"] = name_
        if data_fetched[i]["error"] == "null":
            proceed = 1
            ing["nutrients"] = {}
            ing["name_realized"] = page[page_num]["description"]
            amount = data_fetched[i]["amount"]
            ing["amount"] = amount
            for n in page[page_num]["labelNutrients"]:
                value = page[page_num]["labelNutrients"][n]["value"] * amount
                ing["nutrients"][n] = value
                if ing["nutrients"][n] in nutrients:
                    nutrients[n] += value
                else:
                    nutrients[n] = value
            ing["error"] = "null"
            page_num += 1
        else:
            ing["error"] ="yes"
        ingridients.append(ing)
    results_dict["is_valid"] = proceed
    results_dict["ingridients"] = ingridients
    results_dict["nutrients"] = nutrients
    return jsonify(results_dict)
    

@app.route("/match_ing", methods=['GET'])
def match_ing():
    ing_name = request.args.get('ing-name')
    ing_name_sug = fuzzyfinder(ing_name)[:10]
    return jsonify({"results": ing_name_sug})


@app.route("/validate_ing", methods=['GET'])
def validate_ing():
    ing_name = request.args.get('ing-name')
    ing_name = unquote(ing_name)
    try:
        fdcid = foodFunc.food_list_json[ing_name]
        return jsonify({"is_valid": 1, "fdcid": fdcid})
    except Exception as e:
        return jsonify({"is_valid": 0})


if __name__ == "__main__":
    app.run(debug=True)
