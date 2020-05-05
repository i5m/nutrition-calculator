const form_box = document.getElementById("form-box");
const ing_box = document.getElementById("ing-box");
const output_box = document.getElementById("output-box");
const results_box = document.getElementById("results-box");
const serving = document.getElementById("serving");
const cps_text = document.getElementById("cal-per-serv-text");
const loader_box = document.getElementById("loader-box");

const ing_box_root = ing_box.firstChild;

var form_ = document.getElementById("recipe-form");
var i, data_;

var xhttp = new XMLHttpRequest();

var typingTimer;
const doneTypingInterval = 2000;
const ing_name_char_size_error_text = "Type atleast 3 letters & less than 50 :(";
const common_error_text = "Error occured, try again or refresh!";
const ing_name_not_found_error_text = "No ingridients found, try again.";

if(screen.width < 700) { document.getElementById("bg-box").classList.remove("row"); }


function fill_serving_amount_func() {
    var serving_str = '';
    for(i = 1; i <= 20; i++) {
        serving_str += '<option value="'+i+'">'+i+' Serving</option>';
    }
    serving.innerHTML = serving_str;
}


function handle_form_func() {
    loader_box.classList.remove("none-box");
    formData = new FormData(form_);
    var xhttp_form_handle = new XMLHttpRequest();
    xhttp_form_handle.onreadystatechange = function() {
        console.log(this.readyState + " - &&& - " + this.status);
        if (this.readyState == 4 && this.status == 200) {
            loader_box.classList.add("none-box");
            output_box.classList.remove("none-box");
            data_ = JSON.parse(this.responseText);
            if(data_["is_valid"] == 1) {
                cal_per_serv = parseInt(data_["nutrients"]["calories"] / data_["servings"]);
                if (data_["recipe_name"] != "") {
                    cps_text.innerHTML = data_["recipe_name"] + " has " + cal_per_serv;
                } else {
                    cps_text.innerHTML = "this recipe has " + cal_per_serv;
                }
                ing_data = data_["ingridients"];
                console.log(ing_data.length);
                for(i = 0; i < ing_data.length; i++) {
                    var ing_vld = ing_box.getElementsByClassName("ing-validator")[i+1];
                    console.log(ing_data.length + ' &&& ' + ing_data[i]["error"]);
                    if(ing_data[i]["error"] == "null") {
                        var cal = parseInt(ing_data[i]["nutrients"]["calories"] / data_["servings"]);
                        var name_realised = ing_data[i]["name_realized"];
                        ing_vld.innerHTML = '<p>' + name_realised + ' | <span class="success-color">' + cal + '</span></p>';
                    } else {
                        ing_vld.innerHTML = '<p><span class="danger-color">' + ing_name_not_found_error_text + '</span></p>';
                    }
                }
                
                str_ = '';
                str_ += '<h4 class="bold-text m-4">Nutrition Facts</h4>';
                str_ += '<p><span class="bold-text">Servings: </span> ' + data_["servings"] + '</p>';
                if(data_["serving_size"] != "") {
                    str_ += '<p><span class="bold-text">Serving Size: </span> ' + data_["serving_size"] + '</p>';
                }
                str_ += '<div class="hori-line m-8"></div>';
                str_ += '<h4 class="bold-text">Calories: &nbsp; ' + cal_per_serv + '</h4>';
                str_ += '<table style="width: 95%;" class="bold-text sec-border m-8 p-8">';
                for(i in data_["nutrients"]) {
                    str_ += '<tr class="p-8"><td>' + i + '</td><td>' + data_["nutrients"][i] + '</td></tr>';
                }
                str_ += '</table>';
                results_box.innerHTML = str_;
                results_box.classList.remove("none-box");

            } else {
                results_box.innerHTML = '<p class="danger-color">'+ing_name_not_found_error_text+'</p>';
            }
        } /*else {
            loader_box.classList.add("none-box");
            output_box.classList.remove("none-box");
            results_box.innerHTML = '<p class="danger-color">'+common_error_text+'</p>';
        }*/
    };
    xhttp_form_handle.open("POST", "/fetch", true);
    xhttp_form_handle.send(formData);
}


