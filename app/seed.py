"""
Pre-seeds the IT-101 knowledge base with the teacher's syllabus on first startup.
Edit SEED_DOCS to match your actual course content.
"""

from app.rag import add_document, list_documents

SEED_DOCS = [
    {
        "subject": "it-101",
        "title": "Theory Syllabus — Chapters 1 to 11",
        "doc_type": "syllabus",
        "content": """
CHAPTER 1 — Introduction to Information Technology
Information Technology (IT) refers to the use of computers and software to manage information.
IT covers hardware, software, data, people, and procedures used to process, store, and communicate information.
Key components: Input, Processing, Output, Storage, Communication.

CHAPTER 2 — History & Development of Computers
Generation 1 (1940-56): Vacuum tubes. ENIAC was the first general-purpose computer.
Generation 2 (1956-63): Transistors replaced vacuum tubes. Faster, smaller, cheaper.
Generation 3 (1964-71): Integrated Circuits (IC). Multiple transistors on a chip.
Generation 4 (1971-present): Microprocessors. Intel 4004 was the first microprocessor.
Generation 5 (present/future): Artificial Intelligence, voice recognition, parallel processing.

CHAPTER 3 — Digital Computer Systems
A computer system has 4 main units:
- Input Unit: Accepts data from user (keyboard, mouse)
- Processing Unit (CPU): Processes data — has ALU (Arithmetic Logic Unit) and CU (Control Unit)
- Memory Unit: RAM (volatile, temporary) and ROM (non-volatile, permanent)
- Output Unit: Displays results (monitor, printer)

CHAPTER 4 — Input & Output Devices
Input Devices: Keyboard, Mouse, Scanner, Microphone, Webcam, Joystick, Light Pen, Barcode Reader, OMR, OCR, MICR
Output Devices: Monitor (CRT, LCD, LED), Printer (Dot Matrix, Inkjet, Laser), Speaker, Projector, Plotter

CHAPTER 5 — Storage Devices
Primary Storage: RAM (Random Access Memory) — volatile, fast, temporary
                ROM (Read Only Memory) — non-volatile, permanent
Secondary Storage: Hard Disk Drive (HDD), Solid State Drive (SSD), CD/DVD, USB Flash Drive, Memory Card
Storage units: Bit → Byte → KB → MB → GB → TB (each 1024x larger)

CHAPTER 6 — Computer Software
System Software: Operating System (Windows, Linux, macOS), Device Drivers, Utility Programs
Application Software: MS Office, Browsers, Games, Accounting Software
Programming Languages: Machine Language (binary), Assembly Language, High-Level Languages (Python, C++, Java)

CHAPTER 7 — Data Representation
Binary system: uses only 0 and 1
Bit = smallest unit; Byte = 8 bits
Number systems: Binary (base 2), Octal (base 8), Decimal (base 10), Hexadecimal (base 16)
ASCII: American Standard Code for Information Interchange — assigns numbers to characters
Unicode: extends ASCII to support all world languages including Urdu

CHAPTER 8 — Data Communication
Data communication: transfer of data between devices.
Components: Sender, Receiver, Medium (channel), Message, Protocol
Types of transmission: Simplex (one-way), Half-Duplex (both ways, not simultaneously), Full-Duplex (both ways simultaneously)
Transmission media: Wired (Twisted Pair, Coaxial, Fiber Optic), Wireless (Radio, Microwave, Satellite, Infrared)
Bandwidth: amount of data transferred per second (bps, Kbps, Mbps, Gbps)

CHAPTER 9 — Computer Networking
Network: two or more computers connected to share resources.
Types by size: PAN, LAN, MAN, WAN
Network topologies: Bus, Star, Ring, Mesh, Hybrid
Network devices: Hub, Switch, Router, Modem, Bridge, Repeater
Protocols: TCP/IP, HTTP, FTP, SMTP, DNS

CHAPTER 10 — The Internet
Internet: global network of networks using TCP/IP protocol.
WWW (World Wide Web): collection of web pages accessed via browsers.
URL: Uniform Resource Locator — web address format: protocol://domain/path
Services: Email, FTP, Telnet, VoIP, Social Media, E-commerce, Cloud Computing
ISP: Internet Service Provider connects users to the internet.
Search engines: Google, Bing — index and search web pages.

CHAPTER 11 — Security, Copyright & The Law
Computer security threats: Virus, Worm, Trojan Horse, Spyware, Ransomware, Phishing
Security measures: Antivirus software, Firewall, Strong passwords, Encryption, Backup
Copyright: legal protection for creators of original work.
Piracy: illegal copying and distribution of software.
Cybercrime: illegal activities using computers — hacking, identity theft, cyberbullying.
Computer ethics: responsible and moral use of computers and internet.
"""
    },
    {
        "subject": "it-101",
        "title": "MS Word Practical Tasks 1–15",
        "doc_type": "practical",
        "content": """
PRACTICAL 1 — Create a simple document in MS Word
Steps:
1. Open MS Word: Start → All Programs → Microsoft Office → Microsoft Word
2. Type your text using the keyboard
3. Save: File → Save As → choose location → type filename → click Save
Key concepts: Document, Font, Paragraph, Save, File format (.docx)

PRACTICAL 2 — Letter to father requesting Rs. 14000 for purchasing books
Format of a formal letter:
- Your address (top right)
- Date below your address
- Recipient address (left side)
- Subject line: bold, underlined
- Salutation: "Respected Father,"
- Body: 2-3 paragraphs explaining the need
- Closing: "Your loving son/daughter, [Your Name]"
Steps: Type letter → Format using Home tab → Bold the subject → Align text properly

PRACTICAL 3 — Creating lines representing left and right margins
Steps:
1. Page Layout tab → Margins → Custom Margins
2. Set Left margin and Right margin values
3. To draw a line: Insert → Shapes → Line
4. Or use borders: Home → Paragraph → Borders → Bottom Border

PRACTICAL 4 — Write a passage, insert header, footer, columns, and clip art
Header/Footer: Insert tab → Header → choose style → type text → Close Header and Footer
Columns: Page Layout → Columns → choose number of columns
Clip Art (older Word): Insert → Clip Art → search and insert
Online Pictures (newer Word): Insert → Online Pictures → search

PRACTICAL 5 — Formulas: Area=2πR², Mean=ΣX/n, SinΘ+CosΘ, H₂O
Use Equation Editor: Insert → Equation → Insert New Equation
Or use Insert → Symbol for special characters (π, Σ, Θ)
Area formula: A = 2πR² (π ≈ 3.14159, R = radius)
Mean formula: x̄ = ΣX/n (sum of all values divided by count)
Subscript (H₂O): Select the 2 → Home → Font group → click X₂ (Subscript)

PRACTICAL 6 — Writing a paragraph, copying and pasting
Copy: Select text → Ctrl+C
Paste: Ctrl+V
Cut: Ctrl+X
Undo: Ctrl+Z
Redo: Ctrl+Y
Select All: Ctrl+A

PRACTICAL 7 — Application to librarian requesting books
Format: Same as formal letter. Address to: The Librarian, [College Name]
Subject: Request for Issuance of Books
Body: Mention your name, class, roll number, and list of books needed

PRACTICAL 8 — Writing in columns with different font sizes, name, and Drop Cap
Font size: Select text → Home tab → Font Size box → type size (e.g. 14, 18, 24)
Drop Cap: Click in paragraph → Insert tab → Drop Cap → Dropped or In Margin

PRACTICAL 9 — Application to principal asking for leave certificate
Subject: Request for Leave Certificate
Mention: your name, class, roll number, reason for leave, duration

PRACTICAL 10 — Create a Curriculum Vitae (CV)
CV Sections:
1. Personal Information (Name, DOB, Address, Phone, Email)
2. Objective Statement
3. Education (in reverse order — latest first)
4. Skills
5. Experience (if any)
6. References
Use tables for clean layout: Insert → Table

PRACTICAL 11 — Create an Award Certificate
Steps:
1. Page Layout → Orientation → Landscape
2. Insert → Text Box → draw a text box for the border effect
3. Format → Borders & Shading for decorative border
4. Insert → WordArt for the title "Certificate of Achievement"
5. Type the certificate text, format with large decorative fonts

PRACTICAL 12 — Application to Principal for 7 days leave
Format: Formal application. Include specific dates, reason, and request for approval.

PRACTICAL 13 — Application to librarian for issuance of books
Similar to Practical 7 — list specific book titles and authors needed.

PRACTICAL 14 — Invitation card for friends
Steps:
1. Use a text box or table as the card border
2. Insert → WordArt for the event title
3. Include: Event name, Date, Time, Venue, RSVP details
4. Decorate with Insert → Shapes or Online Pictures

PRACTICAL 15 — Write a passage and apply header and footer
Header: Insert → Header → Edit Header → type your text (e.g. your name, subject)
Footer: Insert → Footer → Edit Footer → Insert Page Number
Page Number: Insert → Page Number → choose position
"""
    },
    {
        "subject": "it-101",
        "title": "MS Excel Practical Tasks 16–30",
        "doc_type": "practical",
        "content": """
PRACTICAL 16 — Creating Payroll spreadsheet for employees
Key columns: Employee Name, Basic Salary, Allowances, Deductions, Net Salary
Formula for Net Salary: =Basic + Allowances - Deductions
Example: If Basic in B2, Allowances in C2, Deductions in D2:
Net Salary = =B2+C2-D2
Use SUM for totals: =SUM(E2:E10)

PRACTICAL 17 — Spreadsheet for calculating daily wages
Daily Wage = Hourly Rate × Hours Worked
Formula: =B2*C2 (if hourly rate in B2, hours in C2)
Weekly Total: =SUM(D2:D8)

PRACTICAL 18 — Attendance Sheet
Columns: Student Name, then dates as columns
Mark P (Present), A (Absent), L (Late)
Count Present: =COUNTIF(B2:AF2,"P")
Total days: =COUNT(B1:AF1)
Attendance %: =(Present/Total)*100

PRACTICAL 19 — Marks Sheet with grade and ascending list
Total Marks formula: =SUM(B2:F2)
Percentage: =(G2/Total_Max)*100
Grade using IF: =IF(H2>=80,"A",IF(H2>=70,"B",IF(H2>=60,"C",IF(H2>=50,"D","F"))))
Sort ascending: Select data → Data tab → Sort → choose column → Smallest to Largest

PRACTICAL 20 — Complete Marks Sheet with percentage and grade
Same as Practical 19 but with more subjects.
Add AVERAGE: =AVERAGE(B2:F2)
MAX marks: =MAX(B2:F2)
MIN marks: =MIN(B2:F2)

PRACTICAL 21 — Marks sheet with missing marks (handling blanks)
Use IFERROR to handle blank cells:
=IFERROR(SUM(B2:F2)/COUNTA(B2:F2)*100, "Incomplete")
COUNTA counts non-empty cells.

PRACTICAL 22 — Expense sheet with graphs/charts
After creating data table:
Select the data → Insert tab → Charts → choose chart type (Bar, Pie, Line)
Chart Title: click on chart title to edit
Format chart: right-click on chart elements to format

PRACTICAL 23 — Electric Bill
Key fields: Previous Reading, Current Reading, Units Consumed, Rate per Unit, Amount
Units = Current Reading - Previous Reading
Amount = Units × Rate
Tax = Amount × Tax Rate
Total = Amount + Tax
Formulas: =C2-B2, =D2*E2, =F2*0.17, =F2+G2

PRACTICAL 24 — Time Table of College
Create a table: days as rows, periods as columns
Use Merge Cells for breaks: Select cells → Home → Merge & Center
Add borders: Select all → Home → Borders → All Borders

PRACTICAL 25 — Expenditure Sheet of Different Provinces
Provinces as rows (Punjab, Sindh, KPK, Balochistan)
Categories as columns
Use SUM for totals, create bar chart for comparison

PRACTICAL 26 — Expense Sheet of Pakistan Printing Press
Include: Item, Quantity, Unit Price, Total Price
Total = Quantity × Unit Price: =B2*C2
Grand Total: =SUM(D2:D20)

PRACTICAL 27 — Sui Gas Utility Bill
Fields: Consumer Name, Account No, Previous Reading, Current Reading
Units = Current - Previous
Slab rates: use nested IF for different rate slabs
First 50 units: Rs. X, Next 100 units: Rs. Y, etc.

PRACTICAL 28 — Profit Sheet of Pak-Suzuki Motors
Columns: Model, Units Sold, Sale Price, Total Revenue, Cost Price, Total Cost, Profit
Profit = Total Revenue - Total Cost
Profit % = (Profit/Total Cost)*100

PRACTICAL 29 — Scholarship Statement
Columns: Student Name, CGPA, Merit Rank, Scholarship %
Scholarship using IF: =IF(B2>=3.8,"50%",IF(B2>=3.5,"25%",IF(B2>=3.0,"10%","None")))

PRACTICAL 30 — PTCL Utility Bill
Fields: Customer Name, Phone No, Call Duration (minutes), Rate/minute, Call Charges
Line Rent: fixed monthly charge
Taxes (GST 17%): =Total*0.17
Net Payable = Call Charges + Line Rent + GST
"""
    },
    {
        "subject": "it-101",
        "title": "Key Formulas & Shortcuts Reference",
        "doc_type": "formula",
        "content": """
MS WORD KEY SHORTCUTS:
Ctrl+B = Bold
Ctrl+I = Italic
Ctrl+U = Underline
Ctrl+C = Copy | Ctrl+V = Paste | Ctrl+X = Cut
Ctrl+Z = Undo | Ctrl+Y = Redo
Ctrl+S = Save | Ctrl+P = Print
Ctrl+A = Select All
Ctrl+F = Find | Ctrl+H = Replace

MS EXCEL KEY FUNCTIONS:
=SUM(range)         — Add all numbers: =SUM(A1:A10)
=AVERAGE(range)     — Find mean: =AVERAGE(B1:B10)
=MAX(range)         — Highest value: =MAX(C1:C10)
=MIN(range)         — Lowest value: =MIN(D1:D10)
=COUNT(range)       — Count numbers: =COUNT(A1:A20)
=COUNTA(range)      — Count non-empty cells
=COUNTIF(range,criteria) — Count cells matching criteria: =COUNTIF(A1:A20,"P")
=IF(condition,true,false) — Conditional: =IF(A1>=50,"Pass","Fail")
=ROUND(number,digits)    — Round off: =ROUND(3.14159,2) → 3.14

GRADE FORMULA (standard):
=IF(A1>=80,"A",IF(A1>=70,"B",IF(A1>=60,"C",IF(A1>=50,"D","F"))))

PERCENTAGE FORMULA:
=(obtained_marks/total_marks)*100

MATHEMATICAL FORMULAS:
Area of Circle = πR²     (π ≈ 3.14159)
Area of Rectangle = Length × Width
Area of Triangle = ½ × Base × Height
Mean (Average) = ΣX/n   (Sum of values divided by count)
sin²θ + cos²θ = 1       (Pythagorean identity)
Water molecule = H₂O    (2 Hydrogen + 1 Oxygen)

COMPUTER UNITS:
1 Byte = 8 Bits
1 KB (Kilobyte) = 1024 Bytes
1 MB (Megabyte) = 1024 KB
1 GB (Gigabyte) = 1024 MB
1 TB (Terabyte) = 1024 GB
"""
    },
]


def seed_it_curriculum() -> None:
    """Load IT-101 curriculum if not already loaded."""
    existing = list_documents("it-101")
    if existing:
        return  # Already seeded
    for doc in SEED_DOCS:
        add_document(
            subject=doc["subject"],
            title=doc["title"],
            content=doc["content"],
            doc_type=doc["doc_type"],
        )
    print("✅ IT-101 curriculum seeded.")
