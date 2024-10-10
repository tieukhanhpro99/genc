from flask import Flask, request, jsonify
import random
import re
from datetime import datetime

app = Flask(__name__)

def luhn_algorithm(card_number):
    def digits_of(n):
        return [int(d) for d in str(n)]
    digits = digits_of(card_number)
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    checksum = sum(odd_digits)
    for d in even_digits:
        checksum += sum(digits_of(d*2))
    return checksum % 10 == 0

def genccn(bin):
    remaining_digits = 16 - len(bin)
    additional_digits = ''.join([str(random.randint(0, 9)) for _ in range(remaining_digits - 1)])
    partial_card_number = bin + additional_digits
    for i in range(10):
        if luhn_algorithm(partial_card_number + str(i)):
            return partial_card_number + str(i)
    return None

def genci(input):
    current_year = datetime.now().year
    current_month = datetime.now().month
    parts = input.split('|')
    while len(parts) < 4:
        parts.append('')

    bin = re.sub(r'\D', '', parts[0])

    if len(bin) < 5:
        return "Input must be at least 5 digits long."
    
    card_number = genccn(bin)
    if card_number:
        parts[0] = card_number
    else:
        return "Failed to generate a valid card number."

    if not parts[1] or not parts[2]:
        year = random.randint(current_year, current_year + 6)
        if year == current_year:
            month = random.randint(current_month, 12)
        else:
            month = random.randint(1, 12)
        parts[1] = str(month).zfill(2)
        parts[2] = str(year)
    else:
        parts[1] = parts[1].zfill(2)
        parts[2] = parts[2]

    if not parts[3]:
        parts[3] = str(random.randint(100, 999))
    cc = '|'.join(parts)
    return [cc, bin]

@app.route('/generate_cc', methods=['POST'])
def generate_cc():
    data = request.json
    input_data = data.get('input', '')
    
    if not input_data:
        return jsonify({'error': 'Input is required.'}), 400
    
    result = genci(input_data)
    
    if isinstance(result, str):
        return jsonify({'error': result}), 400
    
    return jsonify({'credit_card': result[0], 'bin': result[1]})

if __name__ == '__main__':
    app.run(debug=True)
