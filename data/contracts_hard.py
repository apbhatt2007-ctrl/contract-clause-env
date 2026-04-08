"""
Hard task data: 3 contract pairs for multi-contract comparison & redlining.

Each pair has original_sections + revised_sections with ground truth changes,
impact assessments, ideal amendments, and summary key points.
"""

HARD_CONTRACT_PAIRS = [
    # ═══════════════════════════════════════════════════════
    # PAIR 1: Software License — DataStream Inc.
    # ═══════════════════════════════════════════════════════
    {
        "pair_id": "compare_001",
        "title": "Software Licensing Agreement — DataStream Inc.",
        "parties": {"licensor": "DataStream Inc.", "licensee": "Atlas Financial Corp."},
        "original_sections": [
            {
                "index": 0,
                "heading": "1. GRANT OF LICENSE",
                "text": (
                    "Licensor hereby grants to Licensee a non-exclusive, non-transferable "
                    "license to use the DataStream Analytics Platform (the 'Software') for "
                    "Licensee's internal business purposes. The license shall cover up to "
                    "two hundred and fifty (250) named users across all Licensee office "
                    "locations within the United States. Licensee may install the Software "
                    "on its own servers or access via Licensor's cloud infrastructure."
                ),
            },
            {
                "index": 1,
                "heading": "2. LICENSE FEE",
                "text": (
                    "Licensee shall pay an annual license fee of $50,000, due within "
                    "thirty (30) days of the commencement of each license year. The fee "
                    "includes standard technical support during business hours (9 AM – "
                    "6 PM ET, Monday through Friday), software updates, and access to "
                    "Licensor's online knowledge base. Premium 24/7 support is available "
                    "for an additional $12,000 per year."
                ),
            },
            {
                "index": 2,
                "heading": "3. PAYMENT TERMS",
                "text": (
                    "All payments shall be made in United States Dollars within sixty (60) "
                    "days of receipt of invoice (Net-60). Licensee may elect to pay "
                    "annually in advance or in quarterly installments of $12,500 each. "
                    "Late payments shall accrue interest at the rate of 1% per month. "
                    "Licensor shall not suspend access to the Software for late payment "
                    "until at least thirty (30) days after written notice of delinquency."
                ),
            },
            {
                "index": 3,
                "heading": "4. SERVICE LEVEL AGREEMENT",
                "text": (
                    "Licensor shall maintain a minimum service availability of 99.9% "
                    "measured on a calendar month basis for cloud-hosted instances. In the "
                    "event of downtime exceeding the SLA, Licensee shall receive a service "
                    "credit of 10% of the monthly fee for each full 0.1% below the target, "
                    "up to a maximum credit of 100% of the monthly fee. Scheduled "
                    "maintenance windows (Sundays 2-6 AM ET) are excluded from uptime "
                    "calculations."
                ),
            },
            {
                "index": 4,
                "heading": "5. INTELLECTUAL PROPERTY",
                "text": (
                    "Licensee acknowledges that the Software, including all source code, "
                    "object code, algorithms, databases, documentation, and related "
                    "materials, is and shall remain the exclusive property of Licensor. "
                    "Nothing in this Agreement shall be construed as granting Licensee any "
                    "rights beyond the limited license expressly granted herein. Licensee "
                    "shall not decompile, disassemble, or reverse-engineer the Software."
                ),
            },
            {
                "index": 5,
                "heading": "6. TERMINATION",
                "text": (
                    "Either party may terminate this Agreement upon thirty (30) days' "
                    "written notice. In the event of a material breach by either party, "
                    "the non-breaching party may terminate upon fifteen (15) days' written "
                    "notice if the breach remains uncured. Upon termination, Licensee "
                    "shall cease using the Software and destroy all copies within fourteen "
                    "(14) days. Licensor shall provide reasonable assistance in data "
                    "export at no additional charge."
                ),
            },
            {
                "index": 6,
                "heading": "7. LIMITATION OF LIABILITY",
                "text": (
                    "Licensor's total aggregate liability arising from this Agreement "
                    "shall not exceed the total license fees paid during the twelve (12) "
                    "months preceding the event giving rise to the claim. Neither party "
                    "shall be liable for indirect, incidental, special, or consequential "
                    "damages, including lost profits, data loss, or business interruption."
                ),
            },
        ],
        "revised_sections": [
            {
                "index": 0,
                "heading": "1. GRANT OF LICENSE",
                "text": (
                    "Licensor hereby grants to Licensee a non-exclusive, non-transferable "
                    "license to use the DataStream Analytics Platform (the 'Software') for "
                    "Licensee's internal business purposes. The license shall cover up to "
                    "one hundred and fifty (150) named users across Licensee's primary "
                    "office location only. Licensee may access the Software exclusively "
                    "via Licensor's cloud infrastructure; on-premises installation is not "
                    "permitted without a separate Enterprise License."
                ),
            },
            {
                "index": 1,
                "heading": "2. LICENSE FEE",
                "text": (
                    "Licensee shall pay an annual license fee of $75,000, due within "
                    "thirty (30) days of the commencement of each license year. The fee "
                    "includes standard technical support during business hours (9 AM – "
                    "5 PM ET, Monday through Friday), software updates, and access to "
                    "Licensor's online knowledge base. Premium 24/7 support is available "
                    "for an additional $18,000 per year."
                ),
            },
            {
                "index": 2,
                "heading": "3. PAYMENT TERMS",
                "text": (
                    "All payments shall be made in United States Dollars within thirty (30) "
                    "days of receipt of invoice (Net-30). Licensee shall pay annually in "
                    "advance; quarterly installment options are no longer available. "
                    "Late payments shall accrue interest at the rate of 2% per month. "
                    "Licensor reserves the right to immediately suspend access to the "
                    "Software upon any late payment without prior notice."
                ),
            },
            {
                "index": 3,
                "heading": "4. SERVICE LEVEL AGREEMENT",
                "text": (
                    "Licensor shall use commercially reasonable efforts to maintain "
                    "service availability of 99.5% measured on a calendar month basis for "
                    "cloud-hosted instances. In the event of downtime exceeding the SLA, "
                    "Licensee shall receive a service credit of 5% of the monthly fee for "
                    "each full 0.5% below the target, up to a maximum credit of 25% of "
                    "the monthly fee. Scheduled maintenance windows are excluded from "
                    "uptime calculations and may be scheduled at Licensor's discretion."
                ),
            },
            {
                "index": 4,
                "heading": "5. INTELLECTUAL PROPERTY",
                "text": (
                    "Licensee acknowledges that the Software, including all source code, "
                    "object code, algorithms, databases, documentation, and related "
                    "materials, is and shall remain the exclusive property of Licensor. "
                    "Nothing in this Agreement shall be construed as granting Licensee any "
                    "rights beyond the limited license expressly granted herein. Licensee "
                    "shall not decompile, disassemble, or reverse-engineer the Software "
                    "or attempt to derive source code from any compiled components."
                ),
            },
            {
                "index": 5,
                "heading": "6. TERMINATION",
                "text": (
                    "Licensor may terminate this Agreement upon thirty (30) days' written "
                    "notice. Licensee may terminate upon ninety (90) days' written notice "
                    "and payment of an early termination fee equal to 50% of the remaining "
                    "license fees for the current term. Upon termination, Licensee shall "
                    "cease using the Software and destroy all copies within seven (7) "
                    "days. Data export assistance shall be provided at Licensor's standard "
                    "professional services rate of $300 per hour."
                ),
            },
            {
                "index": 6,
                "heading": "7. LIMITATION OF LIABILITY",
                "text": (
                    "Licensor's total aggregate liability arising from this Agreement "
                    "shall not exceed the total license fees paid during the six (6) "
                    "months preceding the event giving rise to the claim. Neither party "
                    "shall be liable for indirect, incidental, special, or consequential "
                    "damages, including lost profits, data loss, or business interruption."
                ),
            },
        ],
        "ground_truth_changes": [
            {
                "section_index": 0,
                "change_type": "modified",
                "original_text": "two hundred and fifty (250) named users across all Licensee office locations",
                "revised_text": "one hundred and fifty (150) named users across Licensee's primary office location only",
                "impact": "unfavorable",
                "significance": "high",
                "ideal_amendment": "Restore original 250 user count and multi-location access; offer tiered pricing for additional locations.",
                "amendment_keywords": ["restore", "250 users", "multi-location", "tiered", "scale"],
            },
            {
                "section_index": 1,
                "change_type": "modified",
                "original_text": "annual license fee of $50,000",
                "revised_text": "annual license fee of $75,000",
                "impact": "unfavorable",
                "significance": "high",
                "ideal_amendment": "Propose phased increase: $55,000 Year 1, $65,000 Year 2, with cap at $70,000; tie increases to CPI index.",
                "amendment_keywords": ["phased", "gradual", "cap", "incremental", "CPI"],
            },
            {
                "section_index": 2,
                "change_type": "modified",
                "original_text": "sixty (60) days of receipt of invoice (Net-60)",
                "revised_text": "thirty (30) days of receipt of invoice (Net-30)",
                "impact": "unfavorable",
                "significance": "medium",
                "ideal_amendment": "Compromise at Net-45 payment terms; retain quarterly installment option for cash flow flexibility.",
                "amendment_keywords": ["Net-45", "compromise", "quarterly", "installment", "cash flow"],
            },
            {
                "section_index": 3,
                "change_type": "modified",
                "original_text": "99.9% ... service credit of 10%",
                "revised_text": "99.5% ... service credit of 5%",
                "impact": "unfavorable",
                "significance": "high",
                "ideal_amendment": "Maintain 99.9% SLA target; restore original 10% credit per 0.1% below target with 100% max credit.",
                "amendment_keywords": ["99.9%", "restore SLA", "uptime", "credit", "service level"],
            },
            {
                "section_index": 4,
                "change_type": "modified",
                "original_text": "shall not decompile, disassemble, or reverse-engineer the Software",
                "revised_text": "shall not decompile, disassemble, or reverse-engineer the Software or attempt to derive source code",
                "impact": "neutral",
                "significance": "low",
                "ideal_amendment": None,
                "amendment_keywords": [],
            },
            {
                "section_index": 5,
                "change_type": "modified",
                "original_text": "Either party may terminate ... upon thirty (30) days' written notice ... data export at no additional charge",
                "revised_text": "Licensee may terminate upon ninety (90) days' notice and payment of early termination fee ... data export at $300/hour",
                "impact": "unfavorable",
                "significance": "high",
                "ideal_amendment": "Restore mutual 30-day termination right; eliminate early termination fee; keep free data export or cap export costs at $5,000.",
                "amendment_keywords": ["mutual termination", "30 days", "no fee", "free export", "restore"],
            },
        ],
        "summary_key_points": [
            "License fee increased by 50% from $50,000 to $75,000",
            "User count reduced from 250 to 150 and restricted to single location",
            "Payment terms shortened from Net-60 to Net-30 with higher late penalty",
            "SLA uptime reduced from 99.9% to 99.5% with lower service credits",
            "Termination rights became asymmetric with early termination fee added",
            "New reverse-engineering restriction clause strengthened",
        ],
    },

    # ═══════════════════════════════════════════════════════
    # PAIR 2: Office Lease — MetroSpaces Commercial Realty
    # ═══════════════════════════════════════════════════════
    {
        "pair_id": "compare_002",
        "title": "Commercial Office Lease Agreement — MetroSpaces Realty",
        "parties": {"landlord": "MetroSpaces Commercial Realty LLC", "tenant": "Vertex Digital Solutions Inc."},
        "original_sections": [
            {
                "index": 0,
                "heading": "1. PREMISES",
                "text": (
                    "Landlord hereby leases to Tenant approximately 8,500 square feet of "
                    "office space located on the 14th floor of One MetroCenter Tower, "
                    "450 Park Avenue, New York, NY 10022 (the 'Premises'). The Premises "
                    "include access to common areas, two (2) reserved parking spaces in "
                    "the underground garage, and use of the building's conference facilities "
                    "for up to twenty (20) hours per month at no additional charge."
                ),
            },
            {
                "index": 1,
                "heading": "2. TERM",
                "text": (
                    "The initial lease term shall be sixty (60) months, commencing on "
                    "April 1, 2025 and expiring on March 31, 2030. Tenant shall have the "
                    "option to renew for two (2) successive periods of thirty-six (36) "
                    "months each, exercisable by providing written notice no later than "
                    "one hundred and eighty (180) days prior to the expiration of the "
                    "then-current term. Renewal rates shall be at the then-prevailing "
                    "market rate, but in no event more than 5% above the prior term rate."
                ),
            },
            {
                "index": 2,
                "heading": "3. BASE RENT",
                "text": (
                    "Tenant shall pay base rent of $72 per square foot per annum "
                    "($612,000 annually / $51,000 monthly) during the initial term. "
                    "Rent shall increase by 3% annually on each anniversary of the "
                    "commencement date. The first month's rent and a security deposit "
                    "equal to two (2) months' rent ($102,000) shall be due upon execution "
                    "of this Lease."
                ),
            },
            {
                "index": 3,
                "heading": "4. TENANT IMPROVEMENTS",
                "text": (
                    "Landlord shall provide a tenant improvement allowance of $45 per "
                    "square foot ($382,500 total) for Tenant's build-out of the Premises. "
                    "Tenant shall submit improvement plans for Landlord's approval, which "
                    "shall not be unreasonably withheld, within sixty (60) days of lease "
                    "execution. Any improvement costs exceeding the allowance shall be "
                    "borne by Tenant. All improvements shall become the property of "
                    "Landlord upon lease termination."
                ),
            },
            {
                "index": 4,
                "heading": "5. MAINTENANCE AND REPAIRS",
                "text": (
                    "Landlord shall be responsible for structural maintenance, HVAC "
                    "systems, elevator service, common area cleaning, exterior window "
                    "cleaning, and building security. Tenant shall be responsible for "
                    "interior maintenance of the Premises, including carpet cleaning, "
                    "interior painting, and repair of Tenant-installed fixtures. Landlord "
                    "shall respond to emergency maintenance requests within four (4) "
                    "hours during business hours and eight (8) hours outside business "
                    "hours."
                ),
            },
            {
                "index": 5,
                "heading": "6. ASSIGNMENT AND SUBLETTING",
                "text": (
                    "Tenant may assign this Lease or sublet the Premises, in whole or in "
                    "part, with Landlord's prior written consent, which shall not be "
                    "unreasonably withheld or delayed. Landlord shall respond to any "
                    "assignment or subletting request within fifteen (15) business days. "
                    "In the event of an approved sublease at a rate exceeding the base "
                    "rent, any excess profit shall be shared equally between Landlord and "
                    "Tenant."
                ),
            },
            {
                "index": 6,
                "heading": "7. DEFAULT AND REMEDIES",
                "text": (
                    "If Tenant fails to pay rent within ten (10) days of the due date, "
                    "or breaches any other provision of this Lease that remains uncured "
                    "for thirty (30) days after written notice, Landlord may pursue "
                    "remedies including acceleration of remaining rent, re-entry and "
                    "repossession, and recovery of damages. Landlord shall mitigate "
                    "damages by making reasonable efforts to re-let the Premises."
                ),
            },
        ],
        "revised_sections": [
            {
                "index": 0,
                "heading": "1. PREMISES",
                "text": (
                    "Landlord hereby leases to Tenant approximately 8,500 square feet of "
                    "office space located on the 14th floor of One MetroCenter Tower, "
                    "450 Park Avenue, New York, NY 10022 (the 'Premises'). The Premises "
                    "include access to common areas and one (1) reserved parking space in "
                    "the underground garage. Use of the building's conference facilities "
                    "shall be billed at $150 per hour, subject to availability."
                ),
            },
            {
                "index": 1,
                "heading": "2. TERM",
                "text": (
                    "The initial lease term shall be sixty (60) months, commencing on "
                    "April 1, 2025 and expiring on March 31, 2030. Tenant shall have the "
                    "option to renew for one (1) successive period of twenty-four (24) "
                    "months, exercisable by providing written notice no later than two "
                    "hundred and forty (240) days prior to the expiration of the then-"
                    "current term. Renewal rates shall be at the then-prevailing market "
                    "rate as determined by Landlord's independent appraisal."
                ),
            },
            {
                "index": 2,
                "heading": "3. BASE RENT",
                "text": (
                    "Tenant shall pay base rent of $82 per square foot per annum "
                    "($697,000 annually / $58,083 monthly) during the initial term. "
                    "Rent shall increase by 4.5% annually on each anniversary of the "
                    "commencement date. The first three (3) months' rent and a security "
                    "deposit equal to three (3) months' rent ($174,250) shall be due upon "
                    "execution of this Lease."
                ),
            },
            {
                "index": 3,
                "heading": "4. TENANT IMPROVEMENTS",
                "text": (
                    "Landlord shall provide a tenant improvement allowance of $30 per "
                    "square foot ($255,000 total) for Tenant's build-out of the Premises. "
                    "Tenant shall submit improvement plans for Landlord's approval within "
                    "thirty (30) days of lease execution. Landlord shall have sole "
                    "discretion in approving or rejecting improvement plans. Any "
                    "improvement costs exceeding the allowance shall be borne by Tenant. "
                    "All improvements shall become the property of Landlord upon lease "
                    "termination."
                ),
            },
            {
                "index": 4,
                "heading": "5. MAINTENANCE AND REPAIRS",
                "text": (
                    "Landlord shall be responsible for structural maintenance, HVAC "
                    "systems, elevator service, and building security. Common area "
                    "cleaning, exterior window cleaning, and pest control costs shall be "
                    "passed through to Tenant as additional rent. Tenant shall be "
                    "responsible for all interior maintenance. Landlord shall respond to "
                    "emergency maintenance requests within a reasonable timeframe."
                ),
            },
            {
                "index": 5,
                "heading": "6. ASSIGNMENT AND SUBLETTING",
                "text": (
                    "Tenant may assign this Lease or sublet the Premises, in whole or in "
                    "part, only with Landlord's prior written consent, which may be "
                    "withheld at Landlord's sole discretion. Landlord shall respond to any "
                    "assignment or subletting request within forty-five (45) business "
                    "days. In the event of an approved sublease, all sublease proceeds "
                    "exceeding Tenant's base rent obligation shall be paid to Landlord."
                ),
            },
            {
                "index": 6,
                "heading": "7. DEFAULT AND REMEDIES",
                "text": (
                    "If Tenant fails to pay rent within five (5) days of the due date, "
                    "or breaches any other provision of this Lease that remains uncured "
                    "for fifteen (15) days after written notice, Landlord may pursue "
                    "remedies including acceleration of remaining rent, re-entry and "
                    "repossession, and recovery of damages. Landlord shall have no "
                    "obligation to mitigate damages or re-let the Premises."
                ),
            },
        ],
        "ground_truth_changes": [
            {
                "section_index": 0,
                "change_type": "modified",
                "original_text": "two (2) reserved parking spaces ... conference facilities for up to twenty (20) hours per month at no additional charge",
                "revised_text": "one (1) reserved parking space ... conference facilities shall be billed at $150 per hour",
                "impact": "unfavorable",
                "significance": "medium",
                "ideal_amendment": "Restore two parking spaces; include 10 hours/month free conference room use with additional hours at $100/hr.",
                "amendment_keywords": ["two parking", "restore", "free hours", "conference", "include"],
            },
            {
                "section_index": 1,
                "change_type": "modified",
                "original_text": "two (2) successive periods of thirty-six (36) months ... 180 days ... no more than 5% above",
                "revised_text": "one (1) successive period of twenty-four (24) months ... 240 days ... Landlord's independent appraisal",
                "impact": "unfavorable",
                "significance": "high",
                "ideal_amendment": "Restore two renewal options; maintain 180-day notice period; cap renewal rate at 5% above prior term or CPI, whichever is less.",
                "amendment_keywords": ["two renewals", "180 days", "cap", "5%", "restore options"],
            },
            {
                "section_index": 2,
                "change_type": "modified",
                "original_text": "$72 per square foot ... 3% annually ... two (2) months' rent security deposit",
                "revised_text": "$82 per square foot ... 4.5% annually ... three (3) months' rent security deposit",
                "impact": "unfavorable",
                "significance": "high",
                "ideal_amendment": "Counter at $76/sqft with 3.5% annual escalation; limit security deposit to two months' rent; offer step-up rent in Year 1.",
                "amendment_keywords": ["counter", "$76", "3.5%", "two months", "step-up"],
            },
            {
                "section_index": 3,
                "change_type": "modified",
                "original_text": "$45 per square foot ... not unreasonably withheld ... sixty (60) days",
                "revised_text": "$30 per square foot ... sole discretion ... thirty (30) days",
                "impact": "unfavorable",
                "significance": "high",
                "ideal_amendment": "Restore TI allowance to $45/sqft; change approval standard back to 'not unreasonably withheld'; extend plan submission to 60 days.",
                "amendment_keywords": ["$45", "restore allowance", "reasonable", "60 days", "not unreasonably"],
            },
            {
                "section_index": 4,
                "change_type": "modified",
                "original_text": "common area cleaning, exterior window cleaning ... respond within four (4) hours",
                "revised_text": "common area cleaning, exterior window cleaning costs passed through to Tenant ... respond within reasonable timeframe",
                "impact": "unfavorable",
                "significance": "medium",
                "ideal_amendment": "Common area costs should be included in base rent; define emergency response as 4 hours during business hours, 8 hours after hours.",
                "amendment_keywords": ["include in rent", "define timeframe", "4 hours", "specific SLA"],
            },
            {
                "section_index": 5,
                "change_type": "modified",
                "original_text": "not unreasonably withheld ... fifteen (15) business days ... excess profit shared equally",
                "revised_text": "sole discretion ... forty-five (45) business days ... all excess proceeds to Landlord",
                "impact": "unfavorable",
                "significance": "high",
                "ideal_amendment": "Restore 'not unreasonably withheld' standard; reduce response time to 15 business days; share sublease profit 50/50.",
                "amendment_keywords": ["not unreasonably", "15 days", "50/50", "equal share", "restore"],
            },
            {
                "section_index": 6,
                "change_type": "modified",
                "original_text": "ten (10) days ... thirty (30) days ... reasonable efforts to re-let",
                "revised_text": "five (5) days ... fifteen (15) days ... no obligation to mitigate",
                "impact": "unfavorable",
                "significance": "high",
                "ideal_amendment": "Restore 10-day grace period and 30-day cure period; require Landlord duty to mitigate damages per NY commercial lease law.",
                "amendment_keywords": ["10 days", "30 days", "mitigate", "cure period", "restore"],
            },
        ],
        "summary_key_points": [
            "Base rent increased from $72 to $82 per square foot (14% increase)",
            "Annual rent escalation increased from 3% to 4.5%",
            "Security deposit increased from 2 to 3 months' rent",
            "Tenant improvement allowance reduced from $45 to $30 per square foot",
            "Renewal options reduced from two 36-month terms to one 24-month term",
            "Subletting consent changed from 'not unreasonably withheld' to 'sole discretion'",
            "Landlord removed obligation to mitigate damages upon default",
        ],
    },

    # ═══════════════════════════════════════════════════════
    # PAIR 3: Partnership Agreement — SynergyWorks Ventures
    # ═══════════════════════════════════════════════════════
    {
        "pair_id": "compare_003",
        "title": "Strategic Partnership Agreement — SynergyWorks Ventures",
        "parties": {"partner_a": "NovaTech Robotics Inc.", "partner_b": "SynergyWorks Ventures LLC"},
        "original_sections": [
            {
                "index": 0,
                "heading": "1. PURPOSE AND SCOPE",
                "text": (
                    "The parties enter into this Strategic Partnership Agreement for the "
                    "purpose of jointly developing, manufacturing, and commercializing "
                    "autonomous warehouse robotics solutions. The partnership shall "
                    "encompass collaborative R&D, shared manufacturing facilities, joint "
                    "sales and marketing efforts, and co-development of intellectual "
                    "property. Each party shall contribute its respective expertise: "
                    "NovaTech in robotics hardware and AI systems, SynergyWorks in "
                    "supply chain logistics and market distribution."
                ),
            },
            {
                "index": 1,
                "heading": "2. FINANCIAL CONTRIBUTIONS",
                "text": (
                    "Each party shall contribute $2,000,000 to the joint venture fund "
                    "within ninety (90) days of execution. Additional capital calls may "
                    "be made by unanimous consent of both parties. Revenue from joint "
                    "products shall be split 50/50 after deduction of direct costs and a "
                    "10% management fee. Each party shall bear its own operating expenses "
                    "not directly attributable to joint activities."
                ),
            },
            {
                "index": 2,
                "heading": "3. INTELLECTUAL PROPERTY",
                "text": (
                    "All intellectual property jointly developed under this Agreement "
                    "shall be co-owned by both parties, with each party receiving an "
                    "equal, undivided interest. Each party may independently license "
                    "jointly developed IP to third parties, subject to written notice to "
                    "the other party and a thirty (30) day consultation period. Background "
                    "IP contributed by each party shall remain the exclusive property of "
                    "the contributing party."
                ),
            },
            {
                "index": 3,
                "heading": "4. GOVERNANCE",
                "text": (
                    "The partnership shall be governed by a Joint Steering Committee "
                    "consisting of three (3) representatives from each party. Decisions "
                    "shall be made by majority vote, with each party having equal voting "
                    "weight. The Committee shall meet quarterly and approve annual budgets, "
                    "product roadmaps, and strategic initiatives. Day-to-day operations "
                    "shall be managed by a jointly appointed Operations Director."
                ),
            },
            {
                "index": 4,
                "heading": "5. TERM AND TERMINATION",
                "text": (
                    "This Agreement shall be effective for an initial term of five (5) "
                    "years, with automatic renewal for successive two (2) year periods "
                    "unless either party provides twelve (12) months' written notice of "
                    "non-renewal. Either party may terminate for material breach upon "
                    "sixty (60) days' notice if the breach remains uncured. Upon "
                    "termination, jointly developed IP shall continue to be co-owned and "
                    "each party shall retain a perpetual license to use such IP."
                ),
            },
        ],
        "revised_sections": [
            {
                "index": 0,
                "heading": "1. PURPOSE AND SCOPE",
                "text": (
                    "The parties enter into this Strategic Partnership Agreement for the "
                    "purpose of jointly developing, manufacturing, and commercializing "
                    "autonomous warehouse robotics solutions. The partnership shall "
                    "encompass collaborative R&D, shared manufacturing facilities, joint "
                    "sales and marketing efforts, and co-development of intellectual "
                    "property. SynergyWorks shall serve as the lead partner for all "
                    "commercial and operational decisions, with NovaTech providing "
                    "technical expertise as directed by SynergyWorks."
                ),
            },
            {
                "index": 1,
                "heading": "2. FINANCIAL CONTRIBUTIONS",
                "text": (
                    "NovaTech shall contribute $3,000,000 and SynergyWorks shall "
                    "contribute $1,500,000 to the joint venture fund within sixty (60) "
                    "days of execution. Additional capital calls may be made by "
                    "SynergyWorks with thirty (30) days' notice, and NovaTech shall fund "
                    "60% of any additional capital requirement. Revenue from joint "
                    "products shall be split 55/45 in favor of SynergyWorks after "
                    "deduction of direct costs and a 15% management fee payable to "
                    "SynergyWorks."
                ),
            },
            {
                "index": 2,
                "heading": "3. INTELLECTUAL PROPERTY",
                "text": (
                    "All intellectual property developed under this Agreement shall be "
                    "owned by SynergyWorks, with NovaTech receiving a non-exclusive, "
                    "royalty-bearing license to use jointly developed IP in NovaTech's "
                    "own products, subject to SynergyWorks' prior written approval and "
                    "a royalty of 8% of net sales. Background IP contributed by each "
                    "party shall remain the property of the contributing party, provided "
                    "that SynergyWorks shall receive a perpetual, royalty-free license "
                    "to NovaTech's background IP used in joint products."
                ),
            },
            {
                "index": 3,
                "heading": "4. GOVERNANCE",
                "text": (
                    "The partnership shall be governed by a Joint Steering Committee "
                    "consisting of four (4) representatives from SynergyWorks and two (2) "
                    "from NovaTech. Decisions shall be made by majority vote. The "
                    "Committee shall meet quarterly and approve annual budgets, product "
                    "roadmaps, and strategic initiatives. Day-to-day operations shall be "
                    "managed by an Operations Director appointed by SynergyWorks."
                ),
            },
            {
                "index": 4,
                "heading": "5. TERM AND TERMINATION",
                "text": (
                    "This Agreement shall be effective for an initial term of seven (7) "
                    "years, with automatic renewal for successive three (3) year periods "
                    "unless SynergyWorks provides twelve (12) months' written notice of "
                    "non-renewal. NovaTech may not terminate without SynergyWorks' "
                    "consent except for material uncured breach. Upon termination, all "
                    "jointly developed IP shall remain the exclusive property of "
                    "SynergyWorks, and NovaTech's license shall terminate within ninety "
                    "(90) days."
                ),
            },
        ],
        "ground_truth_changes": [
            {
                "section_index": 0,
                "change_type": "modified",
                "original_text": "Each party shall contribute its respective expertise",
                "revised_text": "SynergyWorks shall serve as lead partner ... NovaTech providing technical expertise as directed",
                "impact": "unfavorable",
                "significance": "high",
                "ideal_amendment": "Restore equal partnership language; define joint decision-making for commercial and operational matters.",
                "amendment_keywords": ["equal", "joint decision", "restore", "mutual", "partnership"],
            },
            {
                "section_index": 1,
                "change_type": "modified",
                "original_text": "$2,000,000 each ... unanimous consent ... 50/50 ... 10% management fee",
                "revised_text": "$3,000,000 NovaTech / $1,500,000 SynergyWorks ... capital calls by SynergyWorks ... 55/45 ... 15% management fee",
                "impact": "unfavorable",
                "significance": "high",
                "ideal_amendment": "Equalize contributions at $2M each; restore 50/50 revenue split; cap management fee at 10%; require unanimous capital call approval.",
                "amendment_keywords": ["equal contribution", "50/50", "10%", "unanimous", "cap fee"],
            },
            {
                "section_index": 2,
                "change_type": "modified",
                "original_text": "co-owned by both parties ... independently license ... background IP remains exclusive",
                "revised_text": "owned by SynergyWorks ... royalty-bearing license ... SynergyWorks gets royalty-free license to NovaTech background IP",
                "impact": "unfavorable",
                "significance": "high",
                "ideal_amendment": "Restore co-ownership of joint IP; eliminate royalty on NovaTech's use of joint IP; remove free license to NovaTech's background IP.",
                "amendment_keywords": ["co-ownership", "joint IP", "no royalty", "equal rights", "background IP"],
            },
            {
                "section_index": 3,
                "change_type": "modified",
                "original_text": "three (3) representatives from each party ... equal voting weight ... jointly appointed",
                "revised_text": "four (4) from SynergyWorks and two (2) from NovaTech ... majority vote ... appointed by SynergyWorks",
                "impact": "unfavorable",
                "significance": "high",
                "ideal_amendment": "Restore equal representation (3 per party); require supermajority for major decisions; jointly appoint Operations Director.",
                "amendment_keywords": ["equal representation", "3 each", "supermajority", "joint appointment"],
            },
            {
                "section_index": 4,
                "change_type": "modified",
                "original_text": "five (5) years ... either party may terminate ... co-owned IP ... perpetual license",
                "revised_text": "seven (7) years ... NovaTech may not terminate without consent ... IP to SynergyWorks ... license terminates",
                "impact": "unfavorable",
                "significance": "high",
                "ideal_amendment": "Restore 5-year initial term; allow mutual termination rights; maintain co-ownership of joint IP post-termination.",
                "amendment_keywords": ["5 years", "mutual termination", "co-ownership", "perpetual license", "restore"],
            },
        ],
        "summary_key_points": [
            "Partnership structure changed from equal to SynergyWorks-dominated",
            "NovaTech's financial contribution doubled while SynergyWorks' decreased",
            "Revenue split shifted from 50/50 to 55/45 in favor of SynergyWorks",
            "Joint IP ownership transferred entirely to SynergyWorks",
            "Governance changed to give SynergyWorks majority control",
        ],
    },
]
