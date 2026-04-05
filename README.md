# Axial Length Tracker

## Overview
The **Axial Length Tracker** web app is designed to facilitate eye care professionals in tracking and managing the axial lengths of patients' eyes over time. This application provides an intuitive interface for users to record, analyze, and visualize axial length data efficiently.

## Key Features
- **Patient Profile Management**: Store and manage patient information and measurement history.
- **Data Entry**: Simple forms to input axial length measurements (OS and OD) for different patient ages.
- **Data Visualization**: Interactive graphs and charts to visualize changes in axial lengths over time for individual patients.
- **PDF Reports Generation**: Ability to download measurement charts as PDF reports for clinical records.
- **Growth Chart Reference**: Built-in clinical reference data for male and female axial length growth patterns by age and percentile.

## Technologies Used
- **Frontend**: Streamlit
- **Backend**: Python
- **Visualization Library**: Plotly
- **Data Processing**: Pandas

## Installation
To set up the Axial Length Tracker locally:

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/xixicyll/axial-length-tracker.git
   ```
2. Navigate to the project directory:
   ```bash
   cd axial-length-tracker
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the application:
   ```bash
   streamlit run app.py
   ```

## Usage
After successfully starting the application, Streamlit will automatically open your browser to the application URL (typically `http://localhost:8501`). From there, you can:
- Enter patient information in the sidebar
- Input axial length measurements for both eyes (OS and OD)
- View the growth chart with clinical reference percentiles
- Download PDF reports of the measurements

## Contribution
Contributions are welcome! Please feel free to submit a pull request or open an issue for suggestions and improvements.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Author
Developed by xixicyll

## Date
Last updated on 2026-04-05
