# Lead Scoring Baseline Report / Lead Scoring Baseline Raporu

## English

This report summarizes the first Logistic Regression baseline created for the Week 1 dataset preparation of BizPilot AI.

### Dataset Summary

- Raw dataset size: `9240` rows, `37` columns
- Cleaned dataset size: `7484` rows, `28` columns
- Target column: `Converted`
- Positive class meaning: the lead converted into a customer

### Cleaning Decisions

- `Select` values were treated as missing values.
- ID columns were removed.
- Manual quality labels or previous scoring outputs were removed to reduce leakage risk.
- Rows with missing target values were removed.

Removed columns:

- `Prospect ID`
- `Lead Number`
- `Tags`
- `Lead Quality`
- `Lead Profile`
- `Asymmetrique Activity Index`
- `Asymmetrique Profile Index`
- `Asymmetrique Activity Score`
- `Asymmetrique Profile Score`

### Missing Value Summary

- `How did you hear about X Education`: `5494` missing values
- `City`: `1984` missing values
- `What matters most to you in choosing a course`: `1921` missing values
- `What is your current occupation`: `1902` missing values
- `Specialization`: `1802` missing values
- `Country`: `711` missing values
- `Page Views Per Visit`: `136` missing values
- `TotalVisits`: `136` missing values
- `Last Activity`: `102` missing values
- `Lead Source`: `23` missing values

### Model

- Model: scikit-learn Logistic Regression
- Train/test split: 80/20, stratified
- Numeric columns: median imputation + standard scaling
- Categorical columns: most frequent imputation + one-hot encoding

### Results

- Accuracy: `0.7902`
- Precision: `0.7261`
- Recall: `0.7555`
- F1: `0.7405`
- ROC-AUC: `0.8703`

### Classification Report

```text
              precision    recall  f1-score   support

           0       0.84      0.81      0.82       904
           1       0.73      0.76      0.74       593

    accuracy                           0.79      1497
   macro avg       0.78      0.78      0.78      1497
weighted avg       0.79      0.79      0.79      1497
```

### Top Signals Increasing Conversion

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

### Top Signals Decreasing Conversion

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

### Note

This baseline proves that the dataset can be prepared and that the lead scoring model can be trained for the Week 1 deliverable. It is not the final model; it is the first working baseline.

## Türkçe

Bu rapor, BizPilot AI projesinin Week 1 dataset hazırlığı için oluşturulan ilk Logistic Regression baseline sonucunu özetler.

### Dataset Özeti

- Raw dataset boyutu: `9240` satır, `37` sütun
- Temizlenmiş dataset boyutu: `7484` satır, `28` sütun
- Hedef kolon: `Converted`
- Pozitif sınıf anlamı: lead müşteriye dönüştü

### Temizleme Kararları

- `Select` değerleri eksik veri olarak kabul edildi.
- ID kolonları çıkarıldı.
- Manuel kalite etiketi veya önceki scoring çıktısı olabilecek kolonlar leakage riskini azaltmak için çıkarıldı.
- Hedef değeri eksik olan satırlar çıkarıldı.

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

### Eksik Değer Özeti

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

### Model

- Model: scikit-learn Logistic Regression
- Train/test split: 80/20, stratified
- Sayısal kolonlar: median imputation + standard scaling
- Kategorik kolonlar: most frequent imputation + one-hot encoding

### Sonuçlar

- Accuracy: `0.7902`
- Precision: `0.7261`
- Recall: `0.7555`
- F1: `0.7405`
- ROC-AUC: `0.8703`

### Classification Report

```text
              precision    recall  f1-score   support

           0       0.84      0.81      0.82       904
           1       0.73      0.76      0.74       593

    accuracy                           0.79      1497
   macro avg       0.78      0.78      0.78      1497
weighted avg       0.79      0.79      0.79      1497
```

### Pozitif Dönüşümü Artıran İlk Sinyaller

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

### Pozitif Dönüşümü Azaltan İlk Sinyaller

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

### Not

Bu baseline, Week 1 teslimi için dataset'in hazırlanabildiğini ve lead scoring modelinin eğitilebildiğini gösterir. Final model değildir; ilk çalışan baseline modelidir.