function match_ing_func(node_) {
    clearTimeout(typingTimer);
    var ing_vld = node_.parentNode.getElementsByClassName("ing-validator")[0];
    var sug_box = node_.parentNode.getElementsByClassName("ing-sug-box")[0];
    if (node_.value.length >= 3 && node_.value.length <= 100) {
        ing_vld.innerHTML = '';
        typingTimer = setTimeout(function() {
            sug_box.classList.remove("none-box");
            xhttp.onreadystatechange = function() {
                if (this.readyState == 4 && this.status == 200) {
                    res_json = JSON.parse(this.responseText);
                    if(res_json["results"].length > 0) {
                        var str_ = '';
                        for(i in res_json["results"]) {
                            str_ += '<p class="p-4 pointer" onclick="select_ing_name_func(this)">'+res_json["results"][i]+'</p>';
                            str_ += '<div class="m-4 hori-line-thin"></div>'
                        }
                        sug_box.innerHTML = str_;
                    } else {
                        sug_box.innerHTML = '<p class="p-4">'+ing_name_not_found_error_text+'</p>';
                    }
                }/* else {
                    sug_box.innerHTML = '<p class="p-4">'+common_error_text+'</p>';
                }*/
            };
            xhttp.open("GET", "/match_ing?ing-name=" + node_.value.toLowerCase(), true);
            xhttp.send();
        }, doneTypingInterval);
    } else {
        ing_vld.innerHTML = '<p class="warning-color">'+ing_name_char_size_error_text+'</p>';
    }
}


function select_ing_name_func(node_) {
    var sug_box = node_.parentNode.parentNode.getElementsByClassName("ing-sug-box")[0];
    sug_box.classList.add("none-box");
    node_.parentNode.parentNode.getElementsByClassName("ing-name-input")[0].value = node_.innerHTML;
}


function validate_onfocusout(node_) {
    setTimeout(function() {
        var sug_box = node_.parentNode.getElementsByClassName("ing-sug-box")[0];
        var ing_vld = node_.parentNode.getElementsByClassName("ing-validator")[0];
        sug_box.classList.add("none-box");    
        xhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                res = JSON.parse(this.responseText);
                if(res["is_valid"] == 1) {
                    ing_vld.innerHTML = '<p class="p-4 success-color">'+ing_name_valid_text+'</p>';
                } else {
                    ing_vld.innerHTML = '<p class="p-4 danger-color">'+ing_name_not_found_error_text+'</p>';
                }
            }
        };
        xhttp.open("GET", "/validate_ing?ing-name=" + node_.value, true);
        xhttp.send();
    }, 1000);
}


function ing_name_out(node_) {
    setTimeout(function() {
        var ing_sug = node_.parentNode.getElementsByClassName('ing-sug-box')[0];
        ing_sug.classList.add("none-box");
    }, 500);
}


function add_ing_func() { 
    var new_ing_box = ing_box_root.cloneNode(true);
    new_ing_box.classList.remove("none-box");
    for(i in new_ing_box.getElementsByClassName("input")) {
        i.required = true;
    };
    ing_box.appendChild(new_ing_box);
}


function remove_ing_func(node_) {
    ing_box.removeChild(node_.parentNode);
}


function clear_recipe_func() {
    while (ing_box.childNodes.length > 3) {
        ing_box.removeChild(ing_box.lastChild);
    }
    form_.reset();
    ing_box.childNodes[0].getElementsByClassName("ing-validator")[0].classList.add("none-box");
    ing_box.childNodes[0].getElementsByClassName("ing-sug-box")[0].classList.add("none-box");
    output_box.classList.add("none-box");
}


fill_serving_amount_func();