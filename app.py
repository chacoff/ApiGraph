from flask import Flask, jsonify, render_template
from flask_cors import CORS
import pandas as pd
import json
from datetime import datetime

from data_processor import DataFrameConstructor

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)

def json_serial(obj):
    if isinstance(obj, datetime):
        return obj.strftime('%Y-%m-%d')
    raise TypeError(f"Type {type(obj)} not serializable")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/data/<string:y_axis>', methods=['GET'])
def get_data(y_axis):
    try:
        constructor = DataFrameConstructor(y_axis=y_axis)
        constructor.get_data().convert_dataframe().clean_df()
        
        df = constructor.get_cleaned_df()
        
        result = []
        pile_groups = df['pile_group'].unique()
        
        for pile_group in pile_groups:
            pile_data = df[df['pile_group'] == pile_group]
            
            dataset = {
                'label': f'{pile_group}',
                'data': [],
                'borderWidth': 1,
                'fill': False
            }
            
            for _, row in pile_data.iterrows():
                dataset['data'].append({
                    'x': json_serial(row['flightday']),
                    'y': float(row[y_axis])
                })
                
            result.append(dataset)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)