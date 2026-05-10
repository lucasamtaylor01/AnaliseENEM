# 📊 ENEM Score Analysis: 2015–2023

## 📝 Description
The National High School Exam (ENEM) is a non-mandatory, standardized Brazilian national exam that evaluates high school students. It is the most important exam of its kind in Brazil and the second largest in the world by number of candidates, behind only China's national college entrance exam.
ENEM is also used to apply for scholarships at private universities through ProUni or student loans via FIES. In many universities, it has gradually replaced the traditional vestibular as the main form of college admission. [Available on wikipedia.](https://en.wikipedia.org/wiki/Exame_Nacional_do_Ensino_M%C3%A9dio)

This repository contains data processing and analysis of ENEM scores from 2015 to 2023, broken down by municipality and state (UF).
We applied clustering techniques to group municipalities with similar performance profiles, identifying regional patterns. We also built a scatter plot to analyze the relationship between scores and family income.

## ⚙️ Installation
1. Clone the repository
   ```bash
   git clone https://github.com/lucasamtaylor01/enem.git
   ```

2. Install dependencies

   **Linux/macOS:**
   ```bash
   python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
   ```
   **Windows (PowerShell)**
   ```bash
   python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt
   ```

3. Run `main.py`

## ⚠️ Warning
The data used in this project is public and can be obtained from the official INEP website:
https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/enem

Due to the large volume, the files are not included in this repository. To run the project, you must manually download the microdata and organize it according to the structure expected by the code. The data is anonymized and must be used with proper source attribution, in compliance with applicable legislation (LGPD).

## 🤝 Contributing
Contributions are welcome. If you find errors, inconsistencies, or have suggestions for improvement, feel free to open an issue or submit a pull request.

## 📄 License

The code in this repository is licensed under the terms of the [MIT License](LICENSE). The data, in turn, is derived from public INEP sources and is not covered by the MIT License — it remains subject to the terms of use defined by the responsible agency.

## 🤖 Ethical AI Use
This project was developed with the help of [GitHub Copilot](https://github.com/features/copilot).

## 📚 Documentation
The full project documentation is available on the wiki: [https://github.com/lucasamtaylor01/enem/wiki](https://github.com/lucasamtaylor01/enem/wiki)
