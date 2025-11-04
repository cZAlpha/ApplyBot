```
╭─────────────────╮
│    ApplyBot     │
╰─────────────────╯
    ∧___∧
   ( •ㅅ•) 
   /     ♡ 
   (   ⌒  \  
   ＼_ﾉ \＿」  
    ♪ ~ ♪
```

# ApplyBot
A bot to automatically apply to job postings. An attempt to combat the insanely stupid job market using the shotgun method.
<br><br>
Made for use with Firefox (stop using Chrome you weirdo).
<br>
Made with love.
<br><br>

# Processes
```
+-----------------------------------------+
|           APPLY BOT PROCESS             |
+-----------------------------------------+
                    |
                    v
    +-------------------------------+
    |       1. Job Finding          |
    |                               |
    |        <NOT STARTED>          |
    |  - Search on job boards       |
    |  - Uses config settings       |
    +-------------------------------+
                    |
                    | CSV of Job URLs
                    v
    +-------------------------------+
    |       2. Job Scraping         |
    |                               |
    |            <WIP>              |
    |  - Scrape job details         |
    |  - Filter out based on config |
    |  - Save to CSV                |
    +-------------------------------+
                    |
                    | CSV of Job Details
                    v
    +-------------------------------+
    |      3. Applying to Jobs      |
    |                               |
    |            <WIP>              |
    |  - Review scraped data        |
    |  - Tailor resume/cover letter |
    |  - Submit application         |
    +-------------------------------+
```

# Todo
### General
- Add ability for normalize_pay_rate to handle stuff like "$6,943/month - $8,083/month", as it cannot do so currently.
- Reinforce anti-bot countermeasures.
  - Find a way to bypass Cloudflare anti-bot protection for Indeed
      - Not sure if this is even possible, which really sucks
  - Find a way to bypass LinkedIn's captcha on login to make it automatic
### 1. Job Finding
- Add ability for this program to find jobs based on inputted job titles in config file, location, and distance from location as well as other applicable information such as: pay rate, experience level, etc. (this is highly platform dependant)
### 2. Job Scraping
- Ensure that the job description is scraped and placed into the output CSV file, as this is needed for the AI resume tailor
- Adjust calls to the scraping for specific element function to run through the statistically optimized list of xpaths first, and then fall back on the default list (basically how it is currently done as of writing this). This will allow for better efficiency when enough jobs have been scraped
- Have the bot search for "No longer accepting applications". If this is detected at all, disregard the current link being scraped, as its not available. This should be another statistic tracked
  - This is done for Indeed.com but not for Linkedin.com
- Write an algorithm to determine how many skills are listed in the job that the user has from the config, giving a percentage score to each job and sorting them by said score. More things should be added to how this score it calculated as the project moves forward.
### 3. Applying to Jobs
- Automate application process for easy apply on LinkedIn and Indeed
- Automate application process for Workday websites as much as possible
- Finish automating Greenhouse.io websites as much as possible
- These will involve account creation, and tracking of login information. This should be done in a file outside of this project so that login information is not sent to Github, likely in a CSV file on the desktop, or wherever and whose file path will be set in a config.
- Finish generative AI using Ollama to adjust resume for specific job postings to ensure highest likelihood of bypassing ATS.
  - Status: Ridden with issues
    - Typically lengthens resume from 1 -> 2 pages due to mainly formatting issues.
    - Will relatively often lie about skills the user possesses.
<br><br>

## Notes From Author

### Your Data
I'm not Google (stop using Chrome!), this bot does not and will never collect you data.

### PII
In all of the text below, I have omitted my name and paths that may include PII and replaced it with an ellipses ("..."). Keep this in mind when troubleshooting and just in general.
<br><br>

### Questions?
If you have any questions, reach out to me.

<br><br>

# Sample Usage

Once you have found a bunch of job listings you'd like to scrape the information from, put it in a spreadsheet of your choosing, ensuring that all listing URLs are on different lines. Then export that as a CSV file. Below, this is called 'input.csv'. You can then designate the name for the output file, below this is called 'output.csv'.
<br>
The process of sourcing job listing URLs will eventually be automated.
```
.../python .../main.py input.csv output.csv --config="config.json"
```

