from flask import Flask, jsonify, request
import json
import os

app = Flask(__name__)

def load_customers():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(base_dir, "data", "customers.json")
    with open(json_path, "r") as f:
        return json.load(f)


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "service": "mock-server"}), 200


@app.route("/api/customers" , methods=['GET'])
def get_customers():
    customers = load_customers()

    
    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 10, type=int)

    total = len(customers)
    start = (page-1)*limit
    end = start+limit
    paginated = customers[start:end]

    return jsonify({
        "data" : paginated,
        "total" : total,
        "page" : page , 
        "limit" : limit
    })


@app.route('/api/customers/<customer_id>' , methods=['GET'])
def get_customer(customer_id):
    customers = load_customers()

    customer = next(
        (c for c in customers if c['customer_id'] == customer_id),
        None
    )

    if customer is None:
        return jsonify({"error": f"Customer {customer_id} not found"}), 404
    
    return jsonify({"data": customer}), 200



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)