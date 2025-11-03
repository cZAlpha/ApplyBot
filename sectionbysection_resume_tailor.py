import requests
import json
import PyPDF2
import os
import time
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from typing import Dict, List
import re


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
      
      # End the timing and print
      init_end = time.time()
      total_time = init_end - init_start
      print(f"ResumeTailor initalized in {total_time:.2f}s")
      print("")
   
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
   
   def parse_resume_into_sections(self, resume_text: str) -> Dict[str, str]:
      """Parse resume into structured sections for targeted processing"""
      sections = {
         'contact': '',
         'summary': '', 
         'experience': '',
         'skills': '',
         'education': '',
         'projects': '',
         'certifications': ''
      }
      
      # Common section headers (case insensitive)
      section_headers = {
         'experience': ['experience', 'work experience', 'employment'],
         'skills': ['skills', 'technical skills', 'competencies'],
         'education': ['education', 'academic'],
         'projects': ['projects', 'personal projects'],
         'certifications': ['certifications', 'licenses'],
         'summary': ['summary', 'professional summary']
      }
      
      lines = resume_text.split('\n')
      current_section = 'contact'  # Everything before first header is contact/summary
      section_content = []
      
      for line in lines:
         line_stripped = line.strip()
         if not line_stripped:
               continue
               
         # Check if this line is a section header
         is_header = False
         for section, headers in section_headers.items():
               if any(header in line_stripped.lower() for header in headers):
                  # Save previous section
                  if section_content and current_section:
                     sections[current_section] = '\n'.join(section_content)
                  
                  # Start new section
                  current_section = section
                  section_content = [line_stripped]  # Include the header
                  is_header = True
                  break
         
         if not is_header:
               section_content.append(line_stripped)
      
      # Save the final section
      if section_content and current_section:
         sections[current_section] = '\n'.join(section_content)
      
      self.parsed_resume = sections
      return sections
   
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
   

   def tailor_experience_section(self, experience_text: str, job_description: str, skills: str) -> str:
      """Tailor ONLY the experience section - most important part"""
      prompt = f"""
      TAILOR ONLY THE EXPERIENCE BULLET POINTS. DO NOT MODIFY ANYTHING ELSE.

      JOB DESCRIPTION:
      {job_description[:1500]}  # Truncated to save tokens

      RELEVANT SKILLS: {skills}

      ORIGINAL EXPERIENCE SECTION:
      {experience_text}

      CRITICAL RULES:
      1. ONLY modify the bullet points (lines starting with •, ●, or -)
      2. PRESERVE ALL job titles, company names, and date lines EXACTLY as written
      3. Keep the exact same line breaks and spacing
      4. Emphasize skills from the job description naturally
      5. Do not invent experiences or qualifications
      6. Keep approximately the same number of bullet points per position
      7. Return ONLY the modified experience section text

      Focus on making bullet points more achievement-oriented and relevant to the job.
      """
      
      return self._call_llm_safely(prompt, "experience")
   
   def tailor_skills_section(self, skills_text: str, job_description: str, user_skills: List[str]) -> str:
      """Tailor ONLY the skills section"""
      prompt = f"""
      TAILOR ONLY THE SKILLS SECTION. Reorder and emphasize relevant skills.

      JOB DESCRIPTION:
      {job_description[:1000]}  # Even shorter for skills

      USER'S SKILLS: {', '.join(user_skills)}

      ORIGINAL SKILLS SECTION:
      {skills_text}

      RULES:
      1. Reorder skills to put most relevant ones first
      2. You may group related skills together
      3. Keep the same general format (bullets, categories, etc.)
      4. Add any missing skills from USER'S SKILLS that are relevant to the job
      5. Remove obviously irrelevant skills if space is tight
      6. Return ONLY the modified skills section
      """
      
      return self._call_llm_safely(prompt, "skills")

   def _call_llm_safely(self, prompt: str, section_name: str) -> str:
      """Safe wrapper for LLM calls with error handling"""
      payload = {
         "model": "llama3.1:8b",
         "prompt": prompt,
         "stream": False
      }
      
      try:
         print(f"🔄 Tailoring {section_name} section...")
         response = requests.post(self.ollama_url, json=payload)
         response.raise_for_status()
         result = response.json()["response"]
         
         # Basic quality check
         if len(result.strip()) < 10:
               print(f"⚠️  LLM returned empty response for {section_name}, using original")
               return None
               
         return result
      except Exception as e:
         print(f"🚫 Error tailoring {section_name}: {e}")
         return None


   def iterative_tailor_resume(self, job_description: str, instructions: str, 
                              successful_iterations: int = 1, max_iterations: int = 6) -> str:
      """NEW: Targeted iterative tailoring with section-by-section processing"""
      
      # Extract and parse resume once
      current_resume = self.clean_resume_text(
         self.extract_text_from_pdf(self.config["resume_path"])
      )
      
      sections = self.parse_resume_into_sections(current_resume)
      skills_list = self.config["skill_keywords"]
      
      best_resume = current_resume
      best_score = 0
      
      for iteration in range(max_iterations):
         print(f"🔄 Iteration {iteration + 1}/{max_iterations}")
         
         # Tailor key sections sequentially
         tailored_sections = sections.copy()
         
         # 1. Tailor Experience (most important)
         if sections.get('experience'):
               new_experience = self.tailor_experience_section(
                  sections['experience'], job_description, ', '.join(skills_list)
               )
               if new_experience and self._validate_section(sections['experience'], new_experience):
                  tailored_sections['experience'] = new_experience
         
         # 2. Tailor Skills
         if sections.get('skills'):
               new_skills = self.tailor_skills_section(
                  sections['skills'], job_description, skills_list
               )
               if new_skills and self._validate_section(sections['skills'], new_skills):
                  tailored_sections['skills'] = new_skills
         
         # Reassemble resume
         tailored_resume = self._reassemble_resume(tailored_sections)
         
         # Validate improvement
         temp_path = f"temp_iteration_{iteration}.pdf"
         self.save_tailored_resume_pdf(tailored_resume, temp_path)
         
         if self.validate_improvement(temp_path):
               current_score = self._calculate_relevance_score(tailored_resume, job_description)
               if current_score > best_score:
                  best_resume = tailored_resume
                  best_score = current_score
                  print(f"🎯 New best score: {best_score:.2f}")
         
         # Early exit if we have enough good iterations
         if iteration + 1 >= successful_iterations and best_score > 0:
               break
      
      print(f"✅ Best relevance score achieved: {best_score:.2f}")
      return best_resume
   
   def _validate_section(self, original: str, new: str) -> bool:
      """Validate that a tailored section maintains quality"""
      if not new or len(new) < len(original) * 0.3:
         return False
      
      # Check for forbidden phrases
      forbidden_phrases = [
         "here is the tailored", "tailored resume", "i have tailored", 
         "modified version", "based on your job description"
      ]
      if any(phrase in new.lower() for phrase in forbidden_phrases):
         return False
         
      return True

   def _reassemble_resume(self, sections: Dict[str, str]) -> str:
      """Reassemble sections into a complete resume"""
      # Define assembly order
      order = ['contact', 'summary', 'experience', 'skills', 'education', 'projects', 'certifications']
      
      resume_parts = []
      for section in order:
         if sections.get(section):
               resume_parts.append(sections[section])
      
      return '\n\n'.join(resume_parts)

   def _calculate_relevance_score(self, resume_text: str, job_description: str) -> float:
      """Calculate a simple relevance score between resume and job description"""
      job_keywords = set(re.findall(r'\b\w+\b', job_description.lower()))
      resume_keywords = set(re.findall(r'\b\w+\b', resume_text.lower()))
      
      common_keywords = job_keywords.intersection(resume_keywords)
      return len(common_keywords) / len(job_keywords) if job_keywords else 0
   
   def validate_improvement(self, new_resume_pdf):
      """Enhanced quality checks including page count validation"""
      # Check length hasn't changed dramatically
      original_text = self.extract_text_from_pdf(self.config['resume_path'])
      new_text = self.extract_text_from_pdf(new_resume_pdf)
      
      original_length = len(original_text.split())
      new_length = len(new_text.split())
      length_ratio = new_length / original_length if original_length > 0 else 1
      
      # Allow 25% variation in either direction
      if length_ratio < 0.75 or length_ratio > 1.25:
         print(f"🚫 ERROR | validate_improvement | Validation failed: Length changed dramatically (original: {original_length} words, new: {new_length} words, ratio: {length_ratio:.2f})")
         return False
      
      # Check key sections are preserved
      key_sections = ['EXPERIENCE', 'EDUCATION', 'SKILLS', 'PROJECTS']
      original_sections = []
      new_sections = []
      
      for section in key_sections:
         if section in original_text.upper():
            original_sections.append(section)
         if section in new_text.upper():
            new_sections.append(section)
      
      # Ensure all original key sections are preserved in the new resume
      missing_sections = set(original_sections) - set(new_sections)
      if missing_sections:
         print(f"🚫 ERROR | validate_improvement | Validation failed: Missing key sections: {missing_sections}")
         return False
      
      # Check page count by creating temporary PDFs and comparing
      original_pages = self.get_pdf_page_count(self.config['resume_path'])
      new_pages = self.get_pdf_page_count(new_resume_pdf)
      
      print(f"📄 Page count - Original: {original_pages}, New: {new_pages}") # DEBUG/TESTING ONLY
      
      # Allow some flexibility (within 1 page difference)
      if abs(original_pages - new_pages) > 1:
         print(f"🚫 ERROR | validate_improvement | Validation failed: Page count did not match! (Original: {original_pages} vs New: {new_pages})")
         return False
      
      print("✅ Validation passed: Page count and structure maintained")
      return True
   
   def get_page_count_from_text(self, text):
      """Estimate page count by creating a temporary PDF and counting pages"""
      try:
         # Create a temporary PDF file
         temp_path = "temp_page_count.pdf"
         
         # Create PDF document with same compact settings as final PDF
         doc = SimpleDocTemplate(temp_path, pagesize=letter,
                                 rightMargin=54, leftMargin=54,
                                 topMargin=36, bottomMargin=36)
         
         # Build story (content) - same logic as save_tailored_resume_pdf
         story = []
         lines = text.split('\n')
         
         for line in lines:
               line = line.strip()
               if not line:
                  story.append(Spacer(1, 4))
                  continue
               
               # Handle section headers
               if (line.upper() in ['EXPERIENCE', 'EDUCATION', 'SKILLS', 'PROJECTS', 'CERTIFICATIONS'] or
                  any(section in line for section in ['Experience', 'Education', 'Skills', 'Projects', 'Certifications'])):
                  story.append(Paragraph(f"<b>{line}</b>", self.styles['Heading2_Compact']))
                  story.append(Spacer(1, 4))
               
               # Handle bullet points
               elif line.startswith('•') or line.startswith('●') or line.startswith('-'):
                  story.append(Paragraph(f"• {line[1:].strip()}", self.styles['Bullet_Compact']))
               
               # Regular text
               else:
                  story.append(Paragraph(line, self.styles['Normal_Compact']))
                  story.append(Spacer(1, 4))
         
         # Build the PDF to count pages
         doc.build(story)
         
         # Count pages in the generated PDF
         with open(temp_path, 'rb') as file:
               reader = PyPDF2.PdfReader(file)
               page_count = len(reader.pages)
         
         # Clean up temporary file
         try:
               os.remove(temp_path)
         except:
               pass  # Ignore cleanup errors
         
         return page_count
         
      except Exception as e:
         print(f"⚠️ Error estimating page count: {e}")
         # Fallback: estimate pages based on text length (rough approximation)
         estimated_pages = max(1, len(text) // 2000)  # Increased to ~2000 chars per page with compact formatting
         return estimated_pages
   
   def get_pdf_page_count(self, source):
      """Get page count from either text or PDF file path"""
      if isinstance(source, str) and source.endswith('.pdf'):
         # Source is a PDF file path
         try:
               with open(source, 'rb') as file:
                  reader = PyPDF2.PdfReader(file)
                  return len(reader.pages)
         except Exception as e:
               print(f"⚠️ WARNING | get_pdf_page_count | Error reading PDF page count: {e}. Falling back to get_page_count_from_text()")
               # Fallback: extract text and use text-based estimation
               text = self.extract_text_from_pdf(source)
               return self.get_page_count_from_text(text)
      else:
         # Source is text
         return self.get_page_count_from_text(source)
   
   def save_tailored_resume_pdf(self, tailored_text, output_path):
      """Save the tailored resume as a proper PDF with compact formatting"""
      try:
         # Create PDF document with tighter margins
         doc = SimpleDocTemplate(output_path, pagesize=letter,
                                 rightMargin=12,
                                 leftMargin=12,
                                 topMargin=12,
                                 bottomMargin=12)
         
         # Build story (content)
         story = []
         
         # Parse the tailored text and convert to PDF elements
         lines = tailored_text.split('\n')
         for line in lines:
               line = line.strip()
               if not line:
                  story.append(Spacer(1, 4))  # Smaller spacer
                  continue
               
               # Handle section headers
               if (line.upper() in ['EXPERIENCE', 'EDUCATION', 'SKILLS', 'PROJECTS', 'CERTIFICATIONS'] or
                  any(section in line for section in ['Experience', 'Education', 'Skills', 'Projects', 'Certifications'])):
                  story.append(Paragraph(f"<b>{line}</b>", self.styles['Heading2_Compact']))
                  story.append(Spacer(1, 4))
               
               # Handle bullet points
               elif line.startswith('•') or line.startswith('●') or line.startswith('-'):
                  story.append(Paragraph(f"• {line[1:].strip()}", self.styles['Bullet_Compact']))
               
               # Regular text
               else:
                  story.append(Paragraph(line, self.styles['Normal_Compact']))
                  story.append(Spacer(1, 4))
         
         # Build PDF
         doc.build(story)
         print(f"✅ Tailored resume saved as PDF: {output_path}")
         return True
         
      except Exception as e:
         print(f"🚫 ERROR | save_tailored_resume_pdf | Error creating PDF: {e}")
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


# ORIGINAL PROMPT INSTRUCTIONS:
# Instructions:
#       1. Keep the same overall structure and format. Do not change the order of the sections UNDER ANY CIRCUMSTANCE.
#       2. Emphasize skills and experiences relevant to the job listing, you are allowed to change the content of the bullet points in the experience section as well as the skills section.
#       3. Incorporate keywords from the job description naturally, but make sure that you use a majority of them, cross-referencing with the skills of the user given to you.
#       4. Maintain professional tone and factual accuracy at all times.
#       5. Do not invent experiences or qualifications under ANY circumstances.
#       6. Return ONLY the tailored resume text, no explanations.
#       7. DO NOT PUT ANY NOTES AT THE END. The ONLY thing you should output is the tailored resume content, I do not want your comments, notes, concerns, etc.
#       8. Put period at the end of sentences in the bullet points for the experience section.
#       9. DO NOT PUT "Here is the tailored resume" or anything like that in your output. Your output should literaly be what could be written directly into a resume and sent to a hiring manageer.