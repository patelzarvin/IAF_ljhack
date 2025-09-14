import streamlit as st
import requests
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# --- 1. LOGIN PAGE FUNCTION ---
def login_page():
    """Displays the login page and handles authentication."""
    st.set_page_config(
        page_title="IAF AI Login",
        layout="centered"
    )
    
    # --- ADDED LOGO ---
    st.image("logo1.png", width=150)

    st.title("IAF AI-Powered Personnel Insights")
    st.subheader("Login to Access the Dashboard")

    with st.form("login_form"):
        username = st.text_input("Username", key="username")
        password = st.text_input("Password", type="password", key="password")
        submitted = st.form_submit_button("Login")

        if submitted:
            # --- Hardcoded credentials ---
            if username == "IAF123" and password == "1234":
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("The username or password you entered is incorrect.")

# --- 2. MAIN APPLICATION FUNCTION ---
def main_dashboard():
    """This function contains your entire dashboard application."""

    st.set_page_config(
        page_title="IAF Human Management AI",
        page_icon="logo1.png", # Make sure logo1.png is in the folder
        layout="wide"
    )

    @st.cache_data
    def load_data():
        try:
            df = pd.read_csv('dataset.csv')
            df['AttritionRisk'] = df['AttritionRisk'].str.title()
            df['LeadershipPotential'] = df['LeadershipPotential'].str.title()
            return df
        except FileNotFoundError:
            st.error("Error: `dataset.csv` not found. Please make sure the file is in the same folder.")
            return None

    df_original = load_data()

    # --- UPDATED & INTERACTIVE SIDEBAR ---
    with st.sidebar:
        st.image("logo1.png", width=100)
        st.title("IAF AI Insights")
        st.info(f"Welcome, **{st.session_state.get('username', 'IAF123')}**!")
        st.markdown("---")
        
        if df_original is not None:
            st.header("Dashboard Filters")
            # Interactive filters
            selected_ranks = st.multiselect(
                'Filter by Rank',
                options=df_original['Rank'].unique(),
                default=df_original['Rank'].unique()
            )
            selected_specs = st.multiselect(
                'Filter by Specialization',
                options=df_original['Specialization'].unique(),
                default=df_original['Specialization'].unique()
            )
            df_filtered = df_original[
                df_original['Rank'].isin(selected_ranks) &
                df_original['Specialization'].isin(selected_specs)
            ]
        else:
            df_filtered = pd.DataFrame() # Empty dataframe if data fails to load

        st.markdown("---")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()

    # --- Main Page Content ---
    col1, col2 = st.columns([1, 5])
    with col1:
        st.image("logo1.png", width=150)
    with col2:
        st.title("IAF AI-Powered Personnel Insights")

    st.write("Enter personnel data for real-time predictions or use the interactive dashboard below to analyze workforce trends.")

    # --- Prediction Section (No Change) ---
    st.header("Personnel Prediction Tool")
    # ... (form code remains the same)
    with st.form("prediction_form"):
        # ... form elements ...
        col1_form, col2_form = st.columns(2)
        with col1_form:
            age = st.slider("Age", 20, 60, 35)
            years_of_service = st.slider("Years of Service", 1, 40, 12)
            rank = st.selectbox("Rank", ["Flying Officer", "Flight Lieutenant", "Squadron Leader", "Wing Commander", "Group Captain"])
            specialization = st.selectbox("Specialization", ["Pilot", "Engineer", "Admin", "Ground Staff", "Medical"])
            performance_rating = st.slider("Performance Rating (1-5)", 1, 5, 4)
        with col2_form:
            training_courses = st.number_input("Training Courses Completed", min_value=0, max_value=20, value=9, step=1)
            mission_success_rate = st.slider("Mission Success Rate (%)", 0.0, 100.0, 98.5)
            medical_fitness = st.slider("Medical Fitness Score", 0, 100, 96)
            peer_review = st.number_input("Peer Review Score (1-5)", min_value=1.0, max_value=5.0, value=4.7, step=0.1, format="%.1f")
            commanders_assessment = st.number_input("Commander's Assessment (1-5)", min_value=1.0, max_value=5.0, value=4.8, step=0.1, format="%.1f")
        submitted = st.form_submit_button("Analyze Personnel", type="primary")

    if submitted:
        # ... (prediction submission logic remains the same)
        api_data = {
            "PersonnelID": 101, "Age": age, "YearsOfService": years_of_service, "Rank": rank,
            "Specialization": specialization, "PerformanceRating": performance_rating,
            "TrainingCoursesCompleted": training_courses, "MissionSuccessRate": mission_success_rate,
            "MedicalFitnessScore": medical_fitness, "PeerReviewScore": peer_review,
            "CommandersAssessment": commanders_assessment, "AttritionRisk": "Low"
        }
        with st.spinner('Asking the AI...'):
            try:
                response = requests.post("http://127.0.0.1:5000/predict", json=api_data, timeout=10)
                response.raise_for_status()
                prediction = response.json()
                st.success("Analysis Complete!")
                res_col1, res_col2 = st.columns(2)
                res_col1.metric(label="Predicted Leadership Potential", value=prediction['leadership_potential'])
                res_col2.metric(label="Predicted Attrition Risk", value=prediction['attrition_risk'])
            except requests.exceptions.RequestException as e:
                st.error(f"Could not connect to the API. Make sure the backend (app.py) is running. Error: {e}")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")

    # --- REVAMPED Analytics Dashboard Section ---
    st.header("Workforce Analytics Dashboard")
    if not df_filtered.empty:
        # --- KPI Section ---
        st.markdown("#### Key Performance Indicators")
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        kpi1.metric(label="Total Personnel", value=f"{df_filtered.shape[0]:,}")
        kpi2.metric(label="Avg. Age", value=f"{df_filtered['Age'].mean():.1f}")
        kpi3.metric(label="Avg. Years of Service", value=f"{df_filtered['YearsOfService'].mean():.1f}")
        kpi4.metric(label="Avg. Mission Success", value=f"{df_filtered['MissionSuccessRate'].mean():.1f}%")
        st.markdown("---")

        with st.expander("Explore Workforce Data Visualizations", expanded=True):
            sns.set_style("whitegrid")
            
            # --- Row 1: Donut Chart & Bar Chart ---
            viz_col1, viz_col2 = st.columns(2)
            with viz_col1:
                st.subheader("Distribution by Specialization")
                spec_counts = df_filtered['Specialization'].value_counts()
                fig, ax = plt.subplots(figsize=(8, 6))
                ax.pie(spec_counts, labels=spec_counts.index, autopct='%1.1f%%', startangle=90, pctdistance=0.85)
                # Draw a circle at the center to make it a donut chart
                centre_circle = plt.Circle((0,0),0.70,fc='white')
                fig.gca().add_artist(centre_circle)
                ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
                st.pyplot(fig)

            with viz_col2:
                st.subheader("Attrition Risk by Rank")
                attrition_by_rank = df_filtered.groupby('Rank')['AttritionRisk'].value_counts(normalize=True).unstack().fillna(0) * 100
                fig, ax = plt.subplots(figsize=(8, 6))
                attrition_by_rank.plot(kind='barh', stacked=True, ax=ax, colormap='viridis')
                ax.set_xlabel('Percentage of Personnel (%)')
                ax.set_ylabel('Rank')
                ax.legend(title='Attrition Risk')
                st.pyplot(fig)

            # --- Row 2: Scatter and Box Plot ---
            st.markdown("---")
            viz_col3, viz_col4 = st.columns(2)
            with viz_col3:
                st.subheader("Years of Service vs. Mission Success Rate")
                fig, ax = plt.subplots(figsize=(8, 6))
                sns.scatterplot(x='YearsOfService', y='MissionSuccessRate', data=df_filtered, alpha=0.6, color='green', ax=ax, hue='Rank')
                ax.set_xlabel('Years of Service')
                ax.set_ylabel('Mission Success Rate (%)')
                st.pyplot(fig)

            with viz_col4:
                st.subheader("Performance Rating Across Ranks")
                fig, ax = plt.subplots(figsize=(8, 6))
                rank_order = df_filtered['Rank'].value_counts().index
                sns.boxplot(x='PerformanceRating', y='Rank', data=df_filtered, order=rank_order, palette='coolwarm', ax=ax)
                ax.set_xlabel('Performance Rating (1-5)')
                ax.set_ylabel('Rank')
                st.pyplot(fig)
    else:
        st.warning("No data to display. Please adjust filters or ensure the dataset is loaded.")

# --- 3. MAIN SCRIPT LOGIC ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if st.session_state.logged_in:
    main_dashboard()
else:
    login_page()