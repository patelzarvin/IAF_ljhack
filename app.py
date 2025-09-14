import joblib
import pandas as pd
from flask import Flask, request, jsonify

# Initialize the Flask App
app = Flask(__name__)

# Load your trained models
try:
    leadership_model = joblib.load('iaf_model(1).pkl')
    attrition_model = joblib.load('iaf_attrition_model(1).pkl')
    print("✅ Models loaded successfully!")
except Exception as e:
    print(f"❌ Error loading models: {e}")

# Define the prediction API endpoint
@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Get the JSON data from the request
        json_data = request.get_json()
        df = pd.DataFrame(json_data, index=[0])

        # --- Preprocessing ---
        rank_map = {'Flying Officer': 1, 'Flight Lieutenant': 0, 'Squadron Leader': 3, 'Wing Commander': 4, 'Group Captain': 2}
        spec_map = {'Admin': 0, 'Data Analyst': 1, 'Engineer': 2, 'Ground Staff': 3, 'Medical': 4, 'Pilot': 5, 'admin': 6, 'pilot': 7}
        attrition_map = {'High': 0, 'Low': 1, 'Medium': 2, 'high': 3}
        
        df['Rank'] = df['Rank'].map(rank_map)
        df['Specialization'] = df['Specialization'].map(spec_map)
        df['AttritionRisk_encoded'] = df['AttritionRisk'].map(attrition_map)
        
        # Add the missing SkillCluster column with a default value
        df['SkillCluster'] = 0 # Assigning a default cluster

        # --- Prediction ---
        # Features for the leadership model
        leadership_features = df[['PersonnelID', 'Age', 'YearsOfService', 'Rank', 'Specialization', 
                                  'PerformanceRating', 'TrainingCoursesCompleted', 'MissionSuccessRate', 
                                  'MedicalFitnessScore', 'PeerReviewScore', 'CommandersAssessment', 'AttritionRisk_encoded']]
        
        # Features for the attrition model (NOW MATCHING the notebook)
        attrition_features = df[['PersonnelID', 'Age', 'YearsOfService', 'Rank', 'Specialization',
                                 'PerformanceRating', 'TrainingCoursesCompleted', 'MissionSuccessRate',
                                 'MedicalFitnessScore', 'PeerReviewScore', 'CommandersAssessment', 'SkillCluster']]

        # Get predictions
        leadership_pred = leadership_model.predict(leadership_features.rename(columns={'AttritionRisk_encoded': 'AttritionRisk'}))
        attrition_pred = attrition_model.predict(attrition_features)

        # --- Format Response ---
        leadership_map_inv = {0: 'High', 1: 'Low', 2: 'Medium'}
        attrition_map_inv = {0: 'High', 1: 'Low', 2: 'Medium', 3: 'High'}

        response = {
            'leadership_potential': leadership_map_inv.get(leadership_pred[0], "Unknown"),
            'attrition_risk': attrition_map_inv.get(attrition_pred[0], "Unknown")
        }
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({'error': str(e)})

# Run the app
if __name__ == '__main__':
    app.run(debug=True, port=5000)