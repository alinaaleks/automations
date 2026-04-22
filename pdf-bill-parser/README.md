# 📄 PDF-парсер коммунальных квитанций / Utility Bill Parser

---

## 🇷🇺 Описание

Этот проект автоматически извлекает данные из PDF-квитанций разных поставщиков коммунальных услуг и формирует единый структурированный файл для анализа.

### 🔧 Что делает:

- Читает PDF-файлы из папки с квитанциями
- Определяет тип поставщика услуги (электроэнергия, вода, ТКО и др.)
- Извлекает ключевые данные:
  - объём потребления
  - тариф
  - начисленная сумма
- Объединяет данные в единый CSV и Excel файл

### 📊 Результат:

- `output_data.csv`
- `output_data.xlsx`

### 🛠 Технологии:

- Python
- pdfplumber
- pandas

---

## 🇬🇧 Description

This project automatically extracts data from PDF utility bills from different providers and converts it into a unified structured dataset for analysis.

### 🔧 What it does:

- Reads PDF bills from a folder
- Detects utility provider type (electricity, water, waste, etc.)
- Extracts key information:
  - consumption volume
  - tariff rate
  - billed amount
- Combines everything into a single CSV and Excel file

### 📊 Output:

- `output_data.csv`
- `output_data.xlsx`

### 🛠 Tech stack:

- Python
- pdfplumber
- pandas
