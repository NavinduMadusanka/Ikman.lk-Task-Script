import requests
from bs4 import BeautifulSoup
import csv
import pandas as pd
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import smtplib

# Function to search for the motorcycle model "CT-100" and capture the required information
def scrape_data():
    url = "https://www.ikman.lk/en/vehicles/motorcycles/bajaj?q="
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    data_list = []
    for ad in soup.find_all("div", class_="col-md-8 ad-item-info")[:50]:
        location = ad.find("h4", class_="ad-location").text.strip()
        price = ad.find("span", class_="price").text.strip().replace(",", "")
        year_of_manufacture = ad.find("div", class_="ad-item-meta")\
            .find("div", class_="row meta-item").text.strip().split("\n")[1].strip() if ad.find("div", class_="ad-item-meta") else ""
        mileage = ad.find("li", string=lambda text: "Mileage" in text.string)\
            .find_next("span", class_="ad-detail").text.strip() if ad.find("li", string=lambda text: "Mileage" in text.string) else ""

        data_list.append([location, price, year_of_manufacture, mileage])

    return data_list

# Function to calculate the average vehicle price by location
def calculate_average_price(data):
    grouped_data = data.groupby("Location").filter(lambda x: len(x) > 1)
    grouped_data = grouped_data.groupby("Location").mean().reset_index()
    return grouped_data

# Generate the CSV file and send the email
def send_email(grouped_data, data):
    df = pd.DataFrame(data, columns=["Location", "Price", "Year of Manufacture", "Mileage"])
    df.to_csv("output.csv", index=False)

    msg = MIMEMultipart()
    msg['From'] = 'your_email@example.com'
    msg['To'] = 'recipient_email@example.com'
    msg['Subject'] = 'CT-100 Motorcycle Details'

    body = "Here is the average vehicle price by location:\n\n"
    for index, row in grouped_data.iterrows():
        body += f"{row['Location']}: {row['Price']}\n"

    msg.attach(MIMEText(body))

    with open('output.csv', "rb") as f:
        part = MIMEApplication(f.read(), _subtype="csv")
        part.add_header('content-disposition', 'attachment', filename="output.csv")
        msg.attach(part)

    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.starttls()
        smtp.login('your_email@example.com', 'your_password')
        smtp.send_message(msg)

if __name__ ==