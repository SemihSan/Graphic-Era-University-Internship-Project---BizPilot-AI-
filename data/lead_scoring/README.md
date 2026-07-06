# Lead Scoring Dataset Plan / Lead Scoring Dataset Planı

## English

The lead-scoring module uses a public Kaggle lead-scoring dataset and trains a Logistic Regression baseline model, as required by the professor. XGBoost remains an optional improvement model for later stages.

### Candidate Datasets

Primary dataset:

- Name: Lead Scoring Dataset
- Source: Kaggle
- URL: https://www.kaggle.com/datasets/amritachatterjee09/lead-scoring-dataset

Fallback dataset:

- Name: Leads Dataset
- Source: Kaggle
- URL: https://www.kaggle.com/datasets/ashydv/leads-dataset

### Selection Criteria

The selected dataset should:

- contain inbound or marketing lead records,
- contain a binary conversion target such as `Converted`,
- include useful lead features such as source, activity level, visits, company profile, geography, interest level, or engagement,
- have enough records for a train/test split,
- be cleanable without private business data.

### Preparation Status

1. Download selected Kaggle dataset into `data/lead_scoring/raw/`: done.
2. Inspect columns, target labels, missing values, duplicates, and class balance: done.
3. Remove ID columns and likely leakage columns: done.
4. Encode categorical features: done in the scikit-learn pipeline.
5. Scale numeric features for Logistic Regression: done in the scikit-learn pipeline.
6. Split into train/test sets: done.
7. Train Logistic Regression as the Week 1 baseline: done.
8. Save cleaned data into `data/lead_scoring/processed/`: done locally.
9. Record accuracy, precision, recall, F1, and ROC-AUC: done.
10. Document positive and negative signals for explainability: done.

### Week 1 Baseline Result

Script:

- `src/lead_scoring_baseline.py`

Generated local outputs:

- `data/lead_scoring/processed/lead_scoring_cleaned.csv`
- `models/lead_scoring_logreg.joblib`
- `reports/lead_scoring_baseline.md`
- `src/lead_scoring_predictor.py`

Metrics:

- Accuracy: 0.7902
- Precision: 0.7261
- Recall: 0.7555
- F1: 0.7405
- ROC-AUC: 0.8703

Interpretation:

The first Logistic Regression baseline is sufficient for the Week 1 dataset-ready deliverable. It proves that the dataset can be cleaned, modeled, and used as the starting point for the lead qualification module.

### Prediction Wrapper

`src/lead_scoring_predictor.py` loads the trained model and scores a single new lead.

Example command:

```powershell
.venv\Scripts\python src\lead_scoring_predictor.py
```

The output includes:

- ML conversion probability
- ML score out of 100
- rule-based adjustment
- final hybrid score out of 100
- potential label
- short explanation

### Planned Hybrid Score

Final lead score = ML conversion probability + rule-based adjustment.

Example rule-based signals:

- positive adjustment for business email domains,
- positive adjustment for high website engagement,
- positive adjustment for enterprise company size or strong buying intent,
- negative adjustment for incomplete contact information,
- negative adjustment for low engagement or irrelevant industry.

The LLM will explain the score using model probability, rule signals, and retrieved company context.

## Türkçe

Lead-scoring modülü, profesörün belirttiği gereksinime uygun olarak public bir Kaggle lead-scoring dataset kullanır ve Logistic Regression baseline modeli eğitir. XGBoost ilerleyen aşamalar için opsiyonel iyileştirme modeli olarak bırakılmıştır.

### Aday Datasetler

Birincil dataset:

- Ad: Lead Scoring Dataset
- Kaynak: Kaggle
- URL: https://www.kaggle.com/datasets/amritachatterjee09/lead-scoring-dataset

Yedek dataset:

- Ad: Leads Dataset
- Kaynak: Kaggle
- URL: https://www.kaggle.com/datasets/ashydv/leads-dataset

### Seçim Kriterleri

Seçilen dataset şunları sağlamalıdır:

- inbound veya marketing lead kayıtları içermeli,
- `Converted` gibi binary conversion hedef kolonu içermeli,
- source, activity level, visits, company profile, geography, interest level veya engagement gibi faydalı lead özellikleri içermeli,
- train/test split için yeterli kayıt sayısına sahip olmalı,
- özel şirket verisi gerektirmeden temizlenebilir olmalı.

### Hazırlık Durumu

1. Seçilen Kaggle dataset'i `data/lead_scoring/raw/` içine indirme: tamamlandı.
2. Kolonları, hedef etiketi, eksik değerleri, duplicate kayıtları ve class balance durumunu inceleme: tamamlandı.
3. ID kolonlarını ve leakage riski taşıyan kolonları çıkarma: tamamlandı.
4. Kategorik özellikleri encode etme: scikit-learn pipeline içinde tamamlandı.
5. Logistic Regression için sayısal özellikleri scale etme: scikit-learn pipeline içinde tamamlandı.
6. Train/test split yapma: tamamlandı.
7. Week 1 baseline olarak Logistic Regression eğitme: tamamlandı.
8. Temizlenmiş veriyi `data/lead_scoring/processed/` içine lokal olarak kaydetme: tamamlandı.
9. Accuracy, precision, recall, F1 ve ROC-AUC metriklerini kaydetme: tamamlandı.
10. Explainability için pozitif ve negatif sinyalleri dokümante etme: tamamlandı.

### Week 1 Baseline Sonucu

Script:

- `src/lead_scoring_baseline.py`

Oluşan lokal çıktılar:

- `data/lead_scoring/processed/lead_scoring_cleaned.csv`
- `models/lead_scoring_logreg.joblib`
- `reports/lead_scoring_baseline.md`
- `src/lead_scoring_predictor.py`

Metrikler:

- Accuracy: 0.7902
- Precision: 0.7261
- Recall: 0.7555
- F1: 0.7405
- ROC-AUC: 0.8703

Yorum:

İlk Logistic Regression baseline modeli Week 1 dataset-ready teslimi için yeterlidir. Dataset'in temizlenebildiğini, modellenebildiğini ve lead qualification modülü için başlangıç noktası olarak kullanılabildiğini göstermektedir.

### Prediction Wrapper

`src/lead_scoring_predictor.py` eğitilmiş modeli yükler ve tek bir yeni lead için skor üretir.

Örnek komut:

```powershell
.venv\Scripts\python src\lead_scoring_predictor.py
```

Çıktı şunları içerir:

- ML conversion probability
- 100 üzerinden ML skoru
- rule-based adjustment
- 100 üzerinden final hybrid score
- potential label
- kısa açıklama

### Planlanan Hybrid Score

Final lead score = ML conversion probability + rule-based adjustment.

Örnek rule-based sinyaller:

- business email domain için pozitif düzeltme,
- yüksek website engagement için pozitif düzeltme,
- enterprise company size veya güçlü buying intent için pozitif düzeltme,
- eksik iletişim bilgisi için negatif düzeltme,
- düşük engagement veya alakasız industry için negatif düzeltme.

LLM, model olasılığını, rule sinyallerini ve retrieved company context bilgisini kullanarak skoru doğal dilde açıklayacaktır.
