"""This file runs on AWS Lambda"""

import smtplib
import os
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

YOUTUBE_TRENDING_URL = 'https://www.youtube.com/feed/trending'

BINARY_LOCATION = os.environ['BINARY_LOCATION']

def get_driver():
  options = Options()
  options.binary_location = '/opt/headless-chromium'
  options.add_argument('--headless')
  options.add_argument('--no-sandbox')
  options.add_argument('--single-process')
  options.add_argument('--disable-dev-shm-usage')
  driver = webdriver.Chrome('/opt/chromedriver',chrome_options=options)
  
  return driver

def get_videos(driver):
  VIDEO_DIV_TAG = 'ytd-video-renderer'
  driver.get(YOUTUBE_TRENDING_URL)
  videos = driver.find_elements(By.TAG_NAME, VIDEO_DIV_TAG)
  return videos

def parse_video(video):
  title_tag = video.find_element(By.ID, 'video-title')
  title = title_tag.text
  url = title_tag.get_attribute('href')
  
  thumbnail_tag = video.find_element(By.TAG_NAME, 'img')
  thumbnail_url = thumbnail_tag.get_attribute('src')

  channel_div = video.find_element(By.CLASS_NAME, 'ytd-channel-name')
  channel_name = channel_div.text
  
  description = video.find_element(By.ID, 'description-text').text

  return {
    'title': title,
    'url': url,
    'thumbnail_url': thumbnail_url,
    'channel': channel_name,
    'description': description
  }
  
def send_email(body):
  try:
    server_ssl = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server_ssl.ehlo()   

    SENDER_EMAIL = 'sendsometrends@gmail.com'
    RECEIVER_EMAIL = 'sendsometrends@gmail.com'
    SENDER_PASSWORD = os.environ['GMAIL_PASSWORD']
    
    subject = 'YouTube Trending Videos'

    email_text = f"""
    From: {SENDER_EMAIL}
    To: {RECEIVER_EMAIL}
    Subject: {subject}

    {body}
    """

    server_ssl.login(SENDER_EMAIL, SENDER_PASSWORD)
    server_ssl.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, email_text)
    server_ssl.close()

  except:
      print('Something went wrong...')


def lambda_handler(event, context):
    # Create the browser
    driver = get_driver()
    
    # Get the videos
    videos = get_videos(driver)
    
    # Parse the top 10 videos
    videos_data = [parse_video(video) for video in videos[:10]]
    
    # Send the data over email
    body = json.dumps(videos_data)
    send_email(body)

    driver.close();
    driver.quit();

    response = {
        "statusCode": 200,
        "body": videos_data
    }

    return response


if __name__ == "__main__":
  lambda_handler(None, None)

    
