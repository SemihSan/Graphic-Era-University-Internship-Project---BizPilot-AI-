# Lead Scoring Baseline Report

Bu rapor, BizPilot AI projesinin 1. hafta dataset hazırlığı için oluşturulan ilk Logistic Regression baseline sonucudur.

## Dataset Özeti

- Raw dataset satır/sütun sayısı: `9240` satır, `37` sütun
- Temizlenmiş dataset satır/sütun sayısı: `7484` satır, `28` sütun
- Hedef kolon: `Converted`
- Pozitif sınıf anlamı: lead müşteriye dönüştü

## Temizleme Kararları

- `Select` değerleri eksik veri olarak işaretlendi.
- ID kolonları modelden çıkarıldı.
- Manuel kalite etiketi veya önceki skor çıktısı olabilecek kolonlar çıkarıldı.
- Eksik hedef değeri olan satırlar çıkarıldı.

Çıkarılan kolonlar:

- `Prospect ID`
- `Lead Number`
- `Tags`
- `Lead Quality`
- `Lead Profile`
- `Asymmetrique Activity Index`
- `Asymmetrique Profile Index`
- `Asymmetrique Activity Score`
- `Asymmetrique Profile Score`

## Eksik Değer Özeti

- `How did you hear about X Education`: `5494` eksik değer
- `City`: `1984` eksik değer
- `What matters most to you in choosing a course`: `1921` eksik değer
- `What is your current occupation`: `1902` eksik değer
- `Specialization`: `1802` eksik değer
- `Country`: `711` eksik değer
- `Page Views Per Visit`: `136` eksik değer
- `TotalVisits`: `136` eksik değer
- `Last Activity`: `102` eksik değer
- `Lead Source`: `23` eksik değer

## Model

- Model: scikit-learn Logistic Regression
- Train/test split: 80/20, stratified
- Numeric kolonlar: median imputation + standard scaling
- Categorical kolonlar: most frequent imputation + one-hot encoding

## Sonuçlar

- Accuracy: `0.7902`
- Precision: `0.7261`
- Recall: `0.7555`
- F1: `0.7405`
- ROC-AUC: `0.8703`

## Classification Report

```text
              precision    recall  f1-score   support

           0       0.84      0.81      0.82       904
           1       0.73      0.76      0.74       593

    accuracy                           0.79      1497
   macro avg       0.78      0.78      0.78      1497
weighted avg       0.79      0.79      0.79      1497

```

## Pozitif Dönüşümü Artıran İlk Sinyaller

- `cat__Lead Origin_Lead Add Form`: `2.2730`
- `cat__What is your current occupation_Working Professional`: `1.4245`
- `cat__Last Notable Activity_infrequent_sklearn`: `1.2056`
- `num__Total Time Spent on Website`: `1.1186`
- `cat__Lead Source_Olark Chat`: `0.9949`
- `cat__Last Notable Activity_SMS Sent`: `0.8296`
- `cat__Do Not Email_No`: `0.8269`
- `cat__Last Activity_infrequent_sklearn`: `0.6264`
- `cat__Last Activity_SMS Sent`: `0.6035`
- `cat__Digital Advertisement_No`: `0.5665`

## Pozitif Dönüşümü Azaltan İlk Sinyaller

- `cat__What is your current occupation_Unemployed`: `-1.1530`
- `cat__Lead Origin_Landing Page Submission`: `-1.0636`
- `cat__Do Not Email_Yes`: `-0.7543`
- `cat__What is your current occupation_Student`: `-0.6879`
- `cat__Lead Origin_API`: `-0.6518`
- `cat__Last Notable Activity_Modified`: `-0.5993`
- `cat__Last Notable Activity_Olark Chat Conversation`: `-0.5925`
- `cat__Last Activity_Converted to Lead`: `-0.5299`
- `cat__Digital Advertisement_infrequent_sklearn`: `-0.4938`
- `cat__Lead Origin_infrequent_sklearn`: `-0.4850`

## Not

Bu baseline, 1. hafta teslimi için dataset'in hazırlanabildiğini ve lead scoring modelinin kurulabildiğini göstermek amacıyla hazırlanmıştır.