from flask import Flask, request, render_template, jsonify
from urllib.parse import unquote
import requests
import json
import re

app = Flask(__name__)


class foodFunc():
    food_list_json = ''


@app.before_first_request
def food_file_func():
    foodFunc.food_list_json = json.load(open("food.json", 'r'))


def convert_to_float(frac_str):
    try:
        return float(frac_str)
    except ValueError:
        num, denom = frac_str.split('/')
        try:
            leading, num = num.split(' ')
            whole = float(leading)
        except ValueError:
            whole = 0
        frac = float(num) / float(denom)
        return whole - frac if whole < 0 else whole + frac


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


def get_data(items):
    ingridients_dict = []
    for i in items:
        ingridient = {}
        try:
            words = i.split(' ')
            amount = convert_to_float(words[0]) if '/' in words[0] else float(words[0])
            if any(char.isdigit() for char in words[1]):
                amount = amount + convert_to_float(words[1]) if '/' in words[1] else amount * float(words[1])
                desc = words[2].lower()
                name = ' '.join(words[3:]).lower()
            else:
                desc = words[1].lower()
                name = ' '.join(words[2:]).lower()
            
            pattern_match = fuzzyfinder(name)
            fdcid = foodFunc.food_list_json[pattern_match[0]]
            print(z for z in pattern_match[:3])

            ingridient["name"] = name
            ingridient["amount"] = amount
            ingridient["desc"] = desc
            ingridient["fdcid"] = fdcid
            ingridient["error"] = "null"

        except Exception as e:
            ingridient["error"] = "yes"
            ingridient["error_msg"] = str(e)
        
        ingridients_dict.append(ingridient)

    fdcids = ','.join([str(i["fdcid"]) for i in ingridients_dict if i["error"] == "null"])
    return ingridients_dict, fdcids


@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('index.html')


@app.route("/fetch", methods=['GET', 'POST'])
def fetch():
    recipe_name = request.values.get('recipe-name')
    ingridients = request.values.get('ingridients')
    serving = request.values.get('serving')
    size_ = request.values.get('size')
    try:
        items = ingridients.split("\r")
    except:
        items = ingridients
    data_fetched, fdcids = get_data(items)

    results_dict = {}
    results_dict["recipe_name"] = recipe_name
    results_dict["servings"] = serving
    results_dict["serving_size"] = size_
    page = requests.get('https://api.nal.usda.gov/fdc/v1/foods?fdcIds='+fdcids+'&api_key=').json()
    ingridients = []
    nutrients = {}
    
    page_num = 0
    for i in range(len(data_fetched)):
        name = items[i]
        ing = {}
        ing["name_original"] = name
        if data_fetched[i]["error"] == "null":
            ing["nutrients"] = {}
            ing["name_realized"] = page[page_num]["description"]
            amount = data_fetched[i]["amount"]
            ing["amount"] = amount
            ing["desc"] = data_fetched[i]["desc"]
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
            ing["error_msg"] = data_fetched[i]["error_msg"]
        ingridients.append(ing)

    results_dict["ingridients"] = ingridients
    results_dict["nutrients"] = nutrients
    return jsonify(results_dict)


if __name__ == "__main__":
    app.run(debug=True)
