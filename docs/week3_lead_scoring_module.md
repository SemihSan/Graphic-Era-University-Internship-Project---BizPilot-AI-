# Week 3 Lead Scoring Module / 3. Hafta Lead Scoring Modülü

## English

Week 3 task:

- Dates: 20 July - 26 July 2026
- Goal: train the lead-scoring ML model, integrate it with an LLM for natural language explanations, and connect it to a sample CRM-style dataset
- Deliverable: integrated lead scoring module
- Due date: Sunday, 26 July 2026

### Current Status

The project already has a trained Logistic Regression baseline from Week 1:

```text
src/lead_scoring_baseline.py
```

The prediction wrapper is implemented in:

```text
src/lead_scoring_predictor.py
```

The module combines:

- ML conversion probability from the trained Logistic Regression pipeline
- rule-based adjustments for business signals such as email permission, lead origin, occupation, website visits, time spent, and page views
- final 0-100 score
- priority label
- natural language explanation

### Week 3 Additions

New CRM-style sample dataset:

```text
data/crm_sample_leads/crm_leads_sample.csv
```

New batch scoring script:

```text
src/lead_scoring_batch.py
```

New optional LLM explanation layer:

```text
src/lead_scoring_llm_explainer.py
```

Streamlit prompt input:

```text
Lead Qualification tab
```

The Streamlit Lead Qualification screen supports two separate input modes: standalone natural-language lead prompt scoring and structured CRM field scoring. In prompt-only mode, the user does not need to fill the structured form. The prompt parser extracts known fields such as lead origin, lead source, email permission, occupation, visits, website time, page views, and last activity.

The LLM layer uses the normal OpenAI API with `OPENAI_MODEL=gpt-5.4`. If OpenAI is not configured or the request fails, the module falls back to a deterministic template explanation so the prototype still works locally.

Verified: the OpenAI explanation layer was tested end-to-end in both the Streamlit Lead Qualification tab and the CRM batch script, and it returns `explanation_provider=openai`. Note: any `HTTP_PROXY` / `HTTPS_PROXY` values in `.env` must point to a reachable proxy, otherwise requests time out and the module silently falls back to the template explanation. When no proxy is needed, keep those lines commented out. After editing `.env`, restart Streamlit so the new environment is loaded.

### Run Baseline Training

```powershell
.venv\Scripts\python src\lead_scoring_baseline.py
```

### Run Single Lead Prediction

```powershell
.venv\Scripts\python src\lead_scoring_predictor.py
```

### Run CRM Batch Scoring

```powershell
.venv\Scripts\python src\lead_scoring_batch.py
```

Optional LLM explanation mode:

```powershell
$env:OPENAI_API_KEY="your_api_key"
$env:OPENAI_MODEL="gpt-5.4"
.venv\Scripts\python src\lead_scoring_batch.py --llm
```

### Output

The batch script writes:

```text
data/crm_sample_leads/scored_crm_leads.csv
```

The output includes the original CRM-style lead fields plus:

- ML probability
- ML base score
- rule-based adjustment
- final score
- priority label
- explanation
- explanation provider

Verified local batch result:

```text
Rows scored: 8
Average final score: 73.25
High priority leads: 5
```

## Türkçe

3. hafta görevi:

- Tarihler: 20 Temmuz - 26 Temmuz 2026
- Hedef: lead-scoring ML modelini eğitmek, LLM ile doğal dil açıklaması entegre etmek ve sample CRM-style dataset ile bağlamak
- Teslim: entegre lead scoring modülü
- Son teslim tarihi: Pazar, 26 Temmuz 2026

### Mevcut Durum

Projede Week 1'den gelen eğitilmiş Logistic Regression baseline zaten var:

```text
src/lead_scoring_baseline.py
```

Prediction wrapper şu dosyada:

```text
src/lead_scoring_predictor.py
```

Modül şu parçaları birleştirir:

- eğitilmiş Logistic Regression pipeline'dan gelen ML conversion probability
- email permission, lead origin, occupation, website visits, time spent ve page views gibi business sinyallerine göre rule-based adjustment
- final 0-100 skor
- priority label
- doğal dil açıklaması

### 3. Hafta Eklenenler

Yeni CRM-style sample dataset:

```text
data/crm_sample_leads/crm_leads_sample.csv
```

Yeni batch scoring script:

```text
src/lead_scoring_batch.py
```

Yeni opsiyonel LLM açıklama katmanı:

```text
src/lead_scoring_llm_explainer.py
```

Streamlit prompt input:

```text
Lead Qualification tab
```

Streamlit Lead Qualification ekranı iki ayrı input modu destekler: standalone natural-language lead prompt scoring ve structured CRM field scoring. Prompt-only modda kullanıcı structured formu doldurmak zorunda değildir. Prompt parser; lead origin, lead source, email permission, occupation, visits, website time, page views ve last activity gibi bilinen alanları çıkarır.

LLM katmanı normal OpenAI API kullanır ve model olarak `OPENAI_MODEL=gpt-5.4` ayarlanır. OpenAI yapılandırılmamışsa veya istek başarısız olursa sistem deterministic template explanation'a düşer; böylece prototip lokal olarak çalışmaya devam eder.

Doğrulandı: OpenAI açıklama katmanı hem Streamlit Lead Qualification sekmesinde hem de CRM batch script'inde uçtan uca test edildi ve `explanation_provider=openai` döndürüyor. Not: `.env` içindeki `HTTP_PROXY` / `HTTPS_PROXY` değerleri erişilebilir bir proxy'ye işaret etmelidir; aksi halde istekler zaman aşımına uğrar ve modül sessizce template açıklamaya düşer. Proxy gerekmiyorsa bu satırları yorumda (comment) bırak. `.env`'i değiştirdikten sonra yeni ortamın yüklenmesi için Streamlit'i yeniden başlat.

### Baseline Model Eğitimi

```powershell
.venv\Scripts\python src\lead_scoring_baseline.py
```

### Tek Lead Prediction

```powershell
.venv\Scripts\python src\lead_scoring_predictor.py
```

### CRM Batch Scoring

```powershell
.venv\Scripts\python src\lead_scoring_batch.py
```

Opsiyonel LLM explanation modu:

```powershell
$env:OPENAI_API_KEY="your_api_key"
$env:OPENAI_MODEL="gpt-5.4"
.venv\Scripts\python src\lead_scoring_batch.py --llm
```

### Çıktı

Batch script şu dosyayı üretir:

```text
data/crm_sample_leads/scored_crm_leads.csv
```

Çıktı dosyasında orijinal CRM-style lead alanlarına ek olarak şunlar bulunur:

- ML probability
- ML base score
- rule-based adjustment
- final score
- priority label
- explanation
- explanation provider

Doğrulanan lokal batch sonucu:

```text
Rows scored: 8
Average final score: 73.25
High priority leads: 5
```
