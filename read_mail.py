import imaplib
import email
from email.header import decode_header
from dotenv import load_dotenv
import os
import re
import pandas as pd
import joblib
from utils.email_parser import parse_email 
load_dotenv()

def clean_code(text : str) -> str:
    if text is None:
        return ""
    text= text.replace("\r", " ").replace("\n", " ").replace("\t"," ")
    text = re.sub(r"\s+"," ", text)
    return text.strip()



IMAP_HOST = os.getenv("IMAP_HOST")
print(repr(IMAP_HOST))
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv('gmail_pw')

# model load
clf = joblib.load('models/email_classifier.joblib')

mail = imaplib.IMAP4_SSL(IMAP_HOST)
ret = mail.login(EMAIL, PASSWORD)
# print("LOGIN RESULT:", ret)

mail.select("INBOX")

status, data = mail.search(None , 'ALL')

if status != "OK":
    print("메일검색 실패: ", status)
else:
    mail_ids = data[0].split()
    print('총 메일 개수', len(mail_ids))
    latest_10 = mail_ids[-30:]
    
    emails = []
    for mid in reversed(latest_10):
        status , msg_data = mail.fetch(mid,'(RFC822)')
        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)
        
        record = parse_email(msg)
        
    
    print("메일 수집 완료")
    # for e in emails:
    #     print(e['id'] , e['subject'])
    # print("본문 일부:")
    # print(body_text[:200].replace("\n", " "))
    # print()
    df = pd.DataFrame(emails)
    
    #학습용 코드 추후 주석처리 
    df['text'] = df['subject'].fillna("") + " " + df['body'].fillna("")
    
    df.to_csv("email_csv/emails_for_labeling.csv" , index =False , encoding='utf-8-sig')
    print("저장완료 ")
    
mail.logout()