from flask import Flask, render_template, request

app = Flask(__name__)

def convert(decimal_num):
    # set the dictionary for roman numerals
    roman = {1000: 'M', 900: 'CM', 500: 'D', 400: 'CD', 100: 'C', 90: 'XC',
             50: 'L', 40: 'XL', 10: 'X', 9: 'IX', 5: 'V', 4: 'IV', 1: 'I'}
    # initialize the result variable
    num_to_roman = ''
    # loop the roman numerals, calculate for each symbol and add to the result
    for i in roman.keys():
        num_to_roman += roman[i] * (int(decimal_num) // i)
        decimal_num %= i
    return num_to_roman


@app.route('/', methods = ["GET"])
def head():    
    return render_template("index.html", developer_name = "Nec", not_valid = False )


@app.route('/', methods = ["GET", "POST"])
def result():
    mynumber = request.form.get("number")
    if not mynumber.isdigit():
        return render_template("index.html", not_valid = True)
    
    elif int(mynumber) >= 4000 :
        return render_template("index.html", not_valid = True)
    
    else:
        return render_template("result.html", number_decimal = mynumber, number_roman = convert(int(mynumber)), developer_name = "Nec")
           

if __name__ == "__main__" :
    #app.run(debug = True)
     app.run(host = "0.0.0.0", port = 80)