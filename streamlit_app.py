import streamlit as st
import pandas as pd
from openai import OpenAI
import markdown
from io import StringIO
import os
import requests
from requests.auth import HTTPBasicAuth

# Set the page config at the beginning
st.set_page_config(
    page_title="Koalaflow - Your Helpful Content Generator",
    page_icon="https://example.com/favicon.ico",  # Replace with the URL of your favicon
    layout="centered",  # Optional: 'wide' or 'centered'
    initial_sidebar_state="auto"  # Optional: 'auto', 'expanded', 'collapsed'
)

st.title("🎈 Koala FAQ Generator ")

# Language selector dropdown
language = st.selectbox("Select Language / Sprache / Dil Seçin:", ("English", "German", "Turkish"))

# Function to return text based on selected language
def get_text(language):
    common_texts = {
        "English": {
            "how_it_works": """
## How it works
1. Enter your OpenAI API key.
2. Download the sample CSV file and expand the services under **Service**.
3. Upload your saved CSV file.
4. Choose how many FAQs you want to generate.
5. Select the model you want to use.
6. Click **Generate**.
7. After generation is complete, you can download the file.
8. Enter your WordPress Application Password and upload the FAQs directly to your WordPress site.
""",
            "api_key_prompt": "Enter your OpenAI API key:",
            "upload_prompt": "Choose a CSV file",
            "download_sample": "Download sample CSV",
            "num_faqs_prompt": "Number of FAQs to generate per topic:",
            "model_prompt": "Select the model to use:",
            "generate_button": "Generate FAQs",
            "error_message": "Please provide your OpenAI API key and upload a CSV file.",
            "limit_error": "The free version only allows up to 5 FAQs per topic.",
            "wp_url_prompt": "Enter your WordPress site URL:",
            "wp_user_prompt": "Enter your WordPress username:",
            "wp_password_prompt": "Enter your WordPress application password:",
            "post_type_prompt": "Select the type of post to create:",
            "upload_wp_button": "Upload FAQs to WordPress",
            "upload_success": "FAQs successfully uploaded to WordPress!",
            "upload_failure": "Failed to upload FAQs to WordPress. Please check your credentials and try again."
        },
        "German": {
            "how_it_works": """
## Wie es funktioniert
1. Geben Sie Ihren OpenAI API-Schlüssel ein.
2. Laden Sie die Beispiel-CSV-Datei herunter und erweitern Sie die Dienstleistungen unter **Leistungen**.
3. Laden Sie Ihre gespeicherte CSV-Datei wieder hoch.
4. Wählen Sie, wie viele FAQs Sie generieren möchten.
5. Wählen Sie das Modell, das Sie verwenden möchten.
6. Klicken Sie auf **Generieren**.
7. Nach Abschluss der Generierung können Sie die Datei herunterladen.
8. Geben Sie Ihr WordPress-Anwendungspasswort ein und laden Sie die FAQs direkt auf Ihre WordPress-Seite hoch.
""",
            "api_key_prompt": "Geben Sie Ihren OpenAI API-Schlüssel ein:",
            "upload_prompt": "Wählen Sie eine CSV-Datei",
            "download_sample": "Beispiel-CSV herunterladen",
            "num_faqs_prompt": "Anzahl der FAQs, die pro Thema generiert werden sollen:",
            "model_prompt": "Wählen Sie das zu verwendende Modell:",
            "generate_button": "FAQs generieren",
            "error_message": "Bitte geben Sie Ihren OpenAI API-Schlüssel ein und laden Sie eine CSV-Datei hoch.",
            "limit_error": "Die kostenlose Version erlaubt nur bis zu 5 FAQs pro Thema.",
            "wp_url_prompt": "Geben Sie Ihre WordPress-Site-URL ein:",
            "wp_user_prompt": "Geben Sie Ihren WordPress-Benutzernamen ein:",
            "wp_password_prompt": "Geben Sie Ihr WordPress-Anwendungspasswort ein:",
            "post_type_prompt": "Wählen Sie die Art des zu erstellenden Beitrags:",
            "upload_wp_button": "FAQs zu WordPress hochladen",
            "upload_success": "FAQs erfolgreich zu WordPress hochgeladen!",
            "upload_failure": "Hochladen der FAQs zu WordPress fehlgeschlagen. Bitte überprüfen Sie Ihre Anmeldeinformationen und versuchen Sie es erneut."
        },
        "Turkish": {
            "how_it_works": """
## Nasıl çalışır
1. OpenAI API anahtarınızı girin.
2. Örnek CSV dosyasını indirin ve **Hizmet** altında hizmetleri genişletin.
3. Kaydedilmiş CSV dosyanızı yükleyin.
4. Kaç adet SSS oluşturmak istediğinizi seçin.
5. Kullanmak istediğiniz modeli seçin.
6. **Oluştur** düğmesine tıklayın.
7. Oluşturma tamamlandıktan sonra dosyayı indirebilirsiniz.
8. WordPress Uygulama Parolanızı girin ve SSS'leri doğrudan WordPress sitenize yükleyin.
""",
            "api_key_prompt": "OpenAI API anahtarınızı girin:",
            "upload_prompt": "Bir CSV dosyası seçin",
            "download_sample": "Örnek CSV indir",
            "num_faqs_prompt": "Konu başına oluşturulacak SSS sayısı:",
            "model_prompt": "Kullanılacak modeli seçin:",
            "generate_button": "SSS Oluştur",
            "error_message": "Lütfen OpenAI API anahtarınızı girin ve bir CSV dosyası yükleyin.",
            "limit_error": "Ücretsiz sürüm, konu başına en fazla 5 SSS oluşturmaya izin verir.",
            "wp_url_prompt": "WordPress site URL'inizi girin:",
            "wp_user_prompt": "WordPress kullanıcı adınızı girin:",
            "wp_password_prompt": "WordPress uygulama parolanızı girin:",
            "post_type_prompt": "Oluşturulacak gönderi türünü seçin:",
            "upload_wp_button": "SSS'leri WordPress'e yükleyin",
            "upload_success": "SSS'ler başarıyla WordPress'e yüklendi!",
            "upload_failure": "SSS'leri WordPress'e yükleme başarısız oldu. Lütfen kimlik bilgilerinizi kontrol edin ve tekrar deneyin."
        }
    }
    return common_texts[language]

texts = get_text(language)

st.markdown(texts["how_it_works"])

# Input field for OpenAI API key
api_key = st.text_input(texts["api_key_prompt"], type="password")

# File uploader for CSV file
uploaded_file = st.file_uploader(texts["upload_prompt"], type="csv")

# Adding a download button for a sample CSV file
sample_file_path = "sample.csv"
if os.path.exists(sample_file_path):
    with open(sample_file_path, "r") as file:
        sample_csv = file.read()
    st.download_button(label=texts["download_sample"], data=sample_csv, file_name="sample.csv", mime="text/csv", key="sample_csv_download")
else:
    st.error("Sample CSV file not found. Please ensure 'sample.csv' is in the correct directory.")

# Number input for deciding how many FAQs to generate
num_faqs = st.number_input(texts["num_faqs_prompt"], min_value=1, max_value=10, value=5, step=1)

# Dropdown for selecting the model to use
model = st.selectbox(
    texts["model_prompt"],
    ("gpt-3.5-turbo", "gpt-4", "gpt-4-turbo")
)

# Button to generate FAQs
generate_button = st.button(texts["generate_button"])

# Function to generate questions based on the selected language
def generate_questions(api_key, leistung, num_faqs, model, language):
    client = OpenAI(api_key=api_key)
    try:
        if language == "English":
            user_message = f"Generate {num_faqs} FAQs (questions only) in English for the topic {leistung}. No introduction, only the questions."
        elif language == "German":
            user_message = f"Erstelle direkt {num_faqs} FAQs (nur die Fragen) auf Deutsch zu dem Thema {leistung}. Keine Einleitung, nur die Fragen."
        elif language == "Turkish":
            user_message = f"{num_faqs} adet ve {leistung} konusuyla ilgili olarak Türkçe dilinde Soru oluşturun. Giriş yok, sadece sorular."

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_message}
            ],
            max_tokens=1500,
            temperature=0.7,
        )
        generated_text = response.choices[0].message.content
        return generated_text.strip().split('\n')
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return []

# Function to generate answers based on the selected language
def generate_answers(api_key, question, leistung, model, language):
    client = OpenAI(api_key=api_key)
    try:
        if language == "English":
            user_message = f"Create a comprehensive answer in English for the following question on the topic {leistung}: {question}. Use Markdown and HTML formatting to improve readability. The answer should be at least 4-5 sentences long. No introduction, only the answer."
        elif language == "German":
            user_message = f"Erstelle direkt eine umfassende Antwort auf Deutsch für die folgende Frage zum Thema {leistung}: {question}. Verwende Markdown und HTML-Formatierungen, um die Lesbarkeit zu verbessern. Die Antwort sollte mindestens 4-5 Sätze lang sein. Keine Einleitung, nur die Antwort."
        elif language == "Turkish":
            user_message = f"Aşağıdaki soruya Türkçe dilinde {leistung} konusuyla ilgili olarak kapsamlı bir cevap oluşturun: {question}. Okunabilirliği artırmak için Markdown ve HTML biçimlendirmelerini kullanın. Cevap en az 4-5 cümle uzunluğunda olmalıdır. Giriş yok, sadece cevap."

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_message}
            ],
            max_tokens=3500,
            temperature=0.7,
        )
        generated_text = response.choices[0].message.content
        return markdown.markdown(generated_text.strip())
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return ""


# Function to check WordPress connection by creating a test draft post
def check_wordpress_connection(site_url, username, password):
    auth = HTTPBasicAuth(username, password)
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "title": "Test Post",
        "content": "This is a test post to check the WordPress connection.",
        "status": "draft"
    }
    response = requests.post(f"{site_url}/wp-json/wp/v2/posts", json=data, headers=headers, auth=auth)
    if response.status_code == 201:
        return True, response.status_code, response.text
    else:
        return False, response.status_code, response.text

