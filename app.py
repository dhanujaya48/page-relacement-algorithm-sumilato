from flask import Flask, render_template, request, jsonify
import numpy as np
import deadlock  
app = Flask(__name__)
@app.route('/')
def home():
    return render_template('index.html')
@app.route('/detect', methods=['POST'])
def detect():
    data = request.json
    processes = int(data['processes'])
    resources = int(data['resources'])
    allocation = np.array(data['allocation']).reshape(processes, resources)
    request_matrix = np.array(data['request']).reshape(processes, resources)
deadlock_detected, message = deadlock.detect_deadlock(processes, resources, allocation, request_matrix)
    return jsonify({"deadlock": deadlock_detected, "message": message})
if __name__ == "__main__":
    app.run(debug=True)
2. deadlock.py (Deadlock Detection Algorithm)
import numpy as np
def detect_deadlock(processes, resources, allocation, request):
    work = np.zeros(resources)
    finish = [False] * processes
    for j in range(resources):
        work[j] = sum(allocation[i][j] for i in range(processes)) - sum(request[i][j] for i in range(processes))
    safe_sequence = []
    while len(safe_sequence) < processes:
        allocated = False
        for i in range(processes):
            if not finish[i] and all(request[i][j] <= work[j] for j in range(resources)):
                safe_sequence.append(i)
                work += allocation[i]
                finish[i] = True
                allocated = True
                break
        if not allocated:
            return True, "Deadlock detected!"
    return False, f"No deadlock detected. Safe sequence: {safe_sequence}"
3. index.html (Frontend )
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Deadlock Detection Tool</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>
    <h1>Automated Deadlock Detection Tool</h1>
    <form id="deadlockForm">
        <label>Number of Processes:</label>
        <input type="number" id="processes" min="1" required><br><br>
        <label>Number of Resources:</label>
        <input type="number" id="resources" min="1" required><br><br>
        <label>Allocation Matrix (comma-separated, row by row):</label>
        <textarea id="allocation" rows="4" placeholder="e.g., 0,1,0, 2,0,0, 0,0,1" required></textarea><br><br>
        <label>Request Matrix (comma-separated, row by row):</label>
        <textarea id="request" rows="4" placeholder="e.g., 0,0,1, 0,1,0, 1,0,0" required></textarea><br><br>
        <button type="submit">Detect Deadlock</button>
    </form>
    <h2>Result:</h2>
    <p id="result"></p>
    <script src="{{ url_for('static', filename='script.js') }}"></script>
</body>
</html>
4. style.css (Frontend Styling)

body {
    font-family: 'Arial', sans-serif;
    text-align: center;
    background: linear-gradient(to right, #f8f9fa, #e9ecef);
    margin: 0;
    padding: 20px;
}

.container {
    width: 50%;
    margin: auto;
    background: white;
    padding: 25px;
    border-radius: 10px;
    box-shadow: 0px 5px 15px rgba(0, 0, 0, 0.2);
    transition: 0.3s;
}

.container:hover {
    transform: scale(1.02); 
}

input, textarea {
    display: block;
    width: 90%;
    margin: 10px auto;
    padding: 12px;
    border: 2px solid #ccc;
    border-radius: 8px;
    font-size: 16px;
    transition: 0.3s;
}

input:focus, textarea:focus {
    border-color: #007BFF;
    outline: none;
    box-shadow: 0px 0px 5px rgba(0, 123, 255, 0.5);
}

button {
    padding: 14px 22px;
    background: #007BFF;
    color: white;
    font-size: 18px;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    transition: 0.3s;
}

button:hover {
    background: #0056b3;
    transform: scale(1.05);
}

.result-box {
    margin-top: 20px;
    padding: 20px;
    font-size: 18px;
    font-weight: bold;
    display: none;
    border-radius: 8px;
}

.success {
    background: #d4edda;
    border-left: 6px solid #28a745;
    color: #155724;
}

.error {
    background: #f8d7da;
    border-left: 6px solid #dc3545;
    color: #721c24;
}
5. script.js (JavaScript Logic)
document.getElementById('deadlockForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const processes = document.getElementById('processes').value;
    const resources = document.getElementById('resources').value;
    const allocationMatrix = document.getElementById('allocation').value
        .trim().split(/\s*[,|\s]\s*/).map(Number);
    const requestMatrix = document.getElementById('request').value
        .trim().split(/\s*[,|\s]\s*/).map(Number);
    const allocation = [];
    const request = [];
    for (let i = 0; i < processes; i++) {
        allocation.push(allocationMatrix.slice(i * resources, (i + 1) * resources));
        request.push(requestMatrix.slice(i * resources, (i + 1) * resources));
    }
    const response = await fetch('/detect', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ processes, resources, allocation, request })
    });
    const result = await response.json();
    const resultBox = document.getElementById('result-box');
    document.getElementById('result').innerText = result.message;
    resultBox.style.display = "block";
    if (result.deadlock) {
        resultBox.className = "result-box error";  
    } else {
        resultBox.className = "result-box success";  
    }
});

