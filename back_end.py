import logging
from random import uniform
from time import sleep
from typing import Dict, List

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def login_and_answer_security_question(
    driver, username: str, password: str, security: Dict[str, str]
) -> None:
    driver.get("https://employer.jobbank.gc.ca/employer/")

    email_field = driver.find_element(By.ID, "loginForm:input-email")
    email_field.send_keys(username)
    password_field = driver.find_element(By.ID, "loginForm:input-password")
    password_field.send_keys(password)
    sign_in_button = driver.find_element(By.ID, "loginForm:j_id_40")
    sign_in_button.click()

    wait = WebDriverWait(driver, 10)
    question_label = wait.until(
        EC.presence_of_element_located(
            (
                By.CSS_SELECTOR,
                "label.control-label.required.input-security-answer > .field-name",
            )
        )
    )

    question_text = question_label.text

    if question_text in security:
        answer = security[question_text]
        answer_field = driver.find_element(By.ID, "securityForm:input-security-answer")
        answer_field.send_keys(answer)

        continue_button = driver.find_element(By.ID, "continueButton")
        continue_button.click()
    else:
        logging.error(f"Unexpected security question: {question_text}")


def invite_eligible_candidates(
    username: str, password: str, security: Dict[str, str], job_posting_links: List[str]
) -> None:
    chrome_service = Service("./chromedriver")
    driver = Chrome(service=chrome_service)

    try:
        login_and_answer_security_question(driver, username, password, security)

        for job_posting_link in job_posting_links:
            driver.get(job_posting_link)

            wait = WebDriverWait(driver, 10)
            wait.until(EC.presence_of_element_located((By.ID, "matchlistpanel")))

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

            for url in comparison_chart_urls:
                driver.get(f"https://employer.jobbank.gc.ca{url}")
                wait.until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//input[@value='Invite to apply']")
                    )
                )

                invite_button = driver.find_element(
                    By.XPATH, "//input[@value='Invite to apply']"
                )
                invite_button.click()

                sleep(uniform(1, 5))

            logging.info(f"Invited candidates for {job_posting_link}.\n")

        logging.info("All eligible candidates invited.\n")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        driver.quit()
