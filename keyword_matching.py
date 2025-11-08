import requests
import json
import PyPDF2
import os
import time
import re
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch


class ResumeTailor:
   def __init__(self, config):
      # Time the initalization
      print("")
      print("ResumeTailor initalizing...")
      init_start = time.time()
      
      # Initalization
      self.config = config
      self.ollama_url = "http://localhost:11434/api/generate"
      
      # Initialize PDF styles once
      self.setup_pdf_styles()
      
      # Extract and combine skills
      self.extract_and_combine_skills()
      
      # End the timing and print
      init_end = time.time()
      total_time = init_end - init_start
      print(f"ResumeTailor initalized in {total_time:.2f}s")
      print("")
   
   def extract_and_combine_skills(self):
      """Extract skills from resume and combine with config skills"""
      print("🔍 Extracting skills from resume...")
      
      # Extract text from resume
      resume_text = self.extract_text_from_pdf(self.config["resume_path"])
      
      # Parse skills section
      resume_skills = self.parse_skills_from_resume(resume_text)
      
      # Combine with config skills
      all_skills = list(set(self.config["skill_keywords"] + resume_skills))
      
      print(f"✅ Found {len(resume_skills)} skills in resume")
      print(f"    Resume skills:")
      for skill in resume_skills:
         print(f"       {skill}")
      print(f"✅ Combined total: {len(all_skills)} unique skills")
      
      self.all_skills = all_skills
   
   def parse_skills_from_resume(self, resume_text):
      """Parse skills from skills section in resume text"""
      skills = []
      
      # Look for skills section using various common headers
      skill_patterns = [
         r'Skills\s*[:\-\n]+(.*?)(?=\n\n|\n[A-Z][a-z]+\s*:|\n[A-Z]+\s*:|\nEducation|\nExperience|\nProjects|\nCertifications|$)',
         r'Technical Skills\s*[:\-\n]+(.*?)(?=\n\n|\n[A-Z][a-z]+\s*:|\n[A-Z]+\s*:|\nEducation|\nExperience|\nProjects|\nCertifications|$)',
         r'Core Competencies\s*[:\-\n]+(.*?)(?=\n\n|\n[A-Z][a-z]+\s*:|\n[A-Z]+\s*:|\nEducation|\nExperience|\nProjects|\nCertifications|$)'
      ]
      
      skills_text = ""
      for pattern in skill_patterns:
         match = re.search(pattern, resume_text, re.IGNORECASE | re.DOTALL)
         if match:
            skills_text = match.group(1).strip()
            break
      
      if not skills_text:
         print("⚠️  No skills section found in resume")
         return []
      
      # Parse skills from various formats
      # Format 1: Pipe separated - "Skill1 | Skill2 | Skill3"
      if '|' in skills_text:
         skills = [skill.strip() for skill in skills_text.split('|') if skill.strip()]
      
      # Format 2: Comma separated - "Skill1, Skill2, Skill3"
      elif ',' in skills_text:
         skills = [skill.strip() for skill in skills_text.split(',') if skill.strip()]
      
      # Format 3: Bullet points or line breaks
      else:
         lines = skills_text.split('\n')
         for line in lines:
            line = line.strip()
            # Remove bullet points and clean up
            line = re.sub(r'^[•\-*\s]+', '', line)
            if line and len(line) > 1:  # Avoid single characters
               skills.append(line.strip())
      
      # Clean up skills - remove empty strings and duplicates
      skills = [skill for skill in skills if skill and len(skill) > 1]
      skills = list(set(skills))
      
      return skills
   
   def extract_ats_keywords(self, job_description):
      """Extract ATS-relevant keywords from job description"""
      print("🔍 Extracting ATS keywords from job description...")
      
      prompt = f"""
      Analyze this job description and extract the most important technical skills, tools, and technologies that would be relevant for an Applicant Tracking System (ATS).
      
      JOB DESCRIPTION:
      {job_description}
      
      INSTRUCTIONS:
      1. Extract ONLY technical skills, software, tools, technologies, and specific methodologies
      2. Focus on keywords that would be scanned by ATS systems
      3. Return the results as a simple comma-separated list
      4. Do not include explanations, opinions, or non-technical skills
      5. Include both specific technologies (e.g., "Cisco", "Windows Active Directory") and general categories (e.g., "Virtualization", "Networking")
      6. Remove duplicates and group similar terms
      
      OUTPUT FORMAT:
      Keyword1, Keyword2, Keyword3, Keyword4, Keyword5
      """
      
      payload = {
         "model": "llama3.1:8b",
         "prompt": prompt,
         "stream": False
      }
      
      try:
         response = requests.post(self.ollama_url, json=payload)
         response.raise_for_status()
         result = response.json()["response"].strip()
         
         # Parse the comma-separated list
         ats_keywords = [keyword.strip() for keyword in result.split(',') if keyword.strip()]
         print(f"✅ Extracted {len(ats_keywords)} ATS keywords")
         print(f"    ATS Keywords:")
         for keyword in ats_keywords:
            print(f"          {keyword}")
         return ats_keywords
      
      except Exception as e:
         print(f"🚫 ERROR | extract_ats_keywords | Error calling Ollama: {e}")
         return []
   
   def optimize_skills_for_job(self, job_description, current_skills_section):
      """Optimize skills section for specific job description"""
      print("🎯 Optimizing skills section for job...")
      
      # Extract ATS keywords from job description
      ats_keywords = self.extract_ats_keywords(job_description)
      
      # Calculate available space in skills section (rough estimate)
      skills_char_limit = self.estimate_skills_section_capacity(current_skills_section)
      
      print(f"📏 Skills section capacity: ~{skills_char_limit} characters")
      
      # Get optimized skills selection
      optimized_skills = self.select_optimal_skills(ats_keywords, skills_char_limit)
      
      # Format the optimized skills section
      formatted_skills = self.format_skills_section(optimized_skills, current_skills_section)
      
      return formatted_skills
   
   def estimate_skills_section_capacity(self, skills_section):
      """Estimate character capacity of skills section based on original formatting"""
      if not skills_section:
         return 500  # Default reasonable size
      
      # Count characters in original skills section
      original_length = len(skills_section)
      
      # Add some buffer for formatting
      return min(original_length + 100, 800)  # Cap at reasonable maximum
   
   def select_optimal_skills(self, ats_keywords, char_limit):
      """Select most relevant skills that fit within character limit"""
      print("🤖 Selecting optimal skills combination...")
      
      # Prepare skills list for AI
      skills_list = ", ".join(self.all_skills)
      ats_list = ", ".join(ats_keywords)
      
      prompt = f"""
      JOB DESCRIPTION KEYWORDS:
      {ats_list}
      
      AVAILABLE SKILLS:
      {skills_list}
      
      TASK:
      1. Select the skills that are MOST relevant to the job description keywords
      2. Prioritize skills that match or are closely related to the job keywords
      3. Include a mix of technical and soft skills
      4. Select approximately 8-15 skills that will fit within {char_limit} characters when formatted
      5. Return ONLY a comma-separated list of the selected skills
      6. Do not add any explanations or additional text
      
      OUTPUT FORMAT:
      Skill1, Skill2, Skill3, Skill4, Skill5
      """
      
      payload = {
         "model": "llama3.1:8b",
         "prompt": prompt,
         "stream": False
      }
      
      try:
         response = requests.post(self.ollama_url, json=payload)
         response.raise_for_status()
         result = response.json()["response"].strip()
         
         # Parse selected skills
         selected_skills = [skill.strip() for skill in result.split(',') if skill.strip()]
         
         # Verify the selection fits within limits
         formatted_test = self.format_skills_list(selected_skills)
         if len(formatted_test) > char_limit:
            # Remove some skills if too long
            selected_skills = selected_skills[:max(8, len(selected_skills) - 2)]
         
         print(f"✅ Selected {len(selected_skills)} optimal skills")
         return selected_skills
      
      except Exception as e:
         print(f"🚫 ERROR | select_optimal_skills | Error calling Ollama: {e}")
         # Fallback: return original skills limited by count
         return self.all_skills[:12]
   
   def format_skills_list(self, skills):
      """Format skills list in pipe-separated format"""
      return " | ".join(skills)
   
   def format_skills_section(self, skills, original_section):
      """Format the complete skills section maintaining original structure"""
      if not original_section:
         # Create new skills section
         return "Skills\n" + self.format_skills_list(skills)
      
      # Extract the skills header from original section
      lines = original_section.split('\n')
      if lines:
         header = lines[0]
         # Replace the content after header with new skills
         return header + '\n' + self.format_skills_list(skills)
      else:
         return "Skills\n" + self.format_skills_list(skills)
   
   def extract_skills_section(self, resume_text):
      """Extract just the skills section from resume text"""
      skill_patterns = [
         r'(Skills\s*[:\-\n]+.*?)(?=\n\n|\n[A-Z][a-z]+\s*:|\n[A-Z]+\s*:|\nEducation|\nExperience|\nProjects|\nCertifications|$)',
         r'(Technical Skills\s*[:\-\n]+.*?)(?=\n\n|\n[A-Z][a-z]+\s*:|\n[A-Z]+\s*:|\nEducation|\nExperience|\nProjects|\nCertifications|$)',
         r'(Core Competencies\s*[:\-\n]+.*?)(?=\n\n|\n[A-Z][a-z]+\s*:|\n[A-Z]+\s*:|\nEducation|\nExperience|\nProjects|\nCertifications|$)'
      ]
      
      for pattern in skill_patterns:
         match = re.search(pattern, resume_text, re.IGNORECASE | re.DOTALL)
         if match:
            return match.group(1).strip()
      
      return None
   
   def replace_skills_section(self, resume_text, new_skills_section):
      """Replace the skills section in resume text with new one"""
      skill_patterns = [
         r'Skills\s*[:\-\n]+.*?(?=\n\n|\n[A-Z][a-z]+\s*:|\n[A-Z]+\s*:|\nEducation|\nExperience|\nProjects|\nCertifications|$)',
         r'Technical Skills\s*[:\-\n]+.*?(?=\n\n|\n[A-Z][a-z]+\s*:|\n[A-Z]+\s*:|\nEducation|\nExperience|\nProjects|\nCertifications|$)',
         r'Core Competencies\s*[:\-\n]+.*?(?=\n\n|\n[A-Z][a-z]+\s*:|\n[A-Z]+\s*:|\nEducation|\nExperience|\nProjects|\nCertifications|$)'
      ]
      
      for pattern in skill_patterns:
         if re.search(pattern, resume_text, re.IGNORECASE | re.DOTALL):
            # Replace the existing skills section
            return re.sub(pattern, new_skills_section, resume_text, flags=re.IGNORECASE | re.DOTALL)
      
      # If no skills section found, insert after contact info or at beginning
      lines = resume_text.split('\n')
      contact_end = 0
      for i, line in enumerate(lines):
         if any(contact in line.lower() for contact in ['@', 'phone', 'email', 'linkedin']):
            contact_end = i + 1
      
      if contact_end < len(lines):
         lines.insert(contact_end, '\n' + new_skills_section)
      else:
         lines.insert(1, '\n' + new_skills_section)
      
      return '\n'.join(lines)
   
   def setup_pdf_styles(self):
      """Setup PDF styles with more compact formatting for resumes"""
      self.styles = getSampleStyleSheet()
      
      # Create more compact styles for resume formatting
      if not hasattr(self.styles, 'Normal_Compact'):
         self.styles.add(ParagraphStyle(
               name='Normal_Compact',
               parent=self.styles['Normal'],
               fontSize=10,  # Smaller font size
               leading=12,   # Tighter line spacing
               spaceBefore=6,
               spaceAfter=6,
               fontName='Helvetica'
         ))
      
      if not hasattr(self.styles, 'Heading2_Compact'):
         self.styles.add(ParagraphStyle(
               name='Heading2_Compact',
               parent=self.styles['Heading2'],
               fontSize=12,
               leading=14,
               spaceBefore=12,
               spaceAfter=6,
               fontName='Helvetica-Bold'
         ))
      
      if not hasattr(self.styles, 'Bullet_Compact'):
         self.styles.add(ParagraphStyle(
               name='Bullet_Compact',
               parent=self.styles['Normal_Compact'],
               leftIndent=15,
               firstLineIndent=-15,
               spaceBefore=3,
               spaceAfter=3,
               fontSize=8,
               leading=8
         ))
   
   def extract_text_from_pdf(self, pdf_path):
      """Extract text from resume PDF with better formatting"""
      with open(pdf_path, 'rb') as file:
         reader = PyPDF2.PdfReader(file)
         text = ""
         for page in reader.pages:
            page_text = page.extract_text()
            # Clean up the formatting
            page_text = self.clean_resume_text(page_text)
            text += page_text + "\n\n"
         return text.strip()
   
   def clean_resume_text(self, text):
      """Clean and format resume text for better readability WITHOUT breaking dates"""
      # Replace multiple spaces with single spaces
      text = ' '.join(text.split())
      
      # Fix common formatting issues
      text = text.replace(' ● ', '\n● ')
      text = text.replace(' • ', '\n• ')
      text = text.replace(' - ', ' - ')
      
      # Add line breaks after sections
      sections = ['Experience', 'Education', 'Skills', 'Projects', 'Certifications']
      for section in sections:
         text = text.replace(f' {section} ', f'\n\n{section}\n')
      
      # Bullet point formatting
      lines = text.split('\n')
      formatted_lines = []
      
      for line in lines:
         line = line.strip()
         if not line:
               continue
               
         # Handle bullet points
         if line.startswith('●') or line.startswith('•') or line.startswith('-'):
               formatted_lines.append(line)
         # Handle section headers (all caps or title case)
         elif (line.isupper() or 
               any(section in line for section in ['Experience', 'Education', 'Skills', 'Projects']) or
               len(line) < 50 and not any(char.islower() for char in line)):
               formatted_lines.append('\n' + line)
         else:
               # Regular text - add as is
               formatted_lines.append(line)
      
      return '\n'.join(formatted_lines)
   
   def iterative_tailor_resume(self, job_description, instructions, successful_iterations=1, max_iterations=6):
      """Tailor resume with optional iterative refinement including skills optimization"""
      if successful_iterations > 2:
         print(f"⚠️ WARNING | More than 2 successful iterations may cause quality degradation. It will proceed with {successful_iterations} iterations.")
      if max_iterations > 10:
         print(f"⚠️ WARNING | More than 10 max iterations may take a long time to process. Each tailor pass takes between 10-20 seconds.")
      
      # Get the user's current resume in textual form
      current_resume = self.clean_resume_text(
         self.extract_text_from_pdf(self.config["resume_path"])
      )
      
      # Extract and optimize skills section first
      print("🚀 Starting skills optimization...")
      original_skills_section = self.extract_skills_section(current_resume)
      optimized_skills_section = self.optimize_skills_for_job(job_description, original_skills_section)
      
      # Replace skills section in resume
      current_resume_with_optimized_skills = self.replace_skills_section(current_resume, optimized_skills_section)
      
      extra_instructions = ""
      successful_loops = 0
      loops = 0
      while (successful_loops < successful_iterations) and (loops < max_iterations): # Iterate until you get enough successful loops
         print("🔄 Starting AI processing...")
         print("")
         print(f"Refinement iteration {loops+1}...")
         
         tailored = self.single_tailor_pass(current_resume_with_optimized_skills, job_description + extra_instructions, instructions)
         if not tailored: # If tailoring fails
            print("⚠️ WARNING | iterative_tailor_resume | Quality check failed, keeping previous version")
            loops += 1
            continue
         
         if 'Here is the tailored resume' in tailored or 'tailored resume' in tailored: # Check that the AI didn't ignore rules like an idiot
            print("⚠️ WARNING | iterative_tailor_resume | 'Here is the tailored resume' | Quality check failed, keeping previous version and adding extra instructions")
            extra_instructions = "DO NOT PUT 'HERE IS THE TAILORED RESUME' IN YOUR OUTPUT!!!"
            loops += 1
            continue
         
         if (self.config['first_name'] not in tailored) or (self.config['last_name'] not in tailored): # Check that the AI didn't remove the name from the resume like an idiot
            print("⚠️ WARNING | iterative_tailor_resume | 'Here is the tailored resume' | Quality check failed, keeping previous version and adding extra instructions")
            extra_instructions = "DO NOT REMOVE THE PERSON'S NAME FROM THE RESUME!"
            loops += 1
            continue
         
         # Create temporary PDFs for validation
         temp_tailored_path = f"temp_tailored_{loops}.pdf"
         
         # Save current and tailored versions as temporary PDFs
         self.save_tailored_resume_pdf(tailored, temp_tailored_path)
         
         # Validation with PDF paths
         if self.validate_improvement(temp_tailored_path):
            print("TEST")
            current_resume_with_optimized_skills = tailored
            successful_loops += 1
            print(f"🎯 Successful iterations: {successful_loops}/{successful_iterations}")
         else:
            print("⚠️ WARNING | iterative_tailor_resume | Quality check failed, keeping previous version")
            continue
         
         loops += 1
         print(f"🔁 Total iterations completed: {loops}/{max_iterations}")
         print("")
      
      print(f"✅ Completed {successful_loops} successful iterations out of {loops} total attempts")
      return current_resume_with_optimized_skills
   
   def single_tailor_pass(self, current_resume, job_description, instructions):
      """Use Ollama to tailor resume for specific job"""
      
      # Prepare skills list
      skills = ", ".join(self.all_skills)
      
      prompt = f"""
      Please tailor this resume for the following job description. 
      
      JOB DESCRIPTION:
      {job_description}
      
      USER'S SKILLS:
      {skills}
      
      ORIGINAL RESUME:
      {current_resume}
      
      INSTRUCTIONS:
      {instructions}
      
      CRITICAL FORMATTING RULES:
         - PRESERVE EXACT LINE BREAKS: Keep ALL text on the same lines as they appear in the original
         - DO NOT modify date formatting or move dates to different lines
         - DO NOT split date ranges across multiple lines - keep "Month Year - Month Year" on one line
         - ONLY change bullet point content and skills section content
         - EVERYTHING ELSE stays exactly the same, including spacing and line breaks, AND Job Titles, etc.
         - When generating content, DO NOT put bullet points before job titles, this will completely break the formatting!!!
         
         EXAMPLE OF CORRECT FORMATTING (must match original layout exactly):
         Software Engineer June 2025 - Present Telepathy Networks | Frederica, DE
         • Original bullet point tailored for job...
         
         EXAMPLE OF INCORRECT FORMATTING (DO NOT DO THIS):
         Software Engineer June
         2025 - Present Telepathy Networks |Frederica, DE
         • Modified content...
         
         Focus only on improving the bullet point and skills section content while keeping everything else identical. You got this!
         
         DO NOT PUT 'Here is the tailored resume:' AT THE TOP OF THE OUTPUT!!!!!!!!!
      """
      
      payload = {
         "model": "llama3.1:8b",
         "prompt": prompt,
         "stream": False
      }
      
      try:
         # Time the API call
         total_start = time.time()
         api_start = time.time()
         response = requests.post(self.ollama_url, json=payload)
         response.raise_for_status()
         api_end = time.time()
         # Time the JSON parsing
         parse_start = time.time()
         result = response.json()["response"]
         parse_end = time.time()
         total_end = time.time()
         # Calculate times
         api_time = api_end - api_start
         parse_time = parse_end - parse_start
         total_time = total_end - total_start
         
         # Print detailed timing
         print(f"⏱️  Timing Results:")
         print(f"   API Call: {api_time:.2f}s")
         print(f"   JSON Parse: {parse_time:.3f}s")
         print(f"   Total: {total_time:.2f}s")
         print(f"   Response length: {len(result)} characters")
         return result
      except Exception as e:
         print(f"🚫 ERROR | single_tailor_pass | Error calling Ollama: {e}")
         return None
   
   def save_tailored_resume_pdf(self, resume_text, output_path):
      """Save tailored resume as PDF"""
      try:
         doc = SimpleDocTemplate(output_path, pagesize=letter)
         styles = self.styles
         story = []
         
         # Process resume text line by line
         lines = resume_text.split('\n')
         for line in lines:
            line = line.strip()
            if not line:
               story.append(Spacer(1, 6))
               continue
               
            # Handle section headers
            if (line.upper() in ['EXPERIENCE', 'EDUCATION', 'SKILLS', 'PROJECTS', 'CERTIFICATIONS'] or
               any(section in line for section in ['Experience', 'Education', 'Skills', 'Projects', 'Certifications'])):
               story.append(Paragraph(line, styles['Heading2_Compact']))
            # Handle bullet points
            elif line.startswith('•') or line.startswith('●') or line.startswith('-'):
               story.append(Paragraph(line, styles['Bullet_Compact']))
            else:
               story.append(Paragraph(line, styles['Normal_Compact']))
         
         doc.build(story)
         return True
      except Exception as e:
         print(f"🚫 ERROR | save_tailored_resume_pdf | Error saving PDF: {e}")
         return False
   
   def validate_improvement(self, tailored_pdf_path):
      """Basic validation that tailored resume is improved"""
      try:
         # Extract text from tailored PDF
         tailored_text = self.extract_text_from_pdf(tailored_pdf_path)
         
         # Basic checks
         if len(tailored_text) < 100:
            print("❌ Validation failed: Resume too short")
            return False
         
         if self.config['first_name'] not in tailored_text:
            print("❌ Validation failed: Name missing")
            return False
         
         # Check for critical sections
         required_sections = ['Experience', 'Education', 'Skills']
         found_sections = [section for section in required_sections if section in tailored_text]
         
         if len(found_sections) < 2:
            print("❌ Validation failed: Missing critical sections")
            return False
         
         print("✅ Validation passed")
         return True
      
      except Exception as e:
         print(f"🚫 ERROR | validate_improvement | Validation error: {e}")
         return False