## input.csv
The input file. Should contain job listing URLs on each line. The name does not matter, as long as its a CSV.

## output.csv
The output file. The name does not matter, as long as its a CSV.

## --config="config.json"
The config file. This uses the default one, which may or may not work. I would suggest making your own. If you name it "my_config.json", it will not be included in Git.

<br><br>

# Sample Output 
```
==================================================


╭─────────────────╮
│    ApplyBot    │
╰─────────────────╯

    ∧___∧
   ( •ㅅ•) 
   /     ♡ 
   (   ⌒ ヽ  
   ＼_ﾉ  ＿」  
    ♪ ~ ♪

   Made by cZAlpha


==================================================

Normalizing Job Listing URLs...
Successfully normalized 39/39 of input links.

==================================================

✅ Config loaded from 'my_config.json'

==================================================

🕒 Parsing job links from input.csv...


✅ Found 39 unique job links

==================================================

Optimized Job Scraping XPaths (JSON format)

🕒 Opening browser with user profile...
    Profile: /.../Firefox/Profiles/l2iog7ld.default-release

==================================================

Processing link 1/39

Scraping: https://www.linkedin.com/jobs/view/4320419786/
  Job Title was found with XPath #5: //h1[contains(@class, 't-24') and contains(@class, 't-bold')]
XPath statistics saved to xpath_stats.json
  Employer was found with XPath #3: /html/body/div[6]/div[3]/div[2]/div/div/main/div[2]/div[1]/div/div[1]/div/div/div/div[1]/div[1]/div/a
XPath statistics saved to xpath_stats.json
  Location was found with XPath #3: /html/body/div[6]/div[3]/div[2]/div/div/main/div[2]/div[1]/div/div[1]/div/div/div/div[3]/div/span/span[1]
XPath statistics saved to xpath_stats.json
  Pay Rate was found with XPath #3: /html/body/div[6]/div[3]/div[2]/div/div/main/div[2]/div[1]/div/div[1]/div/div/div/div[4]/button[1]/span/strong
XPath statistics saved to xpath_stats.json
  Clearance Check: User has 'none' (0), job requires 'none' (0)
  ✓ User meets clearance requirement
  Title: Intermediate Technical Support Analyst
  Employer: Journal Technologies
  Location: United States
  Pay Rate: ?
  Notes: Could not find or parse pay rate.
  Clearance Level: None
  Easy Apply: False
✅ Successfully scraped and saved

==================================================

...

==================================================

Processing link 39/39

Scraping: https://www.linkedin.com/jobs/view/4333695534/
  Job Title was found with XPath #5: //h1[contains(@class, 't-24') and contains(@class, 't-bold')]
XPath statistics saved to xpath_stats.json
  Employer was found with XPath #3: /html/body/div[6]/div[3]/div[2]/div/div/main/div[2]/div[1]/div/div[1]/div/div/div/div[1]/div[1]/div/a
XPath statistics saved to xpath_stats.json
  Location was found with XPath #3: /html/body/div[6]/div[3]/div[2]/div/div/main/div[2]/div[1]/div/div[1]/div/div/div/div[3]/div/span/span[1]
XPath statistics saved to xpath_stats.json
  Pay Rate was found with XPath #4: /html/body/div[6]/div[3]/div[2]/div/div/main/div[2]/div[1]/div/div[1]/div/div/div/div[4]/button[1]/span[1]/span/strong
XPath statistics saved to xpath_stats.json
  Security Clearance: Detected 'Top Secret with Polygraph' with pattern: ts.*sci.*poly
  Clearance Check: User has 'none' (0), job requires 'top secret with polygraph' (5)
  ✗ User does NOT meet clearance requirement
🚫 Job Thrown Out Due to Lack of Security Clearance!
🚫 Job closed - skipping to next job listing

==================================================
Scraping Complete!
 ✅ Successful: 35
 🚫 Failed: 0
Output saved to: output.csv

==================================================

    ∧___∧      __ _        _   _     _   _          
   ( •ㅅ•)     / _\ |_ __ _| |_(_)___| |_(_) ___ ___ 
   /     ♡    \ \| __/ _` | __| / __| __| |/ __/ __|
   (   ⌒ ヽ    _\ \ || (_| | |_| \__ \ |_| | (__\__ \
   ＼_ﾉ  ＿」   \__/\__\__,_|\__|_|___/\__|_|\___|___/
    ♪ ~ ♪

DOMAIN STATISTICS SUMMARY

www.linkedin.com:
  Elements tracked: 4
  Total hits: 155
  Job Title: 39 hits
  Employer: 39 hits
  Location: 39 hits

XPATH HIT STATISTICS

--- www.linkedin.com ---

Job Title:
  36 hits: //h1[contains(@class, 't-24') and contains(@class, 't-bold')]
  3 hits: /html/body/div[6]/div[3]/div[2]/div/div/main/div[2]/div[1]/div/div[1]/div/div/div/div[2]/div/h1

Employer:
  28 hits: /html/body/div[6]/div[3]/div[2]/div/div/main/div[2]/div[1]/div/div[1]/div/div/div/div[1]/div[1]/div/a
  7 hits: /html/body/div[5]/div[3]/div[2]/div/div/main/div[2]/div[1]/div/div[1]/div/div/div/div[1]/div[1]/div/a
  4 hits: //div[contains(@class, 'job-details-jobs-unified-top-card__company-name')]//a

Location:
  30 hits: /html/body/div[6]/div[3]/div[2]/div/div/main/div[2]/div[1]/div/div[1]/div/div/div/div[3]/div/span/span[1]
  9 hits: /html/body/div[5]/div[3]/div[2]/div/div/main/div[2]/div[1]/div/div[1]/div/div/div/div[3]/div/span/span[1]

Pay Rate:
  17 hits: /html/body/div[6]/div[3]/div[2]/div/div/main/div[2]/div[1]/div/div[1]/div/div/div/div[4]/button[1]/span/strong
  13 hits: /html/body/div[6]/div[3]/div[2]/div/div/main/div[2]/div[1]/div/div[1]/div/div/div/div[4]/button[1]/span[1]/span/strong
  6 hits: /html/body/div[5]/div[3]/div[2]/div/div/main/div[2]/div[1]/div/div[1]/div/div/div/div[4]/button[1]/span/strong
  2 hits: //strong[contains(., '$')]

ELEMENT SCRAPING FAILURES

Critical Element Scraping Failures: 0
Non-Critical Element Scraping Failures: 1

SECURITY CLEARANCE STATISTICS

Number of jobs thrown out due to lack of clearance: 4

(env) ...-MacBook-Pro ApplyBot % 
```

<br><br>

# AI Resume Tailoring Notes (WIP)

1. base resume (from config) 
2. feed base resume into LLM with prompt that includes the job description and/or keywords from the job description
3. adjusts the bullet points in your resume while keeping the # of chars per line the same as to avoid formatting issues (still working out the kinks)
4. Generates new resume pdf and shows user the PDF for approval (this could be a flag in the main.py args to avoid having to approve | this part is not done yet)
5. Uses the tailored resume to apply to the job (not done)
6. Places new resume pdf in a folder such that /employer/job_title/yourbaseresumename_job_title.pdf (not done)
 

<br><br>

# config.json
This is where you can configure how the bot will behave, what it knows about you, etc.

I would suggest, especially if you are going to contribute, that you make your own config. I call mine "my_config.json", hence the usage of that in the main.py file as well as the exclusion of htat in the gitignore.

Format:
```
{
   "firefox_profiles_path": "",
   "resume_path": "",
   "minimum_salary": "0",
   "clearance": "none",
   "skill_keywords": [
      "Microsoft Word",
      "Public Speaking",
      "Writing Reports"
   ],
   "first_name": "John",
   "last_name": "Doe",
   "email": "johndoe@gmail.com",
   "phone": "1234567890",
   "city": "New York",
   "state": "New York",
   "zip_code": "10001",
   "linkedin_url": "",
   "source": "Indeed",
   "is_18_or_older": "True",
   "work_eligible": "True",
   "requires_sponsorship": "False",
   "us_citizen": "True",
   "education_level": "Bachelor's Degree",
   "text_consent": "No",
   "desired_salary": "0",
   "start_date": "1",
   "disability": "optout",
   "veteran": "optout",
   "gender": "optout",
   "race": "optout",
   "truth_statement": "Yes",
   "agree_not_to_use_ai": "Yes",
   "agree_to_drug_test": "Yes",
   "felony": "No",
   "agree_to_background_check": "Yes",
   "dow_available_for_interview": "Weekday",
   "time_available_for_interview": "Anytime"
}
```
### firefox_profiles_path
The absolute path to your firefox profile. 
#### Notes:
This is required as of now but should default to a default profile in the future. I would highly suggest simply using the one you use normally, as platforms like LinkedIn and Indeed have information stored about your existing profile and will notice the change. It lessens the likelihood of it catching you. I would also highly suggest making an alternative account with a burner email while scraping information, as you do not need to be on your main account and if that one gets banned, who cares.

### resume_path
The absolute path to the resume you'd like to use.
#### Notes:
This is not yet implemented but in the future will be used while applying to jobs, and will be edited by a local LLM (or possibly one of your choosing, given you have an API key) to better fit the job being applied to.

### minimum_salary
The numerical minimum annual salary you are willing to work for. DO NOT USE COMMAS (e.x. "50000" NOT "50,000").
#### Notes:
This is not yet implemented but in the future will be used while applying to jobs, and will be edited by a local LLM (or possibly one of your choosing, given you have an API key) to better fit the job being applied to.

### clearance
The type of clearance you have (e.x. "none" by default, other values such as "public trust", "top secret", "top secret with polygraph")
#### Notes:
Used to remove jobs from the job scraping process if you do not possess the minimum clearance.

### skill_keywords
Skills you possess (examples included by default).
#### Notes:
This is not yet implemented but in the future will be used to score jobs that have been scraped on their viability / compatibility with your skillset. This may also be used to prompt the AI model that will tailor your resume so that it lies about your skills and experience as little as possible. This will likely be done with the EXACT SPECIFIC wording you use in your skill_keywords array so be sure to include variants of the same skill/skillset if it written in slightly different ways, otherwise the system will not know. This may be swapped out or bolstered by a local LLM in the future, but likely not.

### first_name
Your first name.
#### Notes:
Used to autofill application forms.
<br><br>

### last_name
Your last name.
#### Notes:
Used to autofill application forms.
<br><br>

### email
Your email address.
#### Notes:
Used to autofill application forms.
<br><br>

### phone
Your phone number.
#### Notes:
Used to autofill application forms.
<br><br>

### country
Your country of residence (e.x. United States by default)
#### Notes:
Used to autofill application forms.
<br><br>

### address
Your street address.
#### Notes:
Used to autofill application forms.
<br><br>

### city
Your city of residence.
#### Notes:
Used to autofill application forms.
<br><br>

### state
Your state of residence.
#### Notes:
Used to autofill application forms.
<br><br>

### zip_code
Your zip code.
#### Notes:
Used to autofill application forms.
<br><br>

### linkedin_url
Your LinkedIn profile URL.
#### Notes:
Used to autofill application forms.
<br><br>

### source
Where you heard about the job application system.
#### Notes:
Used to autofill application forms. Default: "Indeed", but you can do whatever you want, as long as it would be listed in a dropdown commonly.
<br><br>

### is_18_or_older
Whether you are 18 years or older.
#### Notes:
Used to autofill application forms. Options: "True" or "False", "Yes" or "No" (there are fallback values that should avoid issues)
<br><br>

### work_eligible
Whether you are eligible to work in the country.
#### Notes:
Used to autofill application forms. Options: "True" or "False", "Yes" or "No" (there are fallback values that should avoid issues)
<br><br>

### requires_sponsorship
Whether you require visa sponsorship.
#### Notes:
Used to autofill application forms. Options: "True" or "False", "Yes" or "No" (there are fallback values that should avoid issues)
<br><br>

### us_citizen
Whether you are a US citizen.
#### Notes:
Used to autofill application forms. Options: "True" or "False", "Yes" or "No" (there are fallback values that should avoid issues)
<br><br>

### education_level
Your highest education level.
#### Notes:
Used to autofill application forms. Options: "Bachelor's Degree", "Master's Degree", "Doctorate", "High School", etc.
<br><br>

### text_consent
Whether you consent to text communications.
#### Notes:
Used to autofill application forms. Options: "Yes" or "No". Always say no, why would you want these weirdos texting your phone?
<br><br>

### desired_salary
Your desired annual salary. This will be the value auto-filled into applications, NOT what will determine if a job listing will be thrown out when scraping.
#### Notes:
Used to autofill application forms. DO NOT USE COMMAS (e.x. "50000" NOT "50,000").
<br><br>

### start_date
When you can start working.
#### Notes:
Used to autofill application forms. Options: "1", "2", etc., this dictates how many WEEKS from today's date that your availability will be.
<br><br>

### disability
Disability status disclosure.
#### Notes:
Used to autofill EEO forms. Options: "optout", "Yes", "No"
I highly suggest to always optout, as you do not need to help companies in their quest to virtue signal, plus if they're able to see your picked option here, they'll likely throw your application out.
<br><br>

### veteran
Veteran status disclosure.
#### Notes:
Used to autofill EEO forms. Options: "optout", "Yes", "No"
I highly suggest to always optout, as you do not need to help companies in their quest to virtue signal.
<br><br>

### gender
Gender disclosure.
#### Notes:
Used to autofill EEO forms. Options: "optout", "Male", "Female", "Non-binary"
I highly suggest to always optout, as you do not need to help companies in their quest to virtue signal.
<br><br>

### race
Race/ethnicity disclosure.
#### Notes:
Used to autofill EEO forms. Options: "optout", "White", "Black", "Hispanic", "Asian", etc.
I highly suggest to always optout, as you do not need to help companies in their quest to virtue signal.
<br><br>

### truth_statement
Affirmation that application information is truthful.
#### Notes:
Used to autofill application forms. Options: "Yes" or "No" (If you don't have this as yes, you will never get a job!)
<br><br>

### agree_not_to_use_ai
Agreement not to use AI for work tasks.
#### Notes:
Used to autofill application forms. Options: "Yes" or "No" (If you don't have this as yes, you will never get a job!)
<br><br>

### agree_to_drug_test
Agreement to submit to drug testing.
#### Notes:
Used to autofill application forms. Options: "Yes" or "No" (If you don't have this as yes, you will never get a job!)
<br><br>

### agree_to_background_check
Agreement to background check.
#### Notes:
Used to autofill application forms. Options: "Yes" or "No" (If you don't have this as yes, you will never get a job!)
<br><br>

### felony
Do you have a felony on your record?
#### Notes:
Used to autofill application forms. Options: "Yes" or "No"
<br><br>

### dow_available_for_interview
The day(s) of the week that you are available for interviews, used solely for Indeed.com.
#### Notes:
This is not yet implemented but in the future will be used to input into the interview availability question on Indeed.com's easy apply. Options: "Weekday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"
<br><br>

### time_available_for_interview
The time(s) that you are available for interviews, used solely for Indeed.com.
#### Notes:
This is not yet implemented but in the future will be used to input into the interview availability question on Indeed.com's easy apply. Options: "Anytime" (8am-9pm), "Morning" (8am - 12pm), "Afternoon" (12pm - 5pm), "Evening" (5pm - 9pm).
<br><br>

# Good Luck!
