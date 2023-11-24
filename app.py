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
		
		category_data = [{"category_id": product.category_id,"category_name": product.category_name, "image": product.image, "content": product.content
		    } for product in category]
		
		
		return jsonify(category_data)


@app.route('/api/v1/category/items/', methods=['GET'])
def get_items_all():
    with engine.connect() as conn:
        query = text(
            "SELECT i.item_id, i.item_name, i.unit, c.category_name, i.image FROM Item i JOIN Category c ON i.category_id = c.category_id;")
        items = conn.execute(query)

        item_data = [
            {"item_id": item.item_id, "item_name": item.item_name, "unit": item.unit,
             "category": item.category_name, "image": item.image}
            for item in items
        ]

    return jsonify(item_data)

@app.route('/api/v1/category/<int:category_id>', methods=['GET'])
def get_category_details(category_id):
    with engine.connect() as conn:
        category_query = text("SELECT * FROM Category WHERE category_id = :category_id")
        category_result = conn.execute(category_query, {"category_id": category_id})
        category = category_result.fetchone()

        if category is None:
            abort(404, description="Category not found")

        items_query = text("SELECT i.item_id, i.item_name, i.unit, i.image FROM Item i WHERE i.category_id = :category_id")
        items_result = conn.execute(items_query, {"category_id": category_id})
        items_data = [
            {"item_id": item.item_id, "item_name": item.item_name, "unit": item.unit, "image": item.image}
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
                SELECT i.item_id, i.item_name, i.unit, c.category_name, i.image FROM Item i 
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
                "unit": item.unit,
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
                SELECT i.item_id, i.item_name, i.unit, c.category_name, i.image FROM Item i 
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
                "unit": item.unit,
                "category": item.category_name,
                "image": item.image
            }
        return jsonify(item_data)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})    


# branch

@app.route('/api/v1/branch/', methods=['GET'])
def get_all_branches():
    try:
        with engine.connect() as conn:
            query = text("SELECT * FROM Branch")
            branches = conn.execute(query)

            branch_data = [
                {"branch_id": branch.branch_id, "branch_name": branch.branch_name, "location": branch.location}
                for branch in branches
            ]

        return jsonify(branch_data)

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    
@app.route('/api/v1/branch/<int:branch_id>', methods=['GET'])
def get_branch_by_id(branch_id):
    try:
        with engine.connect() as conn:
            query = text("SELECT * FROM Branch WHERE branch_id = :branch_id")
            result = conn.execute(query, {"branch_id": branch_id})
            branch = result.fetchone()

            if branch is None:
                abort(404, description="Branch not found")

            branch_data = {
                "branch_id": branch.branch_id,
                "branch_name": branch.branch_name,
                "location": branch.location
            }

        return jsonify(branch_data)

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})



@app.route('/api/v1/branch/<int:branch_id>/items', methods=['GET'])
def get_items_for_branch(branch_id):
    try:
        with engine.connect() as conn:
            query = text("""
                SELECT bi.item_id, i.item_name, i.unit, i.image, bi.amount
                FROM BranchItem bi
                JOIN Item i ON bi.item_id = i.item_id
                WHERE bi.branch_id = :branch_id;
            """)
            result = conn.execute(query, {"branch_id": branch_id})
            items_data = [
                {"item_id": item.item_id, "item_name": item.item_name, "unit": item.unit, "image": item.image,
                 "amount": item.amount}
                for item in result
            ]

        return jsonify(items_data)

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    
# main stock

@app.route('/api/v1/main_stock/items', methods=['GET'])
def get_items_in_main_stock():
    try:
        with engine.connect() as conn:
            query = text("""
                SELECT ms.main_stock_id, i.item_id, i.item_name, i.unit, i.image, ms.amount
                FROM MainStock ms
                JOIN Item i ON ms.item_id = i.item_id;
            """)
            result = conn.execute(query)
            items_data = [
                {"main_stock_id": item.main_stock_id, "item_id": item.item_id, "item_name": item.item_name,
                 "unit": item.unit, "image": item.image, "amount": item.amount}
                for item in result
            ]

        return jsonify(items_data)

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    
    

@app.route('/api/v1/main_stock/category/<int:category_id>', methods=['GET'])
def get_main_stock_items_by_category(category_id):
    try:
        with engine.connect() as conn:
            query = text("""
                SELECT ms.main_stock_id, ms.item_id, i.item_name, amount, i.unit, i.image, c.category_name
                FROM MainStock ms
                JOIN Item i ON ms.item_id = i.item_id
                JOIN Category c ON i.category_id = c.category_id
                WHERE i.category_id = :category_id;
            """)
            result = conn.execute(query, {"category_id": category_id})
            main_stock_items = [
                {
                    "main_stock_id": row.main_stock_id,
                    "item_id": row.item_id,
                    "item_name": row.item_name,
                    "amount": row.amount,
                    "unit": row.unit,
                    "image": row.image,
                    "category_name": row.category_name
                }
                for row in result
            ]

        return jsonify(main_stock_items)

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/v1/main_stock/<int:item_id>/add_amount', methods=['PUT'])
def add_amount_to_main_stock(item_id):
    try:
        add_amount = request.json.get('add_amount')

        if not add_amount:
            return jsonify({'success': False, 'error': 'add_amount is required.'}), 400

        with engine.connect() as conn:
            check_item_query = text("SELECT * FROM MainStock WHERE item_id = :item_id")
            item_exists = conn.execute(check_item_query, {"item_id": item_id}).fetchone()

            if item_exists:
                change_type = 'add'
                insert_transaction_query = text("""
                    INSERT INTO MainStockTransactions (time, item_id, change_type, amount)
                    VALUES (CURRENT_TIMESTAMP, :item_id, :change_type, :add_amount)
                """)
                conn.execute(insert_transaction_query, {
                    "item_id": item_id,
                    "change_type": change_type,
                    "add_amount": add_amount
                })
                
                update_main_stock_query = text("UPDATE MainStock SET amount = amount + :add_amount WHERE item_id = :item_id")
                conn.execute(update_main_stock_query, {"add_amount": add_amount, "item_id": item_id})
                conn.commit()

                return jsonify({'success': True, 'message': f'Amount added to MainStock for item {item_id}.'})
            else:
                return jsonify({'success': False, 'error': f'Item with ID {item_id} does not exist in MainStock.'}), 404

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500



