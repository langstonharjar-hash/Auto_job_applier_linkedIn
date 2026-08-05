'''
Author:     Sai Vignesh Golla
LinkedIn:   https://www.linkedin.com/in/saivigneshgolla/

Copyright (C) 2024 Sai Vignesh Golla

License:    GNU Affero General Public License
            https://www.gnu.org/licenses/agpl-3.0.en.html
            
GitHub:     https://github.com/GodsScion/Auto_job_applier_linkedIn

Support me: https://github.com/sponsors/GodsScion

version:    26.01.20.5.08
'''


###################################################### APPLICATION INPUTS ######################################################


# >>>>>>>>>>> Easy Apply Questions & Inputs <<<<<<<<<<<

# Give an relative path of your default resume to be uploaded. If file in not found, will continue using your previously uploaded resume in LinkedIn.
default_resume_path = "Langston_Harris_Jara_Resume.pdf"

# What do you want to answer for questions that ask about years of experience you have, this is different from current_experience? 
years_of_experience = "7"          # A number in quotes Eg: "0","1","2","3","4", etc.

# Do you need visa sponsorship now or in future?
require_visa = "No"               # "Yes" or "No"

# What is the link to your portfolio website, leave it empty as "", if you want to leave this question unanswered
website = "https://github.com/GodsScion"                        # "www.example.bio" or "" and so on....

# Please provide the link to your LinkedIn profile.
linkedIn = "https://www.linkedin.com/in/saivigneshgolla/"       # "https://www.linkedin.com/in/example" or "" and so on...

# What is the status of your citizenship? # If left empty as "", tool will not answer the question. However, note that some companies make it compulsory to be answered
# Valid options are: "U.S. Citizen/Permanent Resident", "Non-citizen allowed to work for any employer", "Non-citizen allowed to work for current employer", "Non-citizen seeking work authorization", "Canadian Citizen/Permanent Resident" or "Other"
us_citizenship = "U.S. Citizen/Permanent Resident"



## SOME ANNOYING QUESTIONS BY COMPANIES 🫠 ##

# What to enter in your desired salary question (American and European), What is your expected CTC (South Asian and others)?, only enter in numbers as some companies only allow numbers,
desired_salary = 1200000          # 80000, 90000, 100000 or 120000 and so on... Do NOT use quotes
'''
Note: If question has the word "lakhs" in it (Example: What is your expected CTC in lakhs), 
then it will add '.' before last 5 digits and answer. Examples: 
* 2400000 will be answered as "24.00"
* 850000 will be answered as "8.50"
And if asked in months, then it will divide by 12 and answer. Examples:
* 2400000 will be answered as "200000"
* 850000 will be answered as "70833"
'''

# What is your current CTC? Some companies make it compulsory to be answered in numbers...
current_ctc = 110000            # 800000, 900000, 1000000 or 1200000 and so on... Do NOT use quotes
'''
Note: If question has the word "lakhs" in it (Example: What is your current CTC in lakhs), 
then it will add '.' before last 5 digits and answer. Examples: 
* 2400000 will be answered as "24.00"
* 850000 will be answered as "8.50"
# And if asked in months, then it will divide by 12 and answer. Examples:
# * 2400000 will be answered as "200000"
# * 850000 will be answered as "70833"
'''

# (In Development) # Currency of salaries you mentioned. Companies that allow string inputs will add this tag to the end of numbers. Eg: 
# currency = "INR"                 # "USD", "INR", "EUR", etc.

# What is your notice period in days?
notice_period = 14                   # Any number >= 0 without quotes. Eg: 0, 7, 15, 30, 45, etc.
'''
Note: If question has 'month' or 'week' in it (Example: What is your notice period in months), 
then it will divide by 30 or 7 and answer respectively. Examples:
* For notice_period = 66:
  - "66" OR "2" if asked in months OR "9" if asked in weeks
* For notice_period = 15:"
  - "15" OR "0" if asked in months OR "2" if asked in weeks
* For notice_period = 0:
  - "0" OR "0" if asked in months OR "0" if asked in weeks
'''

# Your LinkedIn headline in quotes Eg: "Software Engineer @ Google, Masters in Computer Science", "Recent Grad Student @ MIT, Computer Science"
linkedin_headline = "Product Data Analyst | Python, SQL, A/B Testing & Predictive Modeling | BA from UC Berkeley" # "Headline" or "" to leave this question unanswered

# Your summary in quotes, use \n to add line breaks if using single quotes "Summary".You can skip \n if using triple quotes """Summary"""
linkedin_summary = """
Product Data Analyst with a strong track record in player segmentation, monetization strategies, user engagement frameworks, and business optimization. Proven ability to transform complex datasets into actionable insights using advanced SQL and Python. Collaborative, innovative, and results-oriented professional specializing in dynamic analysis and cross-functional leadership.
"""

'''
Note: If left empty as "", the tool will not answer the question. However, note that some companies make it compulsory to be answered. Use \n to add line breaks.
''' 

# Your cover letter in quotes, use \n to add line breaks if using single quotes "Cover Letter".You can skip \n if using triple quotes """Cover Letter""" (This question makes sense though)
cover_letter = """
Cover Letter
"""
##> ------ Dheeraj Deshwal : dheeraj9811 Email:dheeraj20194@iiitd.ac.in/dheerajdeshwal9811@gmail.com - Feature ------

