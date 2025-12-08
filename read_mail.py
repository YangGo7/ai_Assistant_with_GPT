import imaplib
import email
from email.header import decode_header
from dotenv import load_dotenv
import os
load_dotenv()

IMAP_HOST = os.getenv("IMAP_HOST")
print(repr(IMAP_HOST))
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv('gmail_pw')
mail = imaplib.IMAP4_SSL(IMAP_HOST)
ret = mail.login(EMAIL, PASSWORD)
print("LOGIN RESULT:", ret)

mail.select("INBOX")

status, data = mail.search(None , 'ALL')

if status != "OK":
    print("메일검색 실패: ", status)
else:
    mail_ids = data[0].split()
    print('총 메일 개수', len(mail_ids))
    latest_10 = mail_ids[-10:]
    
    emails = []
    for mid in reversed(latest_10):
        status , msg_data = mail.fetch(mid,'(RFC822)')
        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)
        
        raw_subject = msg.get('Subject', "")
        subject , encoding = decode_header(raw_subject)[0]
        if isinstance(subject , bytes):
            subject = subject.decode(encoding or "utf-8", errors = 'ignore')
        # print("=" * 80)
        # print("mail ID:", mid.decode())
        # print("제목: ",subject)
        
        body_text = ""
        if msg.is_multipart():
            for part in msg.walk():
                ctype = part.get_content_type()
                if ctype == "text/plain":
                    try:
                        body_text =part.get_payload(decode = True).decode('utf-8', errors= 'ignore')
                    except Exception:
                        pass
                    break
        else:
            try:
                body_text = msg.get_payload(decode = True).decode('utf-8',errors = 'ignore')
            except Exception:
                pass
        emails.append({
            "id":mid.decode(),
            "subject": subject,
            "body": body_text,
        })
        
    
    print("메일 수집 완료")
    for e in emails:
        print(e['id'] , e['subject'])
    # print("본문 일부:")
    # print(body_text[:200].replace("\n", " "))
    # print()

mail.logout()