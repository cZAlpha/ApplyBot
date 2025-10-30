```
╭─────────────────╮
│    ApplyBot    │
╰─────────────────╯
    ∧___∧
   ( •ㅅ•) 
   /     ♡ 
   (   ⌒ ヽ  
   ＼_ﾉ  ＿」  
    ♪ ~ ♪
```

# ApplyBot
A bot to automatically apply to job postings. An attempt to combat the insanely stupid job market using the shotgun method.
<br><br>
Made for use with Firefox.
<br>
Made with love.
<br><br>

# Todo
- IMPORTANT: Change the structure of the xpath_stats.json to be:
    "element_name" {
      "/html/body/div[6]/div[3]/div[2]/div/div/main/div[2]/div[1]/div/div[1]/div/div/div/div[2]/div/h1": {
        "count": 4
      }
    }
  Instead of:
    "element_name" {
      "xpath_2": {
        "count": 4,
        "xpath": "/html/body/div[6]/div[3]/div[2]/div/div/main/div[2]/div[1]/div/div[1]/div/div/div/div[2]/div/h1",
        "index": 2
      }
    }
    REASON: Keeping track of the index is totally unnecessary and overcomplicates things. This is because if the xpath array is adjusted post hoc other than just appendations, it will cease to work and break everything.
- Adjust calls to the scraping for specific element function to run through the statistically optimized list of xpaths first, and then fall back on the default list (basically how it is currently done as of writing this). This will allow for better efficiency when enough jobs have been scraped.
- Have the bot search for "No longer accepting applications". If this is detected at all, disregard the current link being scraped, as its not available. This should be another statistic tracked
- Adjust pay rate normalization function to put the mean (average) pay rate in the pay rate column, and place the range in the notes column (notes column may need to be added). NOTE: Sometimes it will do stuff like: "('$47,000', 'Original range: $37,440/yr - $58,240/yr')", which is basically what I want minus the notes column, but it only does this <50% of the time for some reason. Not sure why.
- Have the bot search for "top secret clearance", "polygraph", etc. and all related terms and not include it in the output if the config says the user does not have a TS clearance
- Add skills to the config and write an algorithm to determine how many skills are listed in the job that the user has, giving a percentage score to each job and sorting them by said score. More things should be added to how this score it calculated as the project moves forward.
- Set up a config file that can be changed by the user that will never be committed to Github (other than the initial template one) that contains information like login info., and general settings such as speed and level of anti-bot countermeasures, and a file path to the resume.
  - NOTE: This is currently implemented but for now only has the Firefox profile file path.
- Reinforce anti-bot countermeasures.
  - Find a way to bypass Cloudflare anti-bot protection for Indeed
  - Find a way to bypass LinkedIn's captcha on login to make it automatic
- Automate application process for easy apply on LinkedIn and Indeed.
- Automate application process for Workday websites as much as possible.
  - This will involve account creation, and tracking of login information. This should be done in a file outside of this project so that login information is not sent to Github, likely in a CSV file on the desktop, or wherever and whose file path will be set in a config.
- Integrate generative AI using Ollama to adjust resume for specific job postings to ensure highest likelihood of bypassing ATS.
- Add ability for this program to find jobs based on inputted job titles in config file, location, and distance from location as well as other applicable information such as: pay rate, experience level, etc. (this is highly platform dependant)/
- More that I haven't thought of yet.
<br><br>

## Note From Author

### PII
In all of the text below, I have omitted my name and paths that may include PII and replaced it with an ellipses ("..."). Keep this in mind when troubleshooting and just in general.
<br><br>

### Don't Worry About This Warning
Its probably mildly important but frankly I do not care, if you see this and figure out how to get it to stop, shoot me an email and/or PR.
```
/.../ApplyBot/env/lib/python3.9/site-packages/urllib3/__init__.py:35: NotOpenSSLWarning: urllib3 v2 only supports OpenSSL 1.1.1+, currently the 'ssl' module is compiled with 'LibreSSL 2.8.3'. See: https://github.com/urllib3/urllib3/issues/3020
  warnings.warn(
```
<br><br>

# Sample Usage

Once you have found a bunch of job listings you'd like to scrape the information from, put it in a spreadsheet of your choosing, ensuring that all listing URLs are on different lines. Then export that as a CSV file. Below, this is called 'input.csv'. You can then designate the name for the output file, below this is called 'output.csv'.
<br>
The process of sourcing job listing URLs will eventually be automated.
```
python main.py input.csv output.csv
```
<br><br>

