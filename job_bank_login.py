import random
import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def read_security_questions(file_name):
    questions = {}
    with open(file_name, "r") as file:
        for line in file:
            question, answer = line.strip().split("::")
            questions[question] = answer
    return questions


def read_job_posting_links(file_name):
    with open(file_name, "r") as file:
        return [line.strip() for line in file]


# Read username, password, security questions, and job postings from text files
with open("username.txt", "r") as file:
    USERNAME = file.read().strip()

with open("password.txt", "r") as file:
    PASSWORD = file.read().strip()

SECURITY_QUESTIONS = read_security_questions("security_questions.txt")
job_posting_links = read_job_posting_links("job_postings.txt")

# Initialize the Chrome driver
chrome_service = Service("./chromedriver")
driver = webdriver.Chrome(service=chrome_service)
driver.get("https://employer.jobbank.gc.ca/employer/")

# Log in
email_field = driver.find_element(By.ID, "loginForm:input-email")
email_field.send_keys(USERNAME)
password_field = driver.find_element(By.ID, "loginForm:input-password")
password_field.send_keys(PASSWORD)
sign_in_button = driver.find_element(By.ID, "loginForm:j_id_40")
sign_in_button.click()

# Wait for the security question page to load
wait = WebDriverWait(driver, 10)
question_label = wait.until(
    EC.presence_of_element_located(
        (
            By.CSS_SELECTOR,
            "label.control-label.required.input-security-answer > .field-name",
        )
    )
)

# Retrieve the question text
question_text = question_label.text

# Check if the question is in the SECURITY_QUESTIONS dictionary and enter the answer
if question_text in SECURITY_QUESTIONS:
    answer = SECURITY_QUESTIONS[question_text]
    answer_field = driver.find_element(By.ID, "securityForm:input-security-answer")
    answer_field.send_keys(answer)

    # Click the Continue button
    continue_button = driver.find_element(By.ID, "continueButton")
    continue_button.click()
else:
    print(f"Unexpected security question: {question_text}")
    # Add additional handling if needed, e.g., logging out and trying again or notifying the user


# Function to find all candidates in a job posting and invite them to apply
def invite_eligible_candidates(job_posting_url):
    driver.get(job_posting_url)

    # Wait for the page to load completely
    wait.until(EC.presence_of_element_located((By.ID, "matchlistpanel")))

    # Extract comparison chart URLs using JavaScript
    comparison_chart_urls = driver.execute_script(
        """
        const candidateRows = document.querySelectorAll('#matchlistpanel tbody tr');
        const chartURLs = [];
        candidateRows.forEach(row => {
            const notInvited = row.querySelector('.text-center.invited-column').innerText.includes('Not invited to apply');
            if (notInvited) {
                const chartURL = row.querySelector('.control a').getAttribute('href');
                chartURLs.push(chartURL);
            }
        });
        return chartURLs;
        """
    )

    # Visit each comparison chart URL and invite the candidate to apply
    for url in comparison_chart_urls:
        driver.get(f"https://employer.jobbank.gc.ca{url}")
        wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//input[@value='Invite to apply']")
            )
        )

        # Locate and click the "Invite to apply" button
        invite_button = driver.find_element(
            By.XPATH, "//input[@value='Invite to apply']"
        )
        invite_button.click()

        # Wait for a random duration between 1 and 5 seconds to avoid being flagged as a bot
        time.sleep(random.randint(1, 5))


# Process each job posting link
for job_posting_link in job_posting_links:
    print(f"Job Posting: {job_posting_link}")
    invite_eligible_candidates(job_posting_link)
    print("All eligible candidates invited.\n")