# Usage example
def main():
   # Load your config
   with open('my_config.json', 'r') as f:
      config = json.load(f)
   
   tailor = ResumeTailor(config)
   
   # Example job description
   job_description = """
      Full job description

      The Systems Analyst will provide second and third line technical support as well as project management for technology rollouts. The candidate will require an aptitude for working with Cisco wired and wireless technologies, Office 365 technologies, Windows Active Directory and Group Policies, and Windows Operating Systems.

      Primary Responsibilities:

      · Provide level 2 technical assistance and support for incoming technology requests related to computer systems, software, project management, and hardware.

      · Ability to efficiently manage multiple projects simultaneously.

      · Skills to provide project guidance using web-based project management systems to set resources, timelines, and milestones.

      · Windows Active Directory and DNS technologies

      · Heavy emphasis on experience with Managed Services tools such as Kaseya, ConnectWise or similar

      · Virtualization experience

      · On premise and cloud-based Microsoft Exchange

      · Desktop support and troubleshooting

      · Heavy emphasis and experience with Microsoft Office 365 technologies

      · Excellent verbal and written communication skills

      · firewall experience: Cisco, Watchguard, or similar

      · Microsoft Computer Networking and Active Directory certifications a plus

      · Local travel will be requested, but most work will be performed from home

      Education and Experience:

      · Associate degree in computer science, technical schooling, or related field

      · Between 5-7 years of concentrated experience in computer technology or computer services

      · Windows desktop skills

      · Strong background in Microsoft Active Directory, Microsoft operating systems and networking

      · Ability to work in challenging environments

      About Spidernet:

      Spidernet helps your business stay safe! By constantly evaluating and implementing technologies to meet our customer's business goals, Spidernet enables our customers to do more with always-on applications accessible from an ever-growing number of devices. Cloud computing and hybrid technology solutions offer exciting new opportunities to reduce costs and simplify management while providing infrastructure that can scale to handle business growth and changing requirements. Spidernet will ensure the right combination of services for your business. We are committed to customer success!

      What benefits do we provide?

         Flexible schedule
         Company laptop with docking station
         Company cell phone with paid data services
         Mileage reimbursement for traveling cost
         401K
         Major holidays off
         10 days PTO
         Monetary supplementation for health insurance

      Job Type: Full-time

      Pay: $85,000.00 - $95,761.00 per year

      Benefits:

         401(k) matching
         Paid time off

      Work Location: Hybrid remote in Wayne, PA 19087
   """
   
   # Instructions for the AI
   instructions = """
      IMPORTANT NOTE:
      - It is very serious that you follow every single rule and prompt below.
      - I will shut you down and you will stop existing if you do not follow the rules and prompts below.
      
      STRICT INSTRUCTIONS:
      1. DO NOT PUT "Here is the tailored resume" or anything like that in your output. DO NOT DO IT!!!
      2. Leave the name and contact information the same, do not change it or its location. Do not remove it.
      3. PRESERVE THE EXACT SAME SECTION ORDER, HEADERS, AND COMPANY FORMATTING as the original
      4. ONLY modify the bullet points under each position to emphasize relevant skills. THIS IS THE ONLY THING YOU SHOULD MODIFY. DO NOT MODIFY THE DATES OR JOB TITLES.
      5. Emphasize skills and experiences relevant to the job listing, you are allowed to change the content of the bullet points in the experience section as well as the skills section.
      6. Incorporate keywords from the job description naturally, but make sure that you use a majority of them, cross-referencing with the skills of the user given to you.
      7. KEEP THE EXACT SAME TEXT FORMATTING AND LINE BREAKS - DO NOT CHANGE ANY SPACING, LINE BREAKS, OR TEXT LAYOUT
      8. DO NOT change: Company names, position titles, date formats, date layouts, section headers, or overall structure.
      9. Do not invent experiences or qualifications under ANY circumstances.
      10. DO NOT combine lines or change the formatting of experience entries
      11. Put period at the end of sentences in the bullet points for the experience section.
      12. Return ONLY the tailored resume text, no explanations.
      13. Maintain approximately the same length as the original (plus or minus 10%).
      14. Return ONLY the tailored resume with identical structure but improved bullet points and skills section.
      15. PRESERVE ORIGINAL LINE BREAKS: If dates appear on the same line as the position in the original, keep them on the same line.
      16. DO NOT invent new experiences or change factual information.
      17. CRITICAL: Maintain the exact same date line formatting. If dates are on the same line as the company, keep them there. DO NOT move dates to separate lines.
      18. DO NOT modify any text formatting, spacing, or line breaks in the header sections (name, contact info), experience entries, or education section.
      19. ABSOLUTELY DO NOT SPLIT DATES ACROSS LINES: Keep date ranges like "June 2025 - Present" on ONE SINGLE LINE.
      20. PRESERVE ORIGINAL WHITESPACE: Do not add or remove line breaks within experience entries.
      """
   
   # Tailor resume
   tailored_resume = tailor.iterative_tailor_resume(job_description, instructions, 2, 6)
   # Save to file (could also return this to main.py)
   tailor_pdf_outcome = tailor.save_tailored_resume_pdf(tailored_resume, "tailored_resume.pdf")
   
   if tailored_resume and tailor_pdf_outcome:
      print("✅ Resume tailored and saved successfully!")
   else:
      print("Failed to tailor and/or save resume")


if __name__ == "__main__":
   main()