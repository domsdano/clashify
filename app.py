import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Custom functions (assumed to be provided)
from library.model import balance_data

# Set page configuration
st.set_page_config(
    page_title="Online Food Order Dataset 🍔",
    layout="centered",
    page_icon="🍔"
)

# Sidebar navigation
st.sidebar.title("Navigation")
sections = ["Home", "Dataset", "Map", "Column Visualizations", "Age Metrics", "Feedback Metrics", "Interactive Model Testing"]
selection = st.sidebar.radio("Go to", sections)

# Load dataset
data = pd.read_csv('onlinefoods.csv')

# Home Section
if selection == "Home":
    st.title("Online Food Order Dataset")
    st.write("""
    The dataset contains information collected from an online food ordering platform over a period of time.
    It encompasses various attributes related to Occupation, Family Size, Feedback, etc.
    """)
    st.markdown("**Source:** [Kaggle](https://www.kaggle.com/datasets/sudarshan24byte/online-food-dataset/data)")
    st.divider()

# Dataset Section
if selection == "Dataset":
    st.title("Dataset")
    st.write("## Dataset")
    st.write(data)

# Map Section
if selection == "Map":
    st.title("Map")
    st.write("## Map")
    st.write("Data was collected from the following locations")
    st.map(data[['latitude', 'longitude']])

# Column Visualizations Section
if selection == "Column Visualizations":
    st.title("Column Visualizations")
    
    # Numeric columns
    st.write("### Numeric Columns")
    for column in data.select_dtypes(include=[np.number]).columns:
        st.write(f"#### {column}")
        if data[column].nunique() > 20:
            st.line_chart(data[column])
        else:
            st.bar_chart(data[column].value_counts())

    # Categorical columns
    st.write("### Categorical Columns")
    for column in data.select_dtypes(include=[object]).columns:
        st.write(f"#### {column}")
        st.bar_chart(data[column].value_counts())

    # Specific visualizations for some columns
    st.write("### Specific Visualizations")
    
    # Gender distribution
    st.write("#### Gender Distribution")
    st.bar_chart(data['Gender'].value_counts())
    
    # Age distribution
    st.write("#### Age Distribution")
    st.hist(data['Age'], bins=20)
    
    # Family size distribution
    st.write("#### Family Size Distribution")
    st.area_chart(data['Family size'].value_counts())
    
    # Feedback distribution
    st.write("#### Feedback Distribution")
    feedback_counts = data['Feedback'].value_counts()
    st.write(feedback_counts.plot.pie(autopct='%1.1f%%').get_figure())

# Age Metrics Section
if selection == "Age Metrics":
    st.title("Age Metrics")
    average_age = data['Age'].mean()
    min_age = data['Age'].min()
    max_age = data['Age'].max()
    col1, col2, col3 = st.columns(3)
    col1.metric("Average Age", f"{average_age:.2f}")
    col2.metric("Min Age", f"{min_age}")
    col3.metric("Max Age", f"{max_age}")

# Feedback Metrics Section
if selection == "Feedback Metrics":
    st.title("Feedback Metrics")
    feedback_types = data['Feedback'].value_counts()
    for feedback_type, count in feedback_types.items():
        st.metric(f"{feedback_type} Feedback Count", count)

# Interactive Model Testing Section
if selection == "Interactive Model Testing":
    st.title("Interactive Model Testing")
    st.write("### Decision Tree vs Random Forest vs SVM")
    selected_features = st.multiselect(
        'Select features to include in the model',
        options=data.columns,
        default=data.columns.tolist()
    )

    # Encode categorical columns
    data_encoded = data.copy()
    label_encoders = {}
    for column in data_encoded.select_dtypes(include=[object]).columns:
        le = LabelEncoder()
        data_encoded[column] = le.fit_transform(data_encoded[column])
        label_encoders[column] = le

    # Define models
    models = {
        'Decision Tree': DecisionTreeClassifier(random_state=42),
        'Random Forest': RandomForestClassifier(random_state=42),
        'Support Vector Machines': SVC(random_state=42)
    }

    if st.button('Evaluate'):
        x = data_encoded.drop(columns=['Feedback'], axis=1)
        y = data_encoded['Feedback']
        x_smote, y_smote = balance_data(x, y)
        x_selected = x_smote[selected_features]
        x_train, x_test, y_train, y_test = train_test_split(x_selected, y_smote, test_size=0.2, random_state=42)
        
        # Evaluate models
        results = {}
        for name, model in models.items():
            model.fit(x_train, y_train)
            y_pred = model.predict(x_test)
            accuracy = accuracy_score(y_test, y_pred)
            results[name] = accuracy

        # Display results
        col1, col2, col3 = st.columns(3)
        col1.metric("Decision Tree Accuracy", f"{results['Decision Tree']*100:.2f}%")
        col2.metric("Random Forest Accuracy", f"{results['Random Forest']*100:.2f}%")
        col3.metric("SVM Accuracy", f"{results['Support Vector Machines']*100:.2f}%")