@app.route('/api/v1/branch/<int:branch_id>/category/<int:category_id>/items', methods=['GET'])
def get_items_by_branch_and_category(branch_id, category_id):
    try:
        with engine.connect() as conn:
            category_query = text("SELECT category_name FROM Category WHERE category_id = :category_id")
            category_result = conn.execute(category_query, {"category_id": category_id})
            category_name = category_result.scalar()

            query = text("""
                SELECT bi.amount, i.item_id, i.item_name, i.unit, i.image
                FROM BranchItem bi
                JOIN Item i ON bi.item_id = i.item_id
                WHERE bi.branch_id = :branch_id AND i.category_id = :category_id;
            """)
            result = conn.execute(query, {"branch_id": branch_id, "category_id": category_id})
            items_data = [
                {
                    "item_id": item.item_id,
                    "item_name": item.item_name,
                    "amount": item.amount,
                    "unit": item.unit,
                    "image": item.image
                }
                for item in result
            ]

            response_data = {
                "category_name": category_name,
                "items": items_data
            }

        return jsonify(response_data)

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    

@app.route('/api/v1/branch/<int:branch_id>/item/<int:item_id>/request_from_main', methods=['PUT', 'PATCH'])
def update_item_amount_by_id(branch_id, item_id):
    try:
        change_amount = request.json.get('change_amount')

        with engine.connect() as conn:
            check_main_stock_query = text("""
                SELECT amount FROM MainStock WHERE item_id = :item_id
            """)
            main_stock_amount = conn.execute(check_main_stock_query, {"item_id": item_id}).scalar()

            if main_stock_amount is not None and main_stock_amount >= change_amount:
                update_main_stock_query = text("""
                    UPDATE MainStock SET amount = amount - :change_amount WHERE item_id = :item_id
                """)
                conn.execute(update_main_stock_query, {"change_amount": change_amount, "item_id": item_id})

                insert_transaction_query = text("""
                    INSERT INTO MainStockTransactions (time, item_id, change_type, amount)
                    VALUES (CURRENT_TIMESTAMP, :item_id, 'remove', :change_amount)
                """)
                conn.execute(insert_transaction_query, {
                    "item_id": item_id,
                    "change_amount": change_amount
                })

                # Update BranchItem
                update_branch_item_query = text("""
                    UPDATE BranchItem SET amount = amount + :change_amount 
                    WHERE item_id = :item_id AND branch_id = :branch_id
                """)
                conn.execute(update_branch_item_query, {"change_amount": change_amount, "item_id": item_id, "branch_id": branch_id})

                conn.commit()
            else:
                return jsonify({'success': False, 'error': 'Insufficient quantity in the main stock.'}), 400

        return jsonify({'success': True, 'message': f'Amount updated for item {item_id} in branch {branch_id}.'})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/v1/branch/<int:branch_id>/item/<int:item_id>/update_amount', methods=['PUT', 'PATCH'])
def update_branch_item_amount(branch_id, item_id):
    try:
        new_amount = request.json.get('new_amount')

        with engine.connect() as conn:
            update_query = text("""
                UPDATE BranchItem SET amount = :new_amount 
                WHERE item_id = :item_id AND branch_id = :branch_id
            """)
            conn.execute(update_query, {"new_amount": new_amount, "item_id": item_id, "branch_id": branch_id})

            conn.commit()

        return jsonify({'success': True, 'message': f'Amount updated for item {item_id} in branch {branch_id}.'})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    

@app.route('/api/v1/main_stock/transactions', methods=['GET'])
def get_main_stock_transactions():
    try:
        with engine.connect() as conn:
            query = text("""
                SELECT mst.transaction_id, mst.time, mst.item_id, i.item_name, i.unit, c.category_name, mst.change_type, mst.amount
                FROM MainStockTransactions mst
                JOIN Item i ON mst.item_id = i.item_id
                JOIN Category c ON i.category_id = c.category_id
                ORDER BY mst.time DESC
            """)
            result = conn.execute(query)
            transactions_data = [
                {
                    "transaction_id": row.transaction_id,
                    "time": row.time.isoformat(),
                    "item_id": row.item_id,
                    "item_name": row.item_name,
                    "unit": row.unit,
                    "category_name": row.category_name,
                    "change_type": row.change_type,
                    "amount": row.amount
                }
                for row in result
            ]

        return jsonify(transactions_data)

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
