import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report
import joblib
df = pd.read_csv(r'email_csv\emails_for_labeling.csv' , encoding= 'utf-8-sig')

df = df[df['label'].notna() & (df['label'] != "")]
if "text" not in df.columns:
    df["text"] = df["subject"].fillna("") + " " + df["body"].fillna("")

# ✅ NaN 방지: 전부 문자열로 통일
df["text"] = df["text"].fillna("").astype(str)
print(len(df))
print(df[['text', 'label']].head())

x = df['text']
y= df['label']

X_train , X_test , y_train  , y_test = train_test_split(
    x, y,
    test_size= 0.2,
    random_state= 42,
    stratify=y if len(df['label'].unique()) > 1 else None,
)

clf = Pipeline([
    ("tfidf", TfidfVectorizer(
        max_features=5000,
        ngram_range=(1, 2),    # unigram + bigram
    )),
    ("logreg", LogisticRegression(
        max_iter=1000,
        n_jobs=-1
    ))
])

# 5) 학습
print("\n=== 모델 학습 중 ===")
clf.fit(X_train, y_train)

# 6) 테스트 평가
print("\n=== 테스트 셋 평가 ===")
y_pred = clf.predict(X_test)
print(classification_report(y_test, y_pred))

# 7) 새 메일 예시로 테스트
test_texts = [
    "결제 내역이 확인되지 않습니다. 카드 청구서 다시 보내주세요.",
    "보안 경고: 새로운 장치에서 로그인했습니다.",
    "10% 할인 이벤트 소식 전해드립니다!"
]

print("\n=== 새 메일 예측 ===")
for t in test_texts:
    label = clf.predict([t])[0]
    print(f"[{label}] {t}")
    
    
joblib.dump(clf , "models/email_classifier.joblib")
print('모델 저장 완료 ')