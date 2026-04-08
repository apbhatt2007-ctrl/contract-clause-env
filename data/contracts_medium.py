"""
Medium task data: 5 vendor contracts for risk flagging & analysis.

Each contract has 7-9 sections, with 3-5 containing subtle risks.
Risks are embedded in realistic legal language with severity and keywords
for deterministic grading.
"""

MEDIUM_CONTRACTS = [
    # ═══════════════════════════════════════════════════════
    # VENDOR 1: Cloud Infrastructure — NimbusTech Solutions
    # ═══════════════════════════════════════════════════════
    {
        "contract_id": "vendor_001",
        "title": "Cloud Infrastructure Services Agreement — NimbusTech Solutions",
        "parties": {"client": "Acme Corp", "vendor": "NimbusTech Solutions LLC"},
        "sections": [
            {
                "index": 0,
                "heading": "1. SCOPE OF SERVICES",
                "text": (
                    "Vendor shall provide cloud hosting, data storage, managed database "
                    "services, and content delivery network access as set forth in Exhibit A "
                    "(the 'Service Order'). Services shall include 99.9% uptime SLA for "
                    "production workloads, 24/7 technical support via phone and email, and "
                    "automated daily backups with 30-day retention. Vendor shall allocate "
                    "dedicated infrastructure resources within its us-east-1 data center "
                    "region for Client's exclusive use."
                ),
                "has_risk": False,
                "risk_type": None,
                "severity": None,
                "risk_keywords": [],
            },
            {
                "index": 1,
                "heading": "2. FEES AND PAYMENT",
                "text": (
                    "Client shall pay a monthly service fee of $18,500 for the base "
                    "infrastructure package, plus usage-based charges for bandwidth "
                    "exceeding 10TB per month at $0.08 per GB. All invoices shall be "
                    "issued on the first business day of each month and are due within "
                    "thirty (30) days of receipt. Late payments shall accrue interest at "
                    "the rate of 1.5% per month or the maximum rate permitted by law, "
                    "whichever is less."
                ),
                "has_risk": False,
                "risk_type": None,
                "severity": None,
                "risk_keywords": [],
            },
            {
                "index": 2,
                "heading": "3. TERM AND RENEWAL",
                "text": (
                    "This Agreement shall commence on January 1, 2025 and shall continue "
                    "for an initial term of thirty-six (36) months. Following the initial "
                    "term, this Agreement shall automatically renew for successive twelve "
                    "(12) month periods unless either party provides written notice of "
                    "non-renewal at least one hundred and twenty (120) calendar days prior "
                    "to the end of the then-current term. Client acknowledges that failure "
                    "to provide timely notice shall constitute acceptance of renewal at "
                    "the then-prevailing rate, which may be adjusted by Vendor at its "
                    "discretion."
                ),
                "has_risk": True,
                "risk_type": "auto_renewal_trap",
                "severity": "high",
                "risk_keywords": [
                    "auto renewal", "automatically renew", "120 days",
                    "prevailing rate", "vendor discretion", "rate adjustment",
                ],
            },
            {
                "index": 3,
                "heading": "4. SERVICE LEVEL AGREEMENT",
                "text": (
                    "Vendor shall use commercially reasonable efforts to maintain service "
                    "availability of 99.9% measured on a monthly basis, excluding scheduled "
                    "maintenance windows. In the event that Vendor fails to meet the "
                    "availability target, Client's sole and exclusive remedy shall be a "
                    "service credit equal to 5% of the monthly fee for each full 1% of "
                    "downtime below the target, up to a maximum credit of 30% of the "
                    "monthly fee. Service credits must be requested within ten (10) "
                    "business days of the downtime event."
                ),
                "has_risk": False,
                "risk_type": None,
                "severity": None,
                "risk_keywords": [],
            },
            {
                "index": 4,
                "heading": "5. LIMITATION OF LIABILITY",
                "text": (
                    "IN NO EVENT SHALL VENDOR BE LIABLE FOR ANY INDIRECT, INCIDENTAL, "
                    "SPECIAL, CONSEQUENTIAL, OR PUNITIVE DAMAGES, INCLUDING BUT NOT "
                    "LIMITED TO LOSS OF PROFITS, DATA, OR BUSINESS OPPORTUNITIES. "
                    "VENDOR'S TOTAL AGGREGATE LIABILITY ARISING OUT OF OR RELATED TO THIS "
                    "AGREEMENT SHALL NOT BE SUBJECT TO A FIXED CAP BUT RATHER SHALL BE "
                    "DETERMINED ON A CASE-BY-CASE BASIS AT VENDOR'S SOLE AND ABSOLUTE "
                    "DISCRETION, TAKING INTO ACCOUNT THE NATURE AND SCOPE OF SERVICES "
                    "RENDERED AND THE CIRCUMSTANCES GIVING RISE TO THE CLAIM."
                ),
                "has_risk": True,
                "risk_type": "unlimited_liability",
                "severity": "critical",
                "risk_keywords": [
                    "uncapped liability", "sole discretion", "no fixed cap",
                    "aggregate liability", "case-by-case", "vendor discretion",
                ],
            },
            {
                "index": 5,
                "heading": "6. CONFIDENTIALITY",
                "text": (
                    "Each party shall maintain the confidentiality of all non-public "
                    "information disclosed by the other party in connection with this "
                    "Agreement. Confidential Information shall not include information "
                    "that: (a) is or becomes publicly available through no fault of the "
                    "receiving party; (b) was in the receiving party's possession prior to "
                    "disclosure; (c) is independently developed by the receiving party; or "
                    "(d) is received from a third party without restriction. This "
                    "obligation shall survive termination for three (3) years."
                ),
                "has_risk": False,
                "risk_type": None,
                "severity": None,
                "risk_keywords": [],
            },
            {
                "index": 6,
                "heading": "7. DATA OWNERSHIP AND PROCESSING",
                "text": (
                    "Client acknowledges and agrees that while Client retains ownership of "
                    "the raw data uploaded to the platform, Vendor shall acquire a "
                    "perpetual, irrevocable, worldwide, royalty-free license to use, "
                    "reproduce, modify, and create derivative works from all data processed "
                    "through the Services, including metadata, usage patterns, aggregated "
                    "analytics, and any machine learning models trained on Client's data. "
                    "Vendor may use such data and derivatives for product improvement, "
                    "benchmarking, and commercial purposes without further consent."
                ),
                "has_risk": True,
                "risk_type": "data_ownership_grab",
                "severity": "critical",
                "risk_keywords": [
                    "perpetual license", "irrevocable", "derivative works",
                    "data ownership", "machine learning models", "without consent",
                    "commercial purposes",
                ],
            },
            {
                "index": 7,
                "heading": "8. GOVERNING LAW",
                "text": (
                    "This Agreement shall be governed by the laws of the State of Delaware "
                    "without regard to conflict of laws principles. Any dispute shall be "
                    "resolved by binding arbitration in Wilmington, Delaware under the "
                    "rules of the American Arbitration Association. The parties consent to "
                    "the exclusive jurisdiction of the courts of Delaware for any ancillary "
                    "proceedings. The prevailing party shall be entitled to recover "
                    "attorneys' fees."
                ),
                "has_risk": False,
                "risk_type": None,
                "severity": None,
                "risk_keywords": [],
            },
        ],
        "ground_truth_risks": [
            {"section_index": 2, "risk_type": "auto_renewal_trap", "severity": "high"},
            {"section_index": 4, "risk_type": "unlimited_liability", "severity": "critical"},
            {"section_index": 6, "risk_type": "data_ownership_grab", "severity": "critical"},
        ],
    },

    # ═══════════════════════════════════════════════════════
    # VENDOR 2: Marketing Agency — BrandForge Creative
    # ═══════════════════════════════════════════════════════
    {
        "contract_id": "vendor_002",
        "title": "Marketing Services Agreement — BrandForge Creative Agency",
        "parties": {"client": "Pinnacle Retail Group", "vendor": "BrandForge Creative Agency"},
        "sections": [
            {
                "index": 0,
                "heading": "1. SERVICES",
                "text": (
                    "Agency shall provide comprehensive marketing services including brand "
                    "strategy development, digital advertising campaign management across "
                    "Google Ads, Meta Ads, and LinkedIn, social media content creation and "
                    "scheduling, email marketing automation, and monthly performance "
                    "reporting. Agency shall dedicate a team consisting of one Account "
                    "Director, two Creative Designers, and one Media Buyer to Client's "
                    "account on a full-time basis."
                ),
                "has_risk": False,
                "risk_type": None,
                "severity": None,
                "risk_keywords": [],
            },
            {
                "index": 1,
                "heading": "2. COMPENSATION",
                "text": (
                    "Client shall pay Agency a monthly retainer of $35,000 for the core "
                    "services described herein. Additional project-based work, including "
                    "website redesigns, video production, and event marketing, shall be "
                    "billed at the blended rate of $225 per hour. All ad spend shall be "
                    "passed through at cost plus a 12% management fee. Payment terms are "
                    "Net-15 from invoice date."
                ),
                "has_risk": False,
                "risk_type": None,
                "severity": None,
                "risk_keywords": [],
            },
            {
                "index": 2,
                "heading": "3. TERM AND TERMINATION",
                "text": (
                    "The initial term of this Agreement shall be twenty-four (24) months. "
                    "Client may terminate this Agreement prior to the expiration of the "
                    "initial term only upon payment of an early termination fee equal to "
                    "the aggregate of all remaining monthly retainers for the balance of "
                    "the term, plus a 25% administrative surcharge. In the event of "
                    "termination, Client shall have thirty (30) days to transition "
                    "campaigns to a new provider."
                ),
                "has_risk": True,
                "risk_type": "excessive_penalty",
                "severity": "high",
                "risk_keywords": [
                    "early termination fee", "remaining retainers", "25% surcharge",
                    "administrative surcharge", "all remaining", "penalty",
                ],
            },
            {
                "index": 3,
                "heading": "4. INTELLECTUAL PROPERTY",
                "text": (
                    "All creative works, designs, copy, and marketing materials produced "
                    "by Agency under this Agreement shall become the property of Client "
                    "upon full payment of all outstanding invoices. Prior to full payment, "
                    "Agency retains all intellectual property rights and may exercise a "
                    "lien on all materials. Agency reserves the right to showcase work in "
                    "its portfolio with Client's prior consent."
                ),
                "has_risk": False,
                "risk_type": None,
                "severity": None,
                "risk_keywords": [],
            },
            {
                "index": 4,
                "heading": "5. INDEMNIFICATION",
                "text": (
                    "Client shall indemnify, defend, and hold harmless Agency, its "
                    "officers, directors, employees, agents, and subcontractors from and "
                    "against any and all claims, damages, losses, liabilities, costs, and "
                    "expenses (including reasonable attorneys' fees) arising out of or "
                    "related to: (a) Client's products or services; (b) Client's "
                    "instructions to Agency; (c) any third-party claims related to the "
                    "marketing materials or campaigns, regardless of whether such claims "
                    "arise from Agency's negligence or errors in execution; and (d) any "
                    "regulatory actions or consumer complaints."
                ),
                "has_risk": True,
                "risk_type": "broad_indemnification",
                "severity": "high",
                "risk_keywords": [
                    "indemnify", "regardless of negligence", "hold harmless",
                    "agency negligence", "errors in execution", "broad indemnification",
                ],
            },
            {
                "index": 5,
                "heading": "6. AMENDMENT AND MODIFICATION",
                "text": (
                    "Agency reserves the right to modify the scope of services, adjust "
                    "pricing, change team assignments, and update its terms of service at "
                    "any time by providing written notice to Client no fewer than fifteen "
                    "(15) business days prior to the effective date of such modification. "
                    "Client's continued use of Services following such notice period shall "
                    "constitute acceptance of the modified terms. Client's sole remedy for "
                    "objecting to any modification shall be to terminate the Agreement "
                    "subject to the early termination provisions of Section 3."
                ),
                "has_risk": True,
                "risk_type": "unilateral_amendment",
                "severity": "critical",
                "risk_keywords": [
                    "unilateral", "modify at any time", "continued use constitutes acceptance",
                    "sole remedy", "change terms", "without consent",
                ],
            },
            {
                "index": 6,
                "heading": "7. NON-COMPETE",
                "text": (
                    "During the term of this Agreement and for a period of twenty-four "
                    "(24) months following termination, Client shall not directly or "
                    "indirectly engage, hire, or contract with any individual who is or "
                    "was employed by or affiliated with Agency during the preceding "
                    "thirty-six (36) months. Client further agrees not to retain any "
                    "competing marketing agency that employs any former Agency personnel "
                    "who worked on Client's account. Violation of this provision shall "
                    "result in liquidated damages of $150,000 per occurrence."
                ),
                "has_risk": True,
                "risk_type": "non_compete_overreach",
                "severity": "high",
                "risk_keywords": [
                    "non-compete", "24 months", "36 months", "overreach",
                    "liquidated damages", "$150,000", "any individual",
                ],
            },
            {
                "index": 7,
                "heading": "8. GOVERNING LAW",
                "text": (
                    "This Agreement shall be governed by the laws of the State of "
                    "Illinois. Any disputes shall be resolved through binding arbitration "
                    "in Chicago, Illinois, administered by JAMS under its Comprehensive "
                    "Arbitration Rules. The arbitration shall be conducted by a panel of "
                    "three (3) arbitrators."
                ),
                "has_risk": False,
                "risk_type": None,
                "severity": None,
                "risk_keywords": [],
            },
        ],
        "ground_truth_risks": [
            {"section_index": 2, "risk_type": "excessive_penalty", "severity": "high"},
            {"section_index": 4, "risk_type": "broad_indemnification", "severity": "high"},
            {"section_index": 5, "risk_type": "unilateral_amendment", "severity": "critical"},
            {"section_index": 6, "risk_type": "non_compete_overreach", "severity": "high"},
        ],
    },

    # ═══════════════════════════════════════════════════════
    # VENDOR 3: IT Consulting — CodeBridge Technologies
    # ═══════════════════════════════════════════════════════
    {
        "contract_id": "vendor_003",
        "title": "IT Consulting Services Agreement — CodeBridge Technologies",
        "parties": {"client": "MedCore Health Systems", "vendor": "CodeBridge Technologies Inc."},
        "sections": [
            {
                "index": 0,
                "heading": "1. ENGAGEMENT AND SERVICES",
                "text": (
                    "Vendor shall provide information technology consulting services "
                    "including system architecture review, legacy application modernization, "
                    "cloud migration strategy, and cybersecurity assessment for Client's "
                    "healthcare information systems. Vendor shall assign a team of three "
                    "(3) senior consultants and one (1) project manager, each with a "
                    "minimum of eight (8) years' industry experience. The engagement shall "
                    "follow an agile methodology with bi-weekly sprint reviews."
                ),
                "has_risk": False,
                "risk_type": None,
                "severity": None,
                "risk_keywords": [],
            },
            {
                "index": 1,
                "heading": "2. FEES",
                "text": (
                    "Client shall pay Vendor a blended daily rate of $2,800 per consultant "
                    "for on-site work and $2,400 per consultant for remote work. The "
                    "estimated total project cost is $840,000 for the eighteen (18) month "
                    "engagement period. All travel expenses shall be reimbursed at cost, "
                    "subject to Client's travel policy. Invoices shall be submitted "
                    "monthly and are payable within twenty (20) business days."
                ),
                "has_risk": False,
                "risk_type": None,
                "severity": None,
                "risk_keywords": [],
            },
            {
                "index": 2,
                "heading": "3. INTELLECTUAL PROPERTY",
                "text": (
                    "All custom code, documentation, system designs, and deliverables "
                    "created specifically for Client under this Agreement shall be owned "
                    "by Client upon full payment. Vendor retains all rights to its "
                    "pre-existing frameworks, libraries, tools, and methodologies, and "
                    "grants Client a non-exclusive, perpetual license to use such "
                    "pre-existing materials solely in connection with the deliverables."
                ),
                "has_risk": False,
                "risk_type": None,
                "severity": None,
                "risk_keywords": [],
            },
            {
                "index": 3,
                "heading": "4. DATA HANDLING AND COMPLIANCE",
                "text": (
                    "Vendor acknowledges that Client's systems contain protected health "
                    "information (PHI) subject to HIPAA. Vendor agrees to execute a "
                    "Business Associate Agreement and comply with all applicable HIPAA "
                    "requirements. Notwithstanding the foregoing, Vendor shall retain the "
                    "right to collect, aggregate, and commercialize anonymized operational "
                    "and performance data derived from Client's systems, including system "
                    "architecture patterns, query performance metrics, and infrastructure "
                    "utilization statistics, for the purpose of improving Vendor's products "
                    "and services."
                ),
                "has_risk": True,
                "risk_type": "data_ownership_grab",
                "severity": "high",
                "risk_keywords": [
                    "commercialize", "anonymized data", "retain right",
                    "aggregate data", "derived from", "without consent",
                ],
            },
            {
                "index": 4,
                "heading": "5. LIMITATION OF LIABILITY",
                "text": (
                    "Vendor's total cumulative liability for all claims arising out of "
                    "this Agreement shall not exceed the fees actually paid by Client in "
                    "the twelve (12) month period preceding the event giving rise to the "
                    "claim. In no event shall Vendor be liable for lost profits, data "
                    "loss, or consequential damages, even if advised of the possibility "
                    "thereof."
                ),
                "has_risk": False,
                "risk_type": None,
                "severity": None,
                "risk_keywords": [],
            },
            {
                "index": 5,
                "heading": "6. INDEMNIFICATION",
                "text": (
                    "Client shall indemnify and hold harmless Vendor against all claims, "
                    "losses, and damages arising from Client's use of the deliverables, "
                    "including but not limited to claims of data breaches, system failures, "
                    "patient harm, regulatory fines, and any downstream liabilities "
                    "incurred by third parties who interact with Client's systems, "
                    "regardless of whether such claims result in whole or in part from "
                    "defects, errors, or omissions in Vendor's deliverables or services."
                ),
                "has_risk": True,
                "risk_type": "broad_indemnification",
                "severity": "critical",
                "risk_keywords": [
                    "indemnify", "regardless of defects", "vendor errors",
                    "hold harmless", "downstream liabilities", "omissions",
                ],
            },
            {
                "index": 6,
                "heading": "7. DISPUTE RESOLUTION",
                "text": (
                    "Any disputes arising under this Agreement shall be resolved "
                    "exclusively by binding arbitration conducted in Singapore under the "
                    "rules of the Singapore International Arbitration Centre (SIAC). The "
                    "language of the arbitration shall be English. Client hereby waives "
                    "any objection to this forum and agrees that the laws of Singapore "
                    "shall govern the arbitration proceedings, notwithstanding that both "
                    "parties are domiciled in the United States."
                ),
                "has_risk": True,
                "risk_type": "jurisdiction_trap",
                "severity": "high",
                "risk_keywords": [
                    "Singapore", "inconvenient jurisdiction", "foreign arbitration",
                    "waives objection", "both parties US", "unfair forum",
                ],
            },
            {
                "index": 7,
                "heading": "8. GENERAL PROVISIONS",
                "text": (
                    "This Agreement constitutes the entire understanding between the "
                    "parties and supersedes all prior agreements, negotiations, and "
                    "representations. No amendment or modification shall be valid unless "
                    "made in writing and signed by authorized representatives of both "
                    "parties. If any provision is found unenforceable, the remaining "
                    "provisions shall continue in full force and effect."
                ),
                "has_risk": False,
                "risk_type": None,
                "severity": None,
                "risk_keywords": [],
            },
        ],
        "ground_truth_risks": [
            {"section_index": 3, "risk_type": "data_ownership_grab", "severity": "high"},
            {"section_index": 5, "risk_type": "broad_indemnification", "severity": "critical"},
            {"section_index": 6, "risk_type": "jurisdiction_trap", "severity": "high"},
        ],
    },

    # ═══════════════════════════════════════════════════════
    # VENDOR 4: Office Supplies — ProcureMax Distribution
    # ═══════════════════════════════════════════════════════
    {
        "contract_id": "vendor_004",
        "title": "Office Supply and Equipment Agreement — ProcureMax Distribution",
        "parties": {"client": "Evergreen Financial Group", "vendor": "ProcureMax Distribution Co."},
        "sections": [
            {
                "index": 0,
                "heading": "1. PRODUCTS AND SERVICES",
                "text": (
                    "Vendor shall supply office furniture, equipment, stationery, "
                    "breakroom supplies, and janitorial products as ordered by Client "
                    "through Vendor's online procurement portal. Vendor shall maintain a "
                    "catalog of no fewer than 15,000 SKUs and shall fulfill standard "
                    "orders within three (3) business days to any Client location within "
                    "the continental United States. Rush delivery (same-day or next-day) "
                    "is available at an additional charge of 35% of order value."
                ),
                "has_risk": False,
                "risk_type": None,
                "severity": None,
                "risk_keywords": [],
            },
            {
                "index": 1,
                "heading": "2. PRICING",
                "text": (
                    "Pricing for all products shall be as set forth in the Master Price "
                    "List attached as Exhibit A. Vendor shall offer Client a volume "
                    "discount of 8% on monthly orders exceeding $25,000 and 12% on "
                    "monthly orders exceeding $50,000. The Master Price List shall be "
                    "effective for the first twelve (12) months, after which Vendor may "
                    "adjust prices with sixty (60) days' written notice."
                ),
                "has_risk": False,
                "risk_type": None,
                "severity": None,
                "risk_keywords": [],
            },
            {
                "index": 2,
                "heading": "3. TERM AND RENEWAL",
                "text": (
                    "This Agreement shall be effective for an initial term of twelve (12) "
                    "months commencing on the date of execution. Thereafter, this Agreement "
                    "shall automatically renew for successive twelve (12) month periods "
                    "unless Client provides written notice of cancellation at least ninety "
                    "(90) calendar days prior to the end of the then-current renewal "
                    "period. Any cancellation notice received after such deadline shall "
                    "be treated as a cancellation request for the subsequent renewal "
                    "period, and Client shall remain bound for the current renewal term."
                ),
                "has_risk": True,
                "risk_type": "auto_renewal_trap",
                "severity": "medium",
                "risk_keywords": [
                    "auto renewal", "automatically renew", "90 days notice",
                    "bound for current term", "cancellation deadline",
                ],
            },
            {
                "index": 3,
                "heading": "4. ORDER CANCELLATION AND RETURNS",
                "text": (
                    "Client may cancel orders prior to shipment without penalty. Returns "
                    "of undamaged products in original packaging are accepted within "
                    "fourteen (14) days of delivery, subject to a restocking fee of 15% of "
                    "the returned product value. Custom-ordered or personalized items are "
                    "non-returnable. Vendor shall replace defective products at no charge "
                    "within thirty (30) days of delivery."
                ),
                "has_risk": False,
                "risk_type": None,
                "severity": None,
                "risk_keywords": [],
            },
            {
                "index": 4,
                "heading": "5. BREACH AND PENALTIES",
                "text": (
                    "In the event that Client fails to place minimum monthly orders "
                    "totaling at least $10,000 in any given calendar month, Client shall "
                    "pay Vendor a shortfall penalty equal to 200% of the difference "
                    "between the minimum order threshold and the actual orders placed. "
                    "Additionally, Client shall be charged a $5,000 account maintenance "
                    "fee for each month in which the minimum is not met. These penalties "
                    "shall be automatically deducted from any credit balances or invoiced "
                    "separately."
                ),
                "has_risk": True,
                "risk_type": "excessive_penalty",
                "severity": "critical",
                "risk_keywords": [
                    "200%", "shortfall penalty", "minimum order",
                    "account maintenance fee", "automatically deducted",
                    "disproportionate",
                ],
            },
            {
                "index": 5,
                "heading": "6. AMENDMENT OF TERMS",
                "text": (
                    "Vendor reserves the unilateral right to amend any provision of this "
                    "Agreement, including but not limited to pricing, delivery times, "
                    "return policies, and minimum order requirements, effective upon "
                    "posting updated terms on Vendor's website and sending notification "
                    "to Client's designated email address. Client's placement of any "
                    "order following such notification shall constitute irrevocable "
                    "acceptance of the amended terms."
                ),
                "has_risk": True,
                "risk_type": "unilateral_amendment",
                "severity": "critical",
                "risk_keywords": [
                    "unilateral right", "amend any provision", "posting on website",
                    "irrevocable acceptance", "placement of order", "without consent",
                ],
            },
            {
                "index": 6,
                "heading": "7. INDEMNIFICATION",
                "text": (
                    "Client agrees to indemnify, defend, and hold harmless Vendor from "
                    "any and all claims, suits, damages, and expenses arising from "
                    "Client's use of products supplied under this Agreement, including "
                    "claims for personal injury, property damage, or workplace accidents, "
                    "even if such claims arise from defects in Vendor's products or from "
                    "Vendor's failure to comply with applicable safety standards or "
                    "regulations."
                ),
                "has_risk": True,
                "risk_type": "broad_indemnification",
                "severity": "high",
                "risk_keywords": [
                    "indemnify", "product defects", "safety standards",
                    "vendor failure", "personal injury", "hold harmless",
                ],
            },
            {
                "index": 7,
                "heading": "8. NON-SOLICITATION",
                "text": (
                    "For a period of thirty-six (36) months following the termination of "
                    "this Agreement, Client shall not directly or indirectly solicit, "
                    "recruit, or engage any of Vendor's employees, agents, or independent "
                    "contractors. This restriction applies to all Vendor personnel, "
                    "regardless of whether they had any involvement with Client's account. "
                    "Breach of this provision shall result in liquidated damages of "
                    "$100,000 per individual solicited."
                ),
                "has_risk": True,
                "risk_type": "non_compete_overreach",
                "severity": "high",
                "risk_keywords": [
                    "36 months", "all personnel", "regardless of involvement",
                    "$100,000", "overreach", "liquidated damages",
                ],
            },
            {
                "index": 8,
                "heading": "9. GOVERNING LAW",
                "text": (
                    "This Agreement shall be governed by the laws of the State of Texas. "
                    "Any legal action shall be brought exclusively in the courts of "
                    "Harris County, Texas. Each party consents to personal jurisdiction "
                    "in those courts. The UN Convention on Contracts for the International "
                    "Sale of Goods shall not apply."
                ),
                "has_risk": False,
                "risk_type": None,
                "severity": None,
                "risk_keywords": [],
            },
        ],
        "ground_truth_risks": [
            {"section_index": 2, "risk_type": "auto_renewal_trap", "severity": "medium"},
            {"section_index": 4, "risk_type": "excessive_penalty", "severity": "critical"},
            {"section_index": 5, "risk_type": "unilateral_amendment", "severity": "critical"},
            {"section_index": 6, "risk_type": "broad_indemnification", "severity": "high"},
            {"section_index": 7, "risk_type": "non_compete_overreach", "severity": "high"},
        ],
    },

    # ═══════════════════════════════════════════════════════
    # VENDOR 5: Legal Services — LexAssist Professional
    # ═══════════════════════════════════════════════════════
    {
        "contract_id": "vendor_005",
        "title": "Legal Services Engagement Letter — LexAssist Professional Corp.",
        "parties": {"client": "Horizon Biotech Ltd.", "vendor": "LexAssist Professional Corp."},
        "sections": [
            {
                "index": 0,
                "heading": "1. SCOPE OF REPRESENTATION",
                "text": (
                    "Firm shall provide legal services to Client in connection with "
                    "intellectual property matters, including patent prosecution, trademark "
                    "registration, licensing negotiations, and IP litigation support. Firm "
                    "shall assign Partner Maria Vasquez as lead attorney, supported by two "
                    "(2) senior associates and one (1) patent agent. The scope of "
                    "representation does not include regulatory compliance or FDA matters "
                    "unless separately agreed in writing."
                ),
                "has_risk": False,
                "risk_type": None,
                "severity": None,
                "risk_keywords": [],
            },
            {
                "index": 1,
                "heading": "2. FEES AND BILLING",
                "text": (
                    "Firm shall bill Client at the following hourly rates: Partner — $750, "
                    "Senior Associate — $475, Patent Agent — $350, Paralegal — $200. "
                    "Invoices shall be rendered monthly and are payable within ten (10) "
                    "business days. A retainer deposit of $50,000 shall be paid upon "
                    "execution of this Engagement Letter and replenished to $50,000 "
                    "whenever the balance falls below $15,000. Unpaid balances shall "
                    "accrue interest at 2% per month."
                ),
                "has_risk": False,
                "risk_type": None,
                "severity": None,
                "risk_keywords": [],
            },
            {
                "index": 2,
                "heading": "3. CONFLICTS OF INTEREST",
                "text": (
                    "Firm represents that it has conducted a conflicts check and is not "
                    "aware of any current conflict of interest that would prevent "
                    "representation of Client. Client acknowledges that Firm represents "
                    "numerous clients in the biotechnology and pharmaceutical sectors and "
                    "consents to Firm's continued representation of such clients, provided "
                    "that Firm shall not represent any party directly adverse to Client in "
                    "substantially related matters."
                ),
                "has_risk": False,
                "risk_type": None,
                "severity": None,
                "risk_keywords": [],
            },
            {
                "index": 3,
                "heading": "4. INTELLECTUAL PROPERTY WORK PRODUCT",
                "text": (
                    "Client shall own all patents, trademarks, and registrations obtained "
                    "through Firm's services. However, Firm shall retain all right, title, "
                    "and interest in its legal memoranda, research analyses, prosecution "
                    "strategies, template documents, analytical frameworks, and practice "
                    "methodologies developed or refined during the engagement, including "
                    "the right to use such materials and any insights derived from Client's "
                    "technology for the benefit of other clients in similar fields without "
                    "attribution or compensation."
                ),
                "has_risk": True,
                "risk_type": "data_ownership_grab",
                "severity": "high",
                "risk_keywords": [
                    "retain all right", "insights derived", "other clients",
                    "without attribution", "without compensation",
                    "practice methodologies",
                ],
            },
            {
                "index": 4,
                "heading": "5. LIMITATION OF LIABILITY",
                "text": (
                    "Firm's aggregate liability for any and all claims arising from the "
                    "legal services rendered under this Engagement Letter, including claims "
                    "for malpractice, negligence, breach of fiduciary duty, or any other "
                    "theory of liability, shall be limited to the lesser of: (a) the total "
                    "fees actually paid by Client during the six (6) months preceding the "
                    "claim; or (b) $25,000. Client expressly waives any right to seek "
                    "consequential, incidental, or punitive damages."
                ),
                "has_risk": True,
                "risk_type": "unlimited_liability",
                "severity": "critical",
                "risk_keywords": [
                    "limited to lesser", "$25,000 cap", "waives right",
                    "malpractice cap", "six months fees", "extremely low cap",
                ],
            },
            {
                "index": 5,
                "heading": "6. TERMINATION",
                "text": (
                    "Either party may terminate this engagement upon thirty (30) days' "
                    "written notice. Upon termination, Firm shall provide Client with all "
                    "original documents and file materials. Client shall pay all fees and "
                    "expenses incurred through the effective date of termination. Firm "
                    "may withdraw from representation if Client fails to pay invoices "
                    "within the specified timeframe or if a conflict of interest arises "
                    "that cannot be waived."
                ),
                "has_risk": False,
                "risk_type": None,
                "severity": None,
                "risk_keywords": [],
            },
            {
                "index": 6,
                "heading": "7. DISPUTE RESOLUTION",
                "text": (
                    "Any dispute between Client and Firm shall be submitted to binding "
                    "arbitration administered exclusively by the Cayman Islands Arbitration "
                    "Forum under its Commercial Arbitration Rules. The seat of arbitration "
                    "shall be George Town, Grand Cayman. Client agrees that the laws of "
                    "the Cayman Islands shall govern all disputes, irrespective of the "
                    "location where services were performed. Client waives any right to "
                    "bring proceedings in any other jurisdiction."
                ),
                "has_risk": True,
                "risk_type": "jurisdiction_trap",
                "severity": "critical",
                "risk_keywords": [
                    "Cayman Islands", "offshore jurisdiction", "waives right",
                    "foreign forum", "inconvenient", "George Town",
                ],
            },
            {
                "index": 7,
                "heading": "8. MODIFICATION OF TERMS",
                "text": (
                    "Firm may amend the billing rates, retainer requirements, and staffing "
                    "assignments under this Engagement Letter at any time upon fifteen (15) "
                    "calendar days' written notice to Client. If Client does not object in "
                    "writing within the notice period, the amendments shall be deemed "
                    "accepted and effective. Client's continued engagement of Firm's "
                    "services after the notice period shall further confirm acceptance."
                ),
                "has_risk": True,
                "risk_type": "unilateral_amendment",
                "severity": "high",
                "risk_keywords": [
                    "amend at any time", "deemed accepted", "continued engagement",
                    "unilateral", "without consent", "15 days notice",
                ],
            },
        ],
        "ground_truth_risks": [
            {"section_index": 3, "risk_type": "data_ownership_grab", "severity": "high"},
            {"section_index": 4, "risk_type": "unlimited_liability", "severity": "critical"},
            {"section_index": 6, "risk_type": "jurisdiction_trap", "severity": "critical"},
            {"section_index": 7, "risk_type": "unilateral_amendment", "severity": "high"},
        ],
    },
]
