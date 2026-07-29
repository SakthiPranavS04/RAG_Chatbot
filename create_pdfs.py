from fpdf import FPDF

# PDF 1: AI_Basics.pdf
pdf1 = FPDF()
pdf1.add_page()
pdf1.set_font("Arial", size=12)
content1 = """Artificial Intelligence Basics

Artificial Intelligence (AI) is a branch of computer science that enables 
machines to perform tasks that normally require human intelligence.

Types of AI
Narrow AI
General AI
Super AI
Machine Learning

Machine Learning is a subset of Artificial Intelligence that allows 
systems to learn from data without explicit programming.

Deep Learning

Deep Learning uses artificial neural networks with multiple layers to 
solve complex problems.

Applications
Chatbots
Healthcare
Finance
Self-driving Cars
Recommendation Systems
Image Recognition

Advantages
Faster decision making
Automation
Reduced human effort

Disadvantages
High development cost
Job displacement
Ethical concerns"""

for line in content1.split('\n'):
    pdf1.cell(200, 8, txt=line, ln=True, align='L')
pdf1.output("data/AI_Basics.pdf")


# PDF 2: Student_Handbook.pdf
pdf2 = FPDF()
pdf2.add_page()
pdf2.set_font("Arial", size=12)
content2 = """Student Handbook
Attendance

Students must maintain at least 75% attendance.

Examination Rules

Students should carry their ID card during examinations.

Library

Library timings are from 9:00 AM to 6:00 PM.

Hostel Rules

Students must return to the hostel before 9:30 PM.

Dress Code

Students should wear formal attire on Mondays.

Leave Policy

Students should apply for leave through the department office.

Sports

Sports facilities are available from 4 PM to 7 PM.

Contact

For any queries, students can contact the academic office."""

for line in content2.split('\n'):
    pdf2.cell(200, 8, txt=line, ln=True, align='L')
pdf2.output("data/Student_Handbook.pdf")
