#! /u/sw/toolchains/gcc-glibc/11.2.0/base/bin/python

import requests
import hashlib
import email
import html2text
from urlextract import URLExtract
import os
from dotenv import load_dotenv

load_dotenv()

API_DOMAINS_URLS = "https://privatix-temp-mail-v1.p.rapidapi.com/request/domains/"
HEADERS = {"x-rapidapi-host": "privatix-temp-mail-v1.p.rapidapi.com",
                "x-rapidapi-key": os.getenv("X-RAPIDAPI-KEY")} # Your API key from .env file  
LOCAL_PART = "danieleferrario"

def get_current_mailbox():
    response = requests.get(API_DOMAINS_URLS, headers=HEADERS)
    domains = response.json()
    domain = domains[0]
    email_address = f"{LOCAL_PART}{domain}"
    encoded_email = hashlib.md5(email_address.encode()).hexdigest()
    return {"plain": email_address, "encoded": encoded_email}

def fetch_last_mail(mailbox, id):
    response = requests.get(f"https://privatix-temp-mail-v1.p.rapidapi.com/request/mail/id/{mailbox}/", headers=HEADERS)
    mails_number = len(response.json())

    if id > mails_number:
        raise ValueError("The number of mails is less than the one you entered: " + str(mails_number))

    last_mail = response.json()[-id]
    msg = email.message_from_string(last_mail['mail_html'])
    sender = email.message_from_string(last_mail['mail_from']).get_payload()
    subject = email.message_from_string(last_mail['mail_subject']).get_payload()
    parsed_msg = html2text.html2text(msg.get_payload())
    
    extractor = URLExtract()
    urls = extractor.find_urls(parsed_msg)
    return sender, subject, parsed_msg, urls

def print_mail_essentials(sender, subject, urls):
    print("SENDER: "+ sender + "\n")
    print("SUBJECT: "+ subject + "\n")
    print("URLS:\n")
    for url in urls:
        print(url)

def print_mail_text(parsed_msg):
    print("MAIL TEXT:\n")
    print(parsed_msg) 
    

def main():
    mailbox = get_current_mailbox()
    print("USING APIKEY: " + HEADERS['x-rapidapi-key'] + "\n")
    print("USING MAILBOX: " + mailbox['plain'] + "\n")
    id = input("Enter the i-latest mail or q to quit (1 is the latest): ")
    while id != "q":
        try:
            sender, subject, parsed_msg, urls = fetch_last_mail(mailbox['encoded'], int(id))
            print_mail_essentials(sender, subject, urls)
            print_mail = input("Do you want to print the mail text? (y/n): ")
            if print_mail == "y":
                print_mail_text(parsed_msg) 
        except ValueError as e:
            print(e)

        id = input("Enter the i-latest mail or q to quit (1 is the latest): ")

if __name__ == "__main__":
    main()