# Your user_information_all letter in quotes, use \n to add line breaks if using single quotes "user_information_all".You can skip \n if using triple quotes """user_information_all""" (This question makes sense though)
# We use this to pass to AI to generate answer from information , Assuing Information contians eg: resume  all the information like name, experience, skills, Country, any illness etc. 
user_information_all = """
LANGSTON HARRIS JARA
San Francisco, CA | 916-990-8266 | langston.harjar@gmail.com | Data Analyst

PROFILE
Product Data Analyst with a strong track record in player segmentation, monetization strategies, user engagement frameworks, and business optimization. Proven ability to transform complex datasets into actionable insights using advanced SQL and Python. Collaborative, innovative, and results-oriented professional specializing in dynamic analysis and cross-functional leadership.

EMPLOYMENT HISTORY
Product Data Analyst | 2K Games | Novato, CA | 2026 – Present
- Spearheaded product analytics and player segmentation frameworks for card-collecting features, uncovering key engagement trends to increase D30 retention by 12% and overall feature stickiness by 18%.
- Analyzed player investment behavior to inform dynamic pack composition adjustments and strategic monetization models, driving a 13% increase in average revenue for the strongest player cohort.
- Partnered with product managers and game designers to evaluate dynamic pricing strategies, improving in-game economy balance and reducing virtual resource inflation by 15%.

Data Analyst | Dropbox | San Francisco, CA | 2025 – 2026
- Managed reporting and analytics for ~30% of the company's business, leveraging advanced SQL window functions to calculate active growth comparisons between quarters, reducing report generation time by 40 hours monthly.
- Partnered with cross-functional teams to redefine organization-wide sales logic, presenting data-driven go-to-market strategies directly to C-Suite executives that contributed to a 2.5 million USD pipeline increase in Q3.

GTM/SalesOps Data Analyst | LinkedIn | San Francisco, CA | 2024 – 2025
- Segmented the existing customer base to identify long-tail customer distributions, uncovering 1.2 million USD in cross-selling opportunities and mitigating regional churn by 14%.
- Engineered predictive models and performed rapid dataframe manipulations utilizing Python and Polars for advanced grouping and sorting, processing 50M+ rows 3x faster than legacy scripts.
- Conducted exploratory A/B testing and inferential statistics to drive core KPIs across B2B and B2C channels, resulting in a 17% boost in conversion rates.

Data Analyst | Google | Redwood City, CA | 2022 – 2023
- Executed expert-level SQL queries—including precise daily result isolation and complex schema troubleshooting—reducing query runtimes by 35% and cutting operational data costs by 150,000 USD annually.
- Designed intuitive data storytelling dashboards to guide ad-sellers toward high-potential revenue streams, increasing ad-seller productivity by 20%.
- Spearheaded measurement and analysis changes within the Google Ads platform, optimizing data signals and taxonomy to improve tracking accuracy by 25%.

Data Analyst | California YMCA Youth & Government | Sacramento, CA | 2019 – 2021
- Engineered robust data pipelines for program, payment, and donor information using custom functions, macros, and Apps Script APIs, eliminating 30+ hours of weekly manual data entry.
- Delivered high-level reporting and strategic insights directly to executive leadership, Board of Directors, and management teams to secure a 15% increase in annual funding.

EDUCATION
Bachelor of Arts | University of California, Berkeley | Graduated 2019

WORK AUTHORIZATION & CITIZENSHIP
- U.S. Citizen / Permanent Resident
- Legally authorized to work in the United States for any employer
- Do NOT require visa sponsorship now or in the future

SKILLS
Languages: Python, SQL, R, Spanish
Data & Analytics: Pandas, Polars, Scikit, SciPy, ETL, A/B Testing, Predictive Modeling
Tools & Platforms: Looker, PowerBI, Tableau, Excel, Google Ads
"""
##<
'''
Note: If left empty as "", the tool will not answer the question. However, note that some companies make it compulsory to be answered. Use \n to add line breaks.
''' 

# Name of your most recent employer
recent_employer = "2K Games" # "", "Lala Company", "Google", "Snowflake", "Databricks"

# Example question: "On a scale of 1-10 how much experience do you have building web or mobile applications? 1 being very little or only in school, 10 being that you have built and launched applications to real users"
confidence_level = "8"             # Any number between "1" to "10" including 1 and 10, put it in quotes ""
##



# >>>>>>>>>>> RELATED SETTINGS <<<<<<<<<<<

## Allow Manual Inputs
# Should the tool pause before every submit application during easy apply to let you check the information?
pause_before_submit = True         # True or False, Note: True or False are case-sensitive
'''
Note: Will be treated as False if `run_in_background = True`
'''

# Should the tool pause if it needs help in answering questions during easy apply?
# Note: If set as False will answer randomly...
pause_at_failed_question = True    # True or False, Note: True or False are case-sensitive
'''
Note: Will be treated as False if `run_in_background = True`
'''
##

# Do you want to overwrite previous answers?
overwrite_previous_answers = False # True or False, Note: True or False are case-sensitive







############################################################################################################
'''
THANK YOU for using my tool 😊! Wishing you the best in your job hunt 🙌🏻!

Sharing is caring! If you found this tool helpful, please share it with your peers 🥺. Your support keeps this project alive.

Support my work on <PATREON_LINK>. Together, we can help more job seekers.

As an independent developer, I pour my heart and soul into creating tools like this, driven by the genuine desire to make a positive impact.

Your support, whether through donations big or small or simply spreading the word, means the world to me and helps keep this project alive and thriving.

Gratefully yours 🙏🏻,
Sai Vignesh Golla
'''
############################################################################################################