def upload_to_wordpress(site_url, username, password, faqs, post_type):
    auth = HTTPBasicAuth(username, password)
    headers = {
        "Content-Type": "application/json"
    }
    success_count = 0

    for index, faq in faqs.iterrows():
        try:
            data = {
                "title": faq["Frage"],
                "content": faq["Antwort"],
                "status": "publish"
            }
            response = requests.post(f"{site_url}/wp-json/wp/v2/{post_type}", json=data, headers=headers, auth=auth)

            if response.status_code == 201:
                success_count += 1
            else:
                st.error(f"Failed to upload FAQ: {faq['Frage']} - Status code: {response.status_code}")
                st.error(f"Response: {response.text}")

        except Exception as e:
            st.error(f"Exception occurred while uploading FAQ: {faq['Frage']}")
            st.error(str(e))

    return success_count == len(faqs)

# Display WordPress settings and upload button only if the checkbox is selected
if upload_to_wordpress and 'faq_df' in st.session_state:
    st.markdown("### WordPress Settings")
    site_url = st.text_input(texts["wp_url_prompt"])
    wp_username = st.text_input(texts["wp_user_prompt"])
    wp_password = st.text_input(texts["wp_password_prompt"], type="password")
    post_type = st.selectbox(texts["post_type_prompt"], ("posts", "pages", "custom"))

    check_wp_button = st.button("Check WordPress Connection")

    if check_wp_button:
        if site_url and wp_username and wp_password:
            success, status_code, response_text = check_wordpress_connection(site_url, wp_username, wp_password)
            if success:
                st.success("Successfully connected to WordPress and created a test draft post!")
                upload_wp_button = st.button(texts["upload_wp_button"])
                if upload_wp_button:
                    if upload_to_wordpress(site_url, wp_username, wp_password, st.session_state['faq_df'], post_type):
                        st.success(texts["upload_success"])
                    else:
                        st.error(texts["upload_failure"])
            else:
                st.error(f"Failed to connect to WordPress. Status code: {status_code}. Response: {response_text}")
        else:
            st.error("Please provide your WordPress site URL, username, and application password.")


# Add a checkbox to show WordPress settings
upload_to_wp = st.checkbox("Upload to WordPress?", key="upload_to_wp_checkbox")

if upload_to_wp and 'faq_df' in st.session_state:
    st.markdown("### WordPress Settings")
    site_url = st.text_input(texts["wp_url_prompt"], key="wp_url_input")
    wp_username = st.text_input(texts["wp_user_prompt"], key="wp_user_input")
    wp_password = st.text_input(texts["wp_password_prompt"], type="password", key="wp_password_input")
    post_type = st.selectbox(texts["post_type_prompt"], ("posts", "pages", "custom"), key="post_type_select")

    check_wp_button = st.button("Check WordPress Connection", key="check_wp_button")

    if check_wp_button:
        if site_url and wp_username and wp_password:
            success, status_code, response_text = check_wordpress_connection(site_url, wp_username, wp_password)
            if success:
                st.success("Successfully connected to WordPress and created a test draft post!")
                upload_wp_button = st.button(texts["upload_wp_button"], key="upload_wp_button")
                if upload_wp_button:
                    if upload_to_wordpress(site_url, wp_username, wp_password, st.session_state['faq_df'], post_type):
                        st.success(texts["upload_success"])
                    else:
                        st.error(texts["upload_failure"])
            else:
                st.error(f"Failed to connect to WordPress. Status code: {status_code}. Response: {response_text}")
        else:
            st.error("Please provide your WordPress site URL, username, and application password.")

# Display the generated FAQs if available in session state
if 'faq_df' in st.session_state:
    st.write(st.session_state['faq_df'])
    
    # Option to download the result as a CSV file
    csv = st.session_state['faq_df'].to_csv(index=False)
    st.download_button(label="Download FAQs as CSV", data=csv, file_name="output_faqs.csv", mime="text/csv", key="faqs_csv_download")

# Display WordPress settings and upload button only if the checkbox is selected
if upload_to_wp and 'faq_df' in st.session_state:
    st.markdown("### WordPress Settings")
    site_url = st.text_input(texts["wp_url_prompt"])
    wp_username = st.text_input(texts["wp_user_prompt"])
    wp_password = st.text_input(texts["wp_password_prompt"], type="password")
    post_type = st.selectbox(texts["post_type_prompt"], ("posts", "pages", "custom"))

    check_wp_button = st.button("Check WordPress Connection")

    if check_wp_button:
        if site_url and wp_username and wp_password:
            success, status_code, response_text = check_wordpress_connection(site_url, wp_username, wp_password)
            if success:
                st.success("Successfully connected to WordPress and created a test draft post!")
                upload_wp_button = st.button(texts["upload_wp_button"])
                if upload_wp_button:
                    if upload_to_wordpress(site_url, wp_username, wp_password, st.session_state['faq_df'], post_type):
                        st.success(texts["upload_success"])
                    else:
                        st.error(texts["upload_failure"])
            else:
                st.error(f"Failed to connect to WordPress. Status code: {status_code}. Response: {response_text}")
        else:
            st.error("Please provide your WordPress site URL, username, and application password.")
