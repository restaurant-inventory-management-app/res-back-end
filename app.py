import os
from flask import Flask, abort, jsonify, request
from sqlalchemy import create_engine,text
from dotenv import load_dotenv
from flask_cors import CORS


load_dotenv()
DATABASE_URL = os.environ['DATABASE_URL']

engine = create_engine(DATABASE_URL, echo=True)

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in the environment variables.")

app = Flask(__name__)
CORS(app)


@app.route('/', methods=['GET'])
def healthcheck():
    try:
        return '<center>The Server is running</center>'
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
  

@app.route('/api/v1/category/',methods=['GET'] )
def get_category_all():
	with engine.connect() as conn:
		query  = text("SELECT * FROM Category")
		category = conn.execute(query )
		
		category_data = [{"category_id": product.category_id,"category_name": product.category_name, "image": product.image
		    } for product in category]
		
		
		return jsonify(category_data)


@app.route('/api/v1/category/items/', methods=['GET'])
def get_items_all():
    with engine.connect() as conn:
        query = text("SELECT i.item_id, i.item_name, i.amount, c.category_name, i.image FROM Item i JOIN Category c ON i.category_id = c.category_id;")
        items = conn.execute(query)

        item_data = [
            {"item_id": item.item_id, "item_name": item.item_name, "amount": item.amount, "category": item.category_name, "image": item.image}
            for item in items
        ]

    return jsonify(item_data)

@app.route('/api/v1/category/<int:category_id>', methods=['GET'])
def get_category_details(category_id):
    with engine.connect() as conn:
        
        category_query = text("SELECT * FROM Category WHERE category_id = :category_id")
        category_result = conn.execute(category_query, {"category_id":category_id})
        category = category_result.fetchone()

        if category is None:
            abort(404, description="Category not found")

        items_query = text("SELECT i.item_id, i.item_name, i.amount, i.image FROM Item i WHERE i.category_id = :category_id")
        items_result = conn.execute(items_query,{"category_id" : category_id})
        items_data = [
            {"item_id": item.item_id, "item_name": item.item_name, "amount": item.amount, "image": item.image}
            for item in items_result
        ]

    category_details = {
        "category_id": category.category_id,
        "category_name": category.category_name,
        "image": category.image,
        "items": items_data
    }

    return jsonify(category_details)


@app.route('/api/v1/category/<int:category_id>/<string:item_name>', methods=['GET'])
def get_item_detail_by_name(category_id, item_name):
    try:
        with engine.connect() as conn:
            query = text("""
                SELECT i.item_id, i.item_name, i.amount, c.category_name, i.image FROM Item i 
                JOIN Category c ON i.category_id = c.category_id 
                WHERE i.category_id = :category_id AND LOWER(i.item_name) = LOWER(:item_name);
                        """)
            result = conn.execute(query, {"category_id": category_id, "item_name": item_name})
            item = result.fetchone()

            if item is None:
                abort(404, description="Item not found in the specified category")

            item_data = {
                "item_id": item.item_id,
                "item_name": item.item_name,
                "amount": item.amount,
                "category": item.category_name,
                "image": item.image
            }
        return jsonify(item_data)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/v1/category/<int:category_id>/<int:item_id>', methods=['GET'])
def get_item_detail_by_id(category_id, item_id):
    try:
        with engine.connect() as conn:
            query = text("""
                SELECT i.item_id, i.item_name, i.amount, c.category_name, i.image FROM Item i 
                JOIN Category c ON i.category_id = c.category_id 
                WHERE i.category_id = :category_id AND i.item_id = :item_id;
                        """)
            result = conn.execute(query, {"category_id": category_id, "item_id": item_id})
            item = result.fetchone()

            if item is None:
                abort(404, description="Item not found in the specified category")

            item_data = {
                "item_id": item.item_id,
                "item_name": item.item_name,
                "amount": item.amount,
                "category": item.category_name,
                "image": item.image
            }
        return jsonify(item_data)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

    
@app.route('/api/v1/item/<int:item_id>/update_amount', methods=['PUT', 'PATCH'])
def update_item_amount_by_id(item_id):
    try:
        new_amount = request.json.get('amount')

        with engine.connect() as conn:
            current_amount_query = text("SELECT amount FROM Item WHERE item_id = :item_id")
            current_amount_result = conn.execute(current_amount_query, {"item_id": item_id})
            current_amount = current_amount_result.scalar()

            update_query = text("""
                UPDATE Item SET amount = :new_amount WHERE item_id = :item_id
            """)
            conn.execute(update_query, {"new_amount": new_amount, "item_id": item_id})

            conn.commit()

            insert_change_query = text("""
                INSERT INTO InventoryChanges (time, item_id, amount_before_change, amount_after_change)
                VALUES (CURRENT_TIMESTAMP, :item_id, :current_amount, :new_amount)
            """)
            conn.execute(insert_change_query, {"item_id": item_id, "current_amount": current_amount, "new_amount": new_amount})

            conn.commit()

        return jsonify({'success': True, 'message': f'Amount updated for item {item_id}.'})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

    

@app.route('/api/v1/transaction_history', methods=['GET'])
def get_all_transaction_history():
    try:
        with engine.connect() as conn:
            query = text("""
                SELECT ic.change_id, time, ic.item_id, amount_before_change, amount_after_change, item_name,category_name
                FROM InventoryChanges ic JOIN Item i ON ic.item_id = i.item_id
                JOIN Category c ON i.category_id = c.category_id
                ORDER BY time DESC;
            """)
            result = conn.execute(query)
            transaction_history = [
                 {
                    "change_id": row.change_id,
                    "transaction_time": row.time.isoformat(),
                    "item_id": row.item_id,
                    "item_name": row.item_name,
                    "category_name": row.category_name,
                    "amount_before_change": row.amount_before_change,
                    "amount_after_change": row.amount_after_change
                }
                for row in result
            ]

        return jsonify(transaction_history)

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})





  