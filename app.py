from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
import math
from collections import Counter
import re

app = Flask(__name__)
CORS(app)

def caesar_cipher(text, shift, encrypt=True):
    """Implement Caesar cipher encryption/decryption"""
    result = ""
    shift = shift if encrypt else -shift
    
    for char in text:
        if char.isalpha():
            ascii_offset = 65 if char.isupper() else 97
            result += chr((ord(char) - ascii_offset + shift) % 26 + ascii_offset)
        else:
            result += char
    return result

def vigenere_cipher(text, key, encrypt=True):
    """Implement Vigenère cipher encryption/decryption"""
    result = ""
    key = key.upper()
    key_index = 0
    
    for char in text:
        if char.isalpha():
            ascii_offset = 65 if char.isupper() else 97
            key_char = key[key_index % len(key)]
            key_shift = ord(key_char) - 65
            
            if encrypt:
                shift = key_shift
            else:
                shift = -key_shift
                
            result += chr((ord(char) - ascii_offset + shift) % 26 + ascii_offset)
            key_index += 1
        else:
            result += char
    return result

def calculate_frequency(text):
    """Calculate letter frequency distribution"""
    text = text.lower()
    letters = [char for char in text if char.isalpha()]
    
    if not letters:
        return {}
    
    freq = Counter(letters)
    total = len(letters)
    
    percentages = {letter: (count / total * 100) for letter, count in freq.items()}
    
    # Fill missing letters with 0
    for char in 'abcdefghijklmnopqrstuvwxyz':
        if char not in percentages:
            percentages[char] = 0
    
    return {
        'counts': dict(freq),
        'percentages': percentages,
        'total': total
    }

def calculate_entropy(text):
    """Calculate Shannon entropy of text"""
    # Clean text - keep only letters
    clean_text = re.sub(r'[^a-zA-Z]', '', text).lower()
    
    if not clean_text:
        return 0
    
    # Calculate frequencies
    freq = Counter(clean_text)
    total = len(clean_text)
    
    # Calculate entropy
    entropy = 0
    for count in freq.values():
        probability = count / total
        entropy -= probability * math.log2(probability)
    
    return entropy

def find_patterns(text, min_length=3, max_length=10):
    """Find repeated patterns in text"""
    text = re.sub(r'[^a-z]', '', text.lower())
    patterns = {}
    
    for length in range(min_length, max_length + 1):
        for i in range(len(text) - length + 1):
            pattern = text[i:i + length]
            
            if pattern in patterns:
                patterns[pattern]['count'] += 1
                patterns[pattern]['positions'].append(i)
            else:
                patterns[pattern] = {
                    'count': 1,
                    'positions': [i]
                }
    
    # Return only patterns that appear more than once
    repeated_patterns = {p: d for p, d in patterns.items() if d['count'] > 1}
    
    # Sort by frequency
    sorted_patterns = dict(sorted(repeated_patterns.items(), 
                                  key=lambda x: x[1]['count'], 
                                  reverse=True))
    
    return sorted_patterns

@app.route('/api/caesar', methods=['POST'])
def api_caesar():
    """API endpoint for Caesar cipher"""
    data = request.json
    text = data.get('text', '')
    shift = data.get('shift', 3)
    action = data.get('action', 'encrypt')  # 'encrypt' or 'decrypt'
    
    if action == 'encrypt':
        result = caesar_cipher(text, shift, True)
    else:
        result = caesar_cipher(text, shift, False)
    
    return jsonify({'result': result})

@app.route('/api/vigenere', methods=['POST'])
def api_vigenere():
    """API endpoint for Vigenère cipher"""
    data = request.json
    text = data.get('text', '')
    key = data.get('key', 'KEY')
    action = data.get('action', 'encrypt')  # 'encrypt' or 'decrypt'
    
    if action == 'encrypt':
        result = vigenere_cipher(text, key, True)
    else:
        result = vigenere_cipher(text, key, False)
    
    return jsonify({'result': result})

@app.route('/api/base64', methods=['POST'])
def api_base64():
    """API endpoint for Base64 encoding/decoding"""
    data = request.json
    text = data.get('text', '')
    action = data.get('action', 'encode')  # 'encode' or 'decode'
    
    try:
        if action == 'encode':
            # Encode string to Base64
            encoded_bytes = base64.b64encode(text.encode('utf-8'))
            result = encoded_bytes.decode('utf-8')
        else:
            # Decode Base64 to string
            decoded_bytes = base64.b64decode(text)
            result = decoded_bytes.decode('utf-8')
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    
    return jsonify({'result': result})

@app.route('/api/frequency', methods=['POST'])
def api_frequency():
    """API endpoint for frequency analysis"""
    data = request.json
    text = data.get('text', '')
    
    freq_data = calculate_frequency(text)
    
    return jsonify(freq_data)

@app.route('/api/entropy', methods=['POST'])
def api_entropy():
    """API endpoint for entropy calculation"""
    data = request.json
    text = data.get('text', '')
    
    entropy = calculate_entropy(text)
    
    return jsonify({'entropy': entropy})

@app.route('/api/patterns', methods=['POST'])
def api_patterns():
    """API endpoint for pattern recognition"""
    data = request.json
    text = data.get('text', '')
    min_length = data.get('min_length', 3)
    max_length = data.get('max_length', 10)
    
    patterns = find_patterns(text, min_length, max_length)
    
    # Convert to list for JSON serialization
    patterns_list = []
    for pattern, data in patterns.items():
        patterns_list.append({
            'pattern': pattern,
            'count': data['count'],
            'positions': data['positions']
        })
    
    return jsonify({'patterns': patterns_list})

@app.route('/api/classify', methods=['POST'])
def api_classify():
    """API endpoint for cipher classification"""
    data = request.json
    text = data.get('text', '')
    
    # Simplified classification logic
    entropy = calculate_entropy(text)
    has_special_chars = bool(re.search(r'[^a-zA-Z\s]', text))
    all_upper_or_lower = text.isupper() or text.islower()
    
    if entropy > 4.5:
        classification = "Random Text or One-Time Pad"
        confidence = 75
        details = "High entropy suggests random distribution of characters."
    elif not has_special_chars and all_upper_or_lower:
        classification = "Classical Cipher (Caesar, Substitution, or Vigenère)"
        confidence = 70
        details = "Text contains only letters with consistent casing, typical of classical ciphers."
    elif has_special_chars:
        classification = "Base64 or Modern Encryption"
        confidence = 65
        details = "Presence of non-alphabetic characters suggests encoding like Base64 or modern encryption."
    else:
        classification = "Unknown/Plain Text"
        confidence = 50
        details = "Unable to determine cipher type with high confidence."
    
    return jsonify({
        'classification': classification,
        'confidence': confidence,
        'details': details,
        'entropy': entropy
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'CryptoLab API'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)