import requests
import time
import pandas as pd
import os
from io import StringIO
from datetime import datetime
from flask import Flask, render_template_string, send_file

# Flask app initialization
app = Flask(__name__)

url = "https://www.atmos.albany.edu/products/nysm/nysm_latest.csv"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://www.atmos.albany.edu/"
}

# File path for storing the CSV data
output_csv = "nysm_latest_data.csv"

def download_csv():
    """Download CSV from the provided URL."""
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.content
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")
        return None

def append_to_csv(data, file_path):
    """Append new data to the existing CSV file."""
    new_df = pd.read_csv(StringIO(data.decode('utf-8')))
    
    # If the CSV file exists, append new data
    if os.path.exists(file_path):
        new_df.to_csv(file_path, mode='a', header=False, index=False)
        print("CSV updated successfully!")
    else:
        new_df.to_csv(file_path, index=False)
        print("CSV created and data saved successfully!")

def reset_csv(file_path):
    """Reset the CSV file at midnight."""
    current_time = datetime.now()
    if current_time.hour == 0 and current_time.minute == 0:
        if os.path.exists(file_path):
            with open(file_path, 'w'):
                pass  # Reset file content
            print("CSV reset successfully at midnight!")

def run_loop(file_path):
    """Run the loop that fetches and appends the CSV data every 6 minutes."""
    while True:
        # Download the CSV data
        data = download_csv()
        
        if data:
            # Append the data to the CSV file
            append_to_csv(data, file_path)

        # Reset CSV at midnight
        reset_csv(file_path)
        
        # Wait for 6 minutes before downloading again
        time.sleep(360)  # 6 minutes = 360 seconds

@app.route('/')
def display_csv():
    """Render the CSV content in an HTML table."""
    if os.path.exists(output_csv):
        df = pd.read_csv(output_csv)
        # Convert the DataFrame to HTML for display
        html_table = df.to_html(classes='data', header="true", index=False)
    else:
        html_table = "<p>No data available.</p>"

    # HTML template with embedded CSV data
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>CSV Data</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
                background-color: #f4f4f4;
            }}
            .container {{
                width: 80%;
                margin: 0 auto;
                background-color: white;
                padding: 20px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            }}
            h1 {{
                text-align: center;
                color: #333;
            }}
            .csv-table {{
                max-height: 400px;
                overflow-y: scroll;
                margin-top: 20px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
            }}
            th, td {{
                padding: 8px;
                text-align: left;
                border: 1px solid #ddd;
            }}
            th {{
                background-color: #f2f2f2;
            }}
            .download-btn {{
                display: block;
                text-align: center;
                margin-top: 20px;
                padding: 10px 20px;
                background-color: #4CAF50;
                color: white;
                text-decoration: none;
                border-radius: 5px;
            }}
            .download-btn:hover {{
                background-color: #45a049;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>CSV Data</h1>
            <div class="csv-table">
                {html_table}
            </div>
            <a href="/download" class="download-btn">Click here to download the CSV file</a>
        </div>
    </body>
    </html>
    """
    return render_template_string(html_content)

@app.route('/download')
def download_csv_file():
    """Allow users to download the CSV file."""
    if os.path.exists(output_csv):
        return send_file(output_csv, as_attachment=True)
    else:
        return "No file available for download."

if __name__ == '__main__':
    # Start the loop in the background
    import threading
    thread = threading.Thread(target=run_loop, args=(output_csv,))
    thread.daemon = True  # This will allow the thread to exit when the main program ends
    thread.start()

    # Start Flask app
    app.run(debug=True, use_reloader=False)