# Sample Output
```
Reading job links...
Found 41 unique job links
Using real Firefox profile: /.../....default-release
MANUAL LOGIN REQUIRED:
1. A Firefox window will open
2. Sign in to LinkedIn manually
3. Come back here and press Enter
Press Enter AFTER you have successfully signed in...

Processing link 1/41

...

Processing link 41/41

Scraping: https://www.linkedin.com/jobs/view/4331820820/?eBP=CwEAAAGaK7o7NrCSP_Z5r7VZV4YfWn0WBRlZsq3m9j4Vlpz-dHllwkp1CkI-5nu0x7ui6peECM9gTYctnEAXlnkmCQhYuKjr7oYcsp0FI2YWDstcQvCAzRspRlEnATq7yttKbhL4DoyPj1ozQbJV3nyxppWtKI7_9JdxmonIMB8vn9jXu0Whte4C7Zf28QugGGHdaTLRdLE25vgK5oA_e4mO53fCTg6dBgXYLm5W7IYbE6xnSQYynbHLUjT0FJTU4y3VGtpR5BB5tpvArCMz-l6yYR22G-nqdYufaHZl5oLStJahu7ZjHERdEXwUh0N81WX-2NI1uL7Nl9j68SoEZNdZIFOiUzRjD2yawMjglAji6FhU65L-s0BXjdt16a44H5HbqSm2pCovhWd_Y43fnJxfTlRP_3V8F30lFsr-BViZfpWTl1mloUkq0GctZHsQ6sMxCXW8dXl01fe2TblcS0pP1jT6GNnz_Gw5XuyualkYwi52TBMd26xS6GXYKmcbfHfG8MMngW_PjA&lici=QWiFA4f6iuFpaMz0Q3oejQ%3D%3D
  Found with XPath #2: /html/body/div[6]/div[3]/div[2]/div/div/main/div[2]/div[1]/div/div[1]/div/div/div/div[2]/div/h1
  Found with XPath #2: /html/body/div[6]/div[3]/div[2]/div/div/main/div[2]/div[1]/div/div[1]/div/div/div/div[1]/div[1]/div/a
  Found with XPath #2: /html/body/div[6]/div[3]/div[2]/div/div/main/div[2]/div[1]/div/div[1]/div/div/div/div[3]/div/span/span[1]
  Title: Programmer I- Custom Reports
  Employer: Lensa
  Location: United States
  Pay Rate: ?
✓ Successfully scraped and saved

===================================================
Scraping Complete!
Successful: 39
Failed: 2
Output saved to: output.csv

Failed links:
  - https://www.linkedin.com/jobs/view/4332016692/?eBP=CwEAAAGaKIvhSk-ziBRlUPKA56C-O87xlUqNy0MFmKHuBcCo4jr5Fg047M65UCrQlqtzhJIR3VzGmMW7qthPXqGhlJwlgt-0hePQZuGKb7WdYdDg-LGAj8j5gxv5SEqt3ec6XdSNVgOHSZDyqLTDFvpLj05X20ks0PMZ3VfTjyVVaFnMYPBc3wsTJYE7wbnYEbK4cPW7aOO7qK_XFwtLISy1PUF84V6QGyhryzTkbkDL5KsP9_P86J0pAoMui-48E3bVh4MN2Jo_RinqPzmSiG6mQRplr1_lmyQk_5ihlONZyyqOZZNPxXgG6M3WsFvCfQsDA0HYpUlS0eaNg-_Sjq6smoYwSIFxYhCrxvKF7iZo9KShixPyURyq3ETK5wLr5KC8bit1sVw_798QY7oCdUV1sOQrzVI8ClBY1IZc5oIKFrRvoPcny4mMkJkIm7xJmQkQNUYXfyi3qAunHgn7945Hz9mkLMMdA-W06wcatfFKLZRod3488YhqVNLR4mbgT_pLt0wotfSyorLr5G8&lici=gznxmE0d7BU4A7rZuiApAA%3D%3D
  - https://www.linkedin.com/jobs/view/4332450147/?eBP=NOT_ELIGIBLE_FOR_CHARGING&lici=gheChUzG%2B1T%2FK5oZM%2FeaLw%3D%3D
```

<br><br>

# Good Luck!