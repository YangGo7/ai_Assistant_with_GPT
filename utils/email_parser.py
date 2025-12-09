from email.header import decode_header
from email.utils import parsedate_to_datetime
from bs4 import BeautifulSoup
import re


def decode_str(s :str) -> str:
    if not s:
        return ""
    value ,enc = decode_header(s)[0]
    if isinstance(value, bytes):
        return value.decode(enc or "utf-8", errors= 'ignore')
    return value


def clean_html(raw: str) -> str:
    if raw is None:
        return ""
    soup = BeautifulSoup(raw, "html.parser")
    text = soup.get_text(" ")
    text = text.replace("\r", " ").replace("\n", " ").replace("\t", " ") # 탈출 문자열 공백처리
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def parse_email(msg) -> dict:
    message_id = msg.get("Message-ID","") or msg.get("UID","") #  메일 ID 
    date_raw = msg.get("Date","") # 날짜
    from_raw = msg.get("From","") # 보낸이
    to_raw = msg.get("To","") #받는이 

    subject_raw = msg.get("Subject","")
    subject = decode_str(subject_raw)
    
    body_raw = ""
    if msg.is_multipart():
        for part in msg.walk():
            ctype = part.get_content_type()
            disp  = str(part.get("Content-Disposition", "")).lower()
            # 첨부파일은 나중에 따로 처리
            if "attachment" in disp:
                continue
            if ctype in ("text/plain", "text/html"):
                try:
                    payload = part.get_payload(decode=True)
                    if payload is None:
                        continue
                    body_raw = payload.decode(part.get_content_charset() or "utf-8",errors="ignore")
                    break
                except Exception:
                    continue
    else:
        try:
            payload = msg.get_payload(decode=True)
            if payload is not None:
                body_raw = payload.decode(msg.get_content_charset() or "utf-8",errors="ignore")
        except Exception:
            body_raw = ""

    body_text = clean_html(body_raw)
    
    try:
        dt = parsedate_to_datetime(date_raw)
        date_str = dt.isoformat()
    except Exception:
        date_str = ""
    
    
    text = (subject + "" + body_text).strip()
    
    return{
        "message_id": message_id,
        "date": date_str,
        "from": from_raw,
        "to": to_raw,
        "subject": subject,
        "body_raw": body_raw,
        "body_text": body_text,
        "text": text,
        "keywords": "",
        "label_manual": "", # manual 은 추후 제거 
        "label_predicted": "",
        "category_rule": "",
        "attachments": "",
        "source": "imap",
    }