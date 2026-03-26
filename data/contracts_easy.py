"""
Easy task data: 5 employment contracts for clause identification.

Each contract has 5-7 sections of realistic legal text with ground truth
clause type labels.
"""

EASY_CONTRACTS = [
    # ═══════════════════════════════════════════════════════
    # CONTRACT 1: Software Engineer — TechNova Inc.
    # ═══════════════════════════════════════════════════════
    {
        "contract_id": "emp_001",
        "title": "Software Engineer Employment Agreement — TechNova Inc.",
        "parties": {"employer": "TechNova Inc.", "employee": "Sarah Chen"},
        "sections": [
            {
                "index": 0,
                "heading": "1. POSITION AND DUTIES",
                "text": (
                    "Employee shall serve as Senior Software Engineer reporting to the "
                    "Vice President of Engineering. Employee shall perform duties as "
                    "reasonably assigned including software development, code review, "
                    "system architecture design, and mentoring junior engineers. Employee "
                    "shall devote full working time and attention to Company business and "
                    "shall not engage in any outside employment without prior written "
                    "consent of the Company. Employee shall comply with all Company policies "
                    "and procedures as may be established from time to time."
                ),
                "clause_type": "position",
            },
            {
                "index": 1,
                "heading": "2. COMPENSATION AND BENEFITS",
                "text": (
                    "Company shall pay Employee a base annual salary of $145,000, payable "
                    "in bi-weekly installments of $5,576.92, less applicable withholdings "
                    "and deductions. Employee shall be eligible for an annual performance "
                    "bonus of up to 15% of base salary, subject to achievement of "
                    "performance targets established by the VP of Engineering. Bonus "
                    "payments, if any, shall be made no later than March 15 of the "
                    "following calendar year. Salary reviews will be conducted annually "
                    "in January, though the Company is under no obligation to increase "
                    "Employee's compensation."
                ),
                "clause_type": "compensation",
            },
            {
                "index": 2,
                "heading": "3. TERMINATION",
                "text": (
                    "Either party may terminate this Agreement at any time, with or "
                    "without cause, upon thirty (30) calendar days' written notice to "
                    "the other party. The Company may, at its sole discretion, elect to "
                    "provide thirty (30) days' base salary in lieu of the notice period. "
                    "Upon termination, Employee shall promptly return all Company property, "
                    "including but not limited to laptops, access badges, and any documents "
                    "containing confidential information. Any accrued but unused vacation "
                    "days shall be paid out in the final paycheck in accordance with "
                    "applicable state law."
                ),
                "clause_type": "termination",
            },
            {
                "index": 3,
                "heading": "4. CONFIDENTIALITY AND NON-DISCLOSURE",
                "text": (
                    "Employee acknowledges that during the course of employment, Employee "
                    "will have access to and become acquainted with trade secrets, "
                    "proprietary data, and confidential information belonging to the "
                    "Company, including but not limited to source code, algorithms, "
                    "customer lists, financial data, and business strategies. Employee "
                    "agrees to hold all such Confidential Information in strict confidence "
                    "and shall not disclose, publish, or otherwise disseminate any "
                    "Confidential Information to any third party during or after the term "
                    "of employment. This obligation shall survive termination of this "
                    "Agreement for a period of five (5) years."
                ),
                "clause_type": "confidentiality",
            },
            {
                "index": 4,
                "heading": "5. INTELLECTUAL PROPERTY ASSIGNMENT",
                "text": (
                    "Employee hereby assigns to the Company all right, title, and interest "
                    "in and to any inventions, discoveries, designs, developments, "
                    "improvements, copyrightable works, and trade secrets conceived, "
                    "developed, or reduced to practice by Employee, solely or jointly with "
                    "others, during the term of employment that relate to the Company's "
                    "current or anticipated business activities. Employee agrees to execute "
                    "any documents necessary to perfect the Company's rights in such "
                    "intellectual property. This assignment does not apply to inventions "
                    "developed entirely on Employee's own time without use of Company "
                    "resources, provided they do not relate to the Company's business."
                ),
                "clause_type": "ip_assignment",
            },
            {
                "index": 5,
                "heading": "6. NON-COMPETE COVENANT",
                "text": (
                    "For a period of twelve (12) months following the termination of "
                    "employment, Employee shall not, directly or indirectly, engage in, "
                    "own, manage, operate, or be employed by any business that competes "
                    "with the Company's enterprise software products within a fifty (50) "
                    "mile radius of the Company's principal office in San Jose, California. "
                    "Employee acknowledges that this restriction is reasonable in scope and "
                    "duration and is necessary to protect the Company's legitimate business "
                    "interests. In the event of a breach, the Company shall be entitled to "
                    "injunctive relief in addition to any other remedies available at law."
                ),
                "clause_type": "non_compete",
            },
            {
                "index": 6,
                "heading": "7. GOVERNING LAW AND JURISDICTION",
                "text": (
                    "This Agreement shall be governed by and construed in accordance with "
                    "the laws of the State of California, without regard to its conflict of "
                    "laws principles. Any dispute arising out of or relating to this "
                    "Agreement shall be resolved exclusively in the state or federal courts "
                    "located in Santa Clara County, California. The parties hereby consent "
                    "to the personal jurisdiction of such courts and waive any objection "
                    "to venue therein. The prevailing party in any such proceeding shall "
                    "be entitled to recover reasonable attorneys' fees and costs."
                ),
                "clause_type": "governing_law",
            },
        ],
        "ground_truth": {
            "0": "position",
            "1": "compensation",
            "2": "termination",
            "3": "confidentiality",
            "4": "ip_assignment",
            "5": "non_compete",
            "6": "governing_law",
        },
    },

    # ═══════════════════════════════════════════════════════
    # CONTRACT 2: Marketing Manager — BrightPath Media
    # ═══════════════════════════════════════════════════════
    {
        "contract_id": "emp_002",
        "title": "Marketing Manager Employment Agreement — BrightPath Media LLC",
        "parties": {"employer": "BrightPath Media LLC", "employee": "James Rodriguez"},
        "sections": [
            {
                "index": 0,
                "heading": "1. POSITION AND RESPONSIBILITIES",
                "text": (
                    "Employee is hereby appointed to the position of Marketing Manager, "
                    "reporting directly to the Chief Marketing Officer. Employee's duties "
                    "shall include developing and executing marketing campaigns, managing "
                    "a team of four (4) marketing coordinators, overseeing digital "
                    "advertising budgets in excess of $500,000 per quarter, and maintaining "
                    "relationships with key media partners. Employee shall perform such "
                    "other duties as may be reasonably assigned and consistent with "
                    "Employee's position."
                ),
                "clause_type": "position",
            },
            {
                "index": 1,
                "heading": "2. COMPENSATION",
                "text": (
                    "Employee shall receive an annual base salary of $112,000, payable in "
                    "semi-monthly installments on the 1st and 15th of each calendar month. "
                    "In addition, Employee shall be eligible for a quarterly performance "
                    "bonus of up to $7,500, contingent upon achieving the KPI targets "
                    "outlined in Exhibit B attached hereto. Employee shall also receive a "
                    "one-time signing bonus of $10,000, payable within thirty (30) days of "
                    "the Effective Date, subject to repayment on a pro-rata basis if "
                    "Employee voluntarily resigns within twelve (12) months."
                ),
                "clause_type": "compensation",
            },
            {
                "index": 2,
                "heading": "3. BENEFITS AND PERQUISITES",
                "text": (
                    "Employee shall be entitled to participate in all employee benefit "
                    "programs offered by the Company, including medical, dental, and vision "
                    "insurance, 401(k) retirement plan with 4% employer match, and life "
                    "insurance coverage equal to two times (2x) Employee's annual base "
                    "salary. Employee shall receive twenty (20) days of paid time off per "
                    "calendar year, accruing at a rate of 1.67 days per month. Additionally, "
                    "Employee shall receive a monthly cell phone stipend of $75 and an "
                    "annual professional development allowance of $3,000."
                ),
                "clause_type": "benefits",
            },
            {
                "index": 3,
                "heading": "4. CONFIDENTIALITY",
                "text": (
                    "Employee agrees that all marketing strategies, customer acquisition "
                    "data, pricing models, vendor agreements, and campaign performance "
                    "metrics constitute Confidential Information of the Company. Employee "
                    "shall not, during or for a period of three (3) years after "
                    "termination, use or disclose any Confidential Information for any "
                    "purpose other than the performance of duties hereunder. Employee "
                    "acknowledges that any breach of this provision would cause irreparable "
                    "harm to the Company for which monetary damages would be an inadequate "
                    "remedy."
                ),
                "clause_type": "confidentiality",
            },
            {
                "index": 4,
                "heading": "5. TERMINATION OF EMPLOYMENT",
                "text": (
                    "This Agreement may be terminated by either party upon fourteen (14) "
                    "days' written notice. The Company may terminate Employee immediately "
                    "for Cause, which shall include but not be limited to: gross "
                    "misconduct, material breach of this Agreement, conviction of a felony, "
                    "or willful refusal to perform assigned duties. Upon termination for "
                    "Cause, Employee shall forfeit any unpaid bonuses and shall not be "
                    "entitled to severance. In the event of termination without Cause, "
                    "Employee shall receive four (4) weeks of base salary as severance."
                ),
                "clause_type": "termination",
            },
            {
                "index": 5,
                "heading": "6. DISPUTE RESOLUTION",
                "text": (
                    "Any dispute, controversy, or claim arising out of or relating to this "
                    "Agreement shall first be submitted to mediation administered by the "
                    "American Arbitration Association in New York, New York. If mediation is "
                    "unsuccessful within sixty (60) days, either party may submit the "
                    "dispute to binding arbitration under the AAA's Employment Arbitration "
                    "Rules. The arbitration shall be conducted by a single arbitrator and "
                    "the decision rendered shall be final and binding. Each party shall bear "
                    "its own costs, except that the Company shall pay all filing fees."
                ),
                "clause_type": "dispute_resolution",
            },
        ],
        "ground_truth": {
            "0": "position",
            "1": "compensation",
            "2": "benefits",
            "3": "confidentiality",
            "4": "termination",
            "5": "dispute_resolution",
        },
    },

    # ═══════════════════════════════════════════════════════
    # CONTRACT 3: Data Analyst — Quantum Analytics
    # ═══════════════════════════════════════════════════════
    {
        "contract_id": "emp_003",
        "title": "Data Analyst Employment Agreement — Quantum Analytics Corp.",
        "parties": {"employer": "Quantum Analytics Corp.", "employee": "Priya Patel"},
        "sections": [
            {
                "index": 0,
                "heading": "1. POSITION",
                "text": (
                    "Employee shall be employed as a Data Analyst II within the Business "
                    "Intelligence Division, reporting to the Director of Analytics. "
                    "Employee shall be responsible for designing and maintaining data "
                    "pipelines, creating dashboards and reports using Tableau and Power BI, "
                    "conducting statistical analyses, and presenting insights to senior "
                    "leadership. Employee shall maintain all required professional "
                    "certifications at Employee's own expense."
                ),
                "clause_type": "position",
            },
            {
                "index": 1,
                "heading": "2. COMPENSATION AND EQUITY",
                "text": (
                    "Employee shall receive a base annual salary of $98,500, subject to "
                    "standard payroll deductions. In addition, Employee shall be granted "
                    "2,500 Restricted Stock Units (RSUs) vesting over four (4) years on a "
                    "quarterly basis, with a one-year cliff. Employee shall also be "
                    "eligible for an annual discretionary bonus of up to 10% of base "
                    "salary. Any equity grants are subject to the terms and conditions of "
                    "the Company's 2024 Equity Incentive Plan."
                ),
                "clause_type": "compensation",
            },
            {
                "index": 2,
                "heading": "3. PROBATIONARY PERIOD",
                "text": (
                    "Employee's employment shall be subject to a probationary period of "
                    "ninety (90) calendar days commencing on the Effective Date. During "
                    "the probationary period, either party may terminate this Agreement "
                    "with five (5) business days' written notice. Upon successful "
                    "completion of the probationary period, Employee shall be eligible for "
                    "full benefits and the equity grant described in Section 2. Performance "
                    "shall be evaluated against the objectives set forth in Exhibit A."
                ),
                "clause_type": "probation",
            },
            {
                "index": 3,
                "heading": "4. CONFIDENTIALITY AND DATA PROTECTION",
                "text": (
                    "Employee acknowledges that the datasets, analytical models, machine "
                    "learning algorithms, customer segmentation data, and predictive "
                    "analytics frameworks used by the Company are proprietary and constitute "
                    "trade secrets. Employee shall take all reasonable precautions to "
                    "protect the confidentiality of such information, including using "
                    "encrypted storage devices and secure communication channels. Employee "
                    "shall comply with all applicable data protection regulations, "
                    "including GDPR and CCPA, in the handling of personal data."
                ),
                "clause_type": "confidentiality",
            },
            {
                "index": 4,
                "heading": "5. NOTICE PERIOD AND TERMINATION",
                "text": (
                    "Following the probationary period, either party may terminate this "
                    "Agreement by providing sixty (60) calendar days' written notice. The "
                    "Company reserves the right to place Employee on garden leave during "
                    "the notice period, during which Employee shall continue to receive "
                    "full salary and benefits but shall not be required to attend the "
                    "office or perform duties. Upon termination, all unvested RSUs shall "
                    "be forfeited and all Company equipment must be returned within "
                    "five (5) business days."
                ),
                "clause_type": "notice_period",
            },
        ],
        "ground_truth": {
            "0": "position",
            "1": "compensation",
            "2": "probation",
            "3": "confidentiality",
            "4": "notice_period",
        },
    },

    # ═══════════════════════════════════════════════════════
    # CONTRACT 4: Sales Director — GlobalReach Solutions
    # ═══════════════════════════════════════════════════════
    {
        "contract_id": "emp_004",
        "title": "Sales Director Employment Agreement — GlobalReach Solutions Inc.",
        "parties": {"employer": "GlobalReach Solutions Inc.", "employee": "Michael Thompson"},
        "sections": [
            {
                "index": 0,
                "heading": "1. APPOINTMENT AND DUTIES",
                "text": (
                    "The Company hereby appoints Employee as Regional Sales Director for "
                    "the Eastern United States territory, encompassing all states east of "
                    "the Mississippi River. Employee shall be responsible for managing a "
                    "sales team of twelve (12) account executives, achieving quarterly "
                    "revenue targets of no less than $2,400,000, developing new business "
                    "opportunities, and maintaining key client relationships. Employee "
                    "shall report directly to the Chief Revenue Officer and shall travel "
                    "as required, estimated at 40-50% of working time."
                ),
                "clause_type": "position",
            },
            {
                "index": 1,
                "heading": "2. COMPENSATION STRUCTURE",
                "text": (
                    "Employee shall receive a base annual salary of $165,000, payable on "
                    "a bi-weekly basis. In addition, Employee shall participate in the "
                    "Company's Sales Incentive Plan, under which Employee may earn "
                    "commissions of 2.5% on all team revenue exceeding $2,000,000 per "
                    "quarter, and an additional accelerator of 4.0% on revenue exceeding "
                    "$3,000,000. Employee shall also receive a $750 per month car allowance "
                    "and reimbursement for reasonable business travel expenses in accordance "
                    "with the Company's Travel and Expense Policy."
                ),
                "clause_type": "compensation",
            },
            {
                "index": 2,
                "heading": "3. BENEFITS",
                "text": (
                    "Employee shall be eligible for the Company's executive benefits "
                    "package, which includes comprehensive medical and dental coverage for "
                    "Employee and dependents with 100% premium coverage, a Health Savings "
                    "Account with $3,000 annual employer contribution, 401(k) with 6% "
                    "employer match, executive life insurance of $500,000, and long-term "
                    "disability coverage. Employee shall receive twenty-five (25) days of "
                    "paid vacation per year, ten (10) paid holidays, and five (5) personal "
                    "days."
                ),
                "clause_type": "benefits",
            },
            {
                "index": 3,
                "heading": "4. NON-COMPETE AND NON-SOLICITATION",
                "text": (
                    "For a period of eighteen (18) months following the cessation of "
                    "employment for any reason, Employee shall not: (a) directly or "
                    "indirectly solicit, recruit, or hire any employee of the Company; "
                    "(b) contact, solicit, or transact business with any client or "
                    "prospect that Employee serviced or had material contact with during "
                    "the last twenty-four (24) months of employment; or (c) engage in or "
                    "be employed by any enterprise software sales organization operating "
                    "within Employee's assigned territory. Employee acknowledges receipt "
                    "of adequate consideration for these restrictions."
                ),
                "clause_type": "non_compete",
            },
            {
                "index": 4,
                "heading": "5. TERMINATION PROVISIONS",
                "text": (
                    "The Company may terminate this Agreement without Cause upon sixty "
                    "(60) days' written notice, in which case Employee shall receive "
                    "severance equal to six (6) months of base salary plus the average of "
                    "the prior two (2) years' bonus payments. Employee may resign upon "
                    "thirty (30) days' written notice. Termination for Cause — defined as "
                    "fraud, embezzlement, willful misconduct, or material breach of "
                    "fiduciary duty — shall result in immediate termination with no "
                    "severance. Upon any termination, Employee shall cooperate in the "
                    "orderly transition of client relationships."
                ),
                "clause_type": "termination",
            },
            {
                "index": 5,
                "heading": "6. INTELLECTUAL PROPERTY",
                "text": (
                    "All sales methodologies, client databases, pricing strategies, "
                    "proposal templates, and market analyses developed by Employee during "
                    "the course of employment shall be the exclusive property of the "
                    "Company. Employee hereby irrevocably assigns to the Company all right, "
                    "title, and interest in any work product created within the scope of "
                    "employment. Employee agrees to assist the Company in obtaining and "
                    "enforcing patents, copyrights, and other protections for such "
                    "intellectual property at the Company's expense."
                ),
                "clause_type": "ip_assignment",
            },
            {
                "index": 6,
                "heading": "7. GOVERNING LAW",
                "text": (
                    "This Agreement shall be governed by the laws of the Commonwealth of "
                    "Massachusetts, without regard to conflict of law provisions. Any legal "
                    "action arising from this Agreement shall be brought exclusively in the "
                    "Superior Court of Suffolk County or the United States District Court "
                    "for the District of Massachusetts. Both parties irrevocably submit to "
                    "the jurisdiction of these courts. In any proceeding to enforce this "
                    "Agreement, the prevailing party shall be entitled to recover "
                    "reasonable attorneys' fees and litigation costs."
                ),
                "clause_type": "governing_law",
            },
        ],
        "ground_truth": {
            "0": "position",
            "1": "compensation",
            "2": "benefits",
            "3": "non_compete",
            "4": "termination",
            "5": "ip_assignment",
            "6": "governing_law",
        },
    },

    # ═══════════════════════════════════════════════════════
    # CONTRACT 5: Product Designer — CreativeForge Studios
    # ═══════════════════════════════════════════════════════
    {
        "contract_id": "emp_005",
        "title": "Product Designer Employment Agreement — CreativeForge Studios Inc.",
        "parties": {"employer": "CreativeForge Studios Inc.", "employee": "Aisha Johnson"},
        "sections": [
            {
                "index": 0,
                "heading": "1. POSITION AND SCOPE",
                "text": (
                    "Employee shall serve as Lead Product Designer within the UX/UI Design "
                    "Department, reporting to the Head of Design. Employee's "
                    "responsibilities shall include leading the design of user interfaces "
                    "for the Company's SaaS product suite, conducting user research and "
                    "usability testing, creating wireframes and high-fidelity prototypes "
                    "in Figma, and establishing the Company's design system. Employee "
                    "shall collaborate cross-functionally with product managers, engineers, "
                    "and marketing teams to deliver exceptional user experiences."
                ),
                "clause_type": "position",
            },
            {
                "index": 1,
                "heading": "2. COMPENSATION",
                "text": (
                    "The Company shall compensate Employee at an annual base salary of "
                    "$128,000, payable in accordance with the Company's standard payroll "
                    "schedule. Employee shall be eligible for an annual performance bonus "
                    "ranging from 8% to 12% of base salary, based upon individual "
                    "performance and Company financial results. Employee shall also receive "
                    "stock options to purchase 5,000 shares of the Company's common stock "
                    "at an exercise price equal to the fair market value on the grant date, "
                    "vesting monthly over four (4) years with a one-year cliff."
                ),
                "clause_type": "compensation",
            },
            {
                "index": 2,
                "heading": "3. INTELLECTUAL PROPERTY AND WORK PRODUCT",
                "text": (
                    "All designs, mockups, prototypes, design systems, branding materials, "
                    "icons, illustrations, and any other creative works produced by "
                    "Employee during the term of employment shall be considered works made "
                    "for hire and shall be the sole and exclusive property of the Company. "
                    "To the extent that any such works are not deemed works made for hire "
                    "under applicable law, Employee hereby assigns all rights therein to "
                    "the Company. Employee waives any moral rights in such works to the "
                    "fullest extent permitted by law."
                ),
                "clause_type": "ip_assignment",
            },
            {
                "index": 3,
                "heading": "4. CONFIDENTIALITY",
                "text": (
                    "Employee shall maintain in confidence all product roadmaps, user "
                    "research data, design specifications, unannounced features, A/B "
                    "testing results, and competitive analyses that Employee has access to "
                    "during employment. Employee shall not share any such information on "
                    "portfolio websites, social media platforms, or design communities "
                    "such as Dribbble or Behance without express written permission from "
                    "the Head of Design. This obligation shall survive termination for a "
                    "period of two (2) years."
                ),
                "clause_type": "confidentiality",
            },
            {
                "index": 4,
                "heading": "5. TERMINATION",
                "text": (
                    "Either party may terminate this Agreement by providing thirty (30) "
                    "days' written notice. In the event of termination without Cause, "
                    "Employee shall receive a severance package consisting of eight (8) "
                    "weeks of base salary, continuation of health benefits for three (3) "
                    "months, and acceleration of any stock options that would have vested "
                    "within the ninety (90) days following termination. Termination for "
                    "Cause — including plagiarism of third-party designs, unauthorized "
                    "disclosure of Confidential Information, or repeated failure to meet "
                    "deadlines — shall result in forfeiture of all unvested options."
                ),
                "clause_type": "termination",
            },
            {
                "index": 5,
                "heading": "6. GOVERNING LAW AND VENUE",
                "text": (
                    "This Agreement shall be governed by and interpreted under the laws "
                    "of the State of New York. Any claims arising under or relating to "
                    "this Agreement shall be resolved in the state or federal courts "
                    "situated in the Borough of Manhattan, New York City. The parties "
                    "agree that the United Nations Convention on Contracts for the "
                    "International Sale of Goods shall not apply. Each party waives any "
                    "right to a jury trial in any action arising from this Agreement."
                ),
                "clause_type": "governing_law",
            },
        ],
        "ground_truth": {
            "0": "position",
            "1": "compensation",
            "2": "ip_assignment",
            "3": "confidentiality",
            "4": "termination",
            "5": "governing_law",
        },
    },
]
