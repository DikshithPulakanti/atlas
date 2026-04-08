-- =============================================================================
-- NovaCRM — PostgreSQL Seed Data
-- B2B SaaS CRM platform mock dataset
-- =============================================================================

BEGIN;

-- ---------------------------------------------------------------------------
-- 1. customers (200 rows)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS customers (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    plan TEXT NOT NULL CHECK (plan IN ('starter', 'professional', 'enterprise')),
    arr NUMERIC(12, 2) NOT NULL,
    industry TEXT NOT NULL,
    employee_count INT NOT NULL,
    country TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    churned_at TIMESTAMPTZ,
    account_manager TEXT NOT NULL
);

-- ---------------------------------------------------------------------------
-- 2. support_tickets (2000 rows)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS support_tickets (
    id SERIAL PRIMARY KEY,
    customer_id INT NOT NULL REFERENCES customers(id),
    subject TEXT NOT NULL,
    priority TEXT NOT NULL CHECK (priority IN ('low', 'medium', 'high', 'critical')),
    status TEXT NOT NULL CHECK (status IN ('open', 'in_progress', 'resolved', 'closed')),
    category TEXT NOT NULL CHECK (category IN ('billing', 'technical', 'feature_request', 'bug', 'onboarding')),
    created_at TIMESTAMPTZ NOT NULL,
    resolved_at TIMESTAMPTZ
);

-- ---------------------------------------------------------------------------
-- 3. ticket_messages (5000 rows)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS ticket_messages (
    id SERIAL PRIMARY KEY,
    ticket_id INT NOT NULL REFERENCES support_tickets(id),
    sender_type TEXT NOT NULL CHECK (sender_type IN ('customer', 'agent')),
    body TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL
);

-- ---------------------------------------------------------------------------
-- 4. deploy_log (500 rows)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS deploy_log (
    id SERIAL PRIMARY KEY,
    service TEXT NOT NULL,
    version TEXT NOT NULL,
    commit_sha TEXT NOT NULL,
    author TEXT NOT NULL,
    deployed_at TIMESTAMPTZ NOT NULL,
    environment TEXT NOT NULL CHECK (environment IN ('staging', 'production')),
    rollback BOOLEAN NOT NULL DEFAULT FALSE
);

-- ---------------------------------------------------------------------------
-- 5. users (50 rows — NovaCRM internal employees)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    role TEXT NOT NULL CHECK (role IN ('engineer', 'support', 'sales', 'management')),
    department TEXT NOT NULL,
    hire_date DATE NOT NULL
);

-- =============================================================================
-- Helper: generate deterministic pseudo-random data with generate_series
-- =============================================================================

-- Account managers pool
CREATE TEMP TABLE _account_managers (idx INT, name TEXT);
INSERT INTO _account_managers VALUES
    (0, 'Sarah Chen'), (1, 'Marcus Johnson'), (2, 'Priya Patel'),
    (3, 'David Kim'), (4, 'Rachel Torres'), (5, 'James O''Brien'),
    (6, 'Aisha Mohammed'), (7, 'Tom Andersson'), (8, 'Lisa Nakamura'),
    (9, 'Carlos Rivera');

-- Company names pool (200 names)
CREATE TEMP TABLE _company_names (idx INT, name TEXT);
INSERT INTO _company_names VALUES
    (0, 'Acme Corp'), (1, 'TechVista Inc'), (2, 'Meridian Systems'), (3, 'CloudPeak Solutions'),
    (4, 'DataForge Analytics'), (5, 'Pinnacle Health'), (6, 'Quantum Retail'), (7, 'BlueShift Manufacturing'),
    (8, 'Horizon Financial'), (9, 'Apex Dynamics'), (10, 'NorthStar Logistics'), (11, 'CyberWave Security'),
    (12, 'GreenLeaf Energy'), (13, 'Titanium Labs'), (14, 'Cascade Software'), (15, 'Summit Healthcare'),
    (16, 'Velocity Media'), (17, 'IronBridge Capital'), (18, 'Silverline Tech'), (19, 'Redwood Partners'),
    (20, 'Orion Aerospace'), (21, 'Neptune Analytics'), (22, 'Aurora Biotech'), (23, 'Eclipse Digital'),
    (24, 'Frontier AI'), (25, 'Catalyst Ventures'), (26, 'Mosaic Data'), (27, 'Sterling Commerce'),
    (28, 'Vanguard Systems'), (29, 'Nexus Innovations'), (30, 'Pacific Rim Trading'), (31, 'Atlas Robotics'),
    (32, 'Keystone Financial'), (33, 'Ember Technologies'), (34, 'Zenith Pharma'), (35, 'Crimson Software'),
    (36, 'Falcon Industries'), (37, 'Granite Solutions'), (38, 'Cobalt Engineering'), (39, 'Sapphire Health'),
    (40, 'Trident Manufacturing'), (41, 'Phoenix Group'), (42, 'Beacon Analytics'), (43, 'Opal Networks'),
    (44, 'Vertex Solutions'), (45, 'Lunar Labs'), (46, 'Solar Dynamics'), (47, 'Tidal Wave Media'),
    (48, 'Evergreen Consulting'), (49, 'Ironclad Security'), (50, 'Crystal Clear Optics'), (51, 'BrightPath Education'),
    (52, 'CoreLogic Systems'), (53, 'Wavelength Telecom'), (54, 'Stonewall Capital'), (55, 'RapidScale Cloud'),
    (56, 'Nimbus Health'), (57, 'Fortis Group'), (58, 'DigitalBridge Partners'), (59, 'Helix Genomics'),
    (60, 'Prism Analytics'), (61, 'Compass Navigation'), (62, 'Torque Motors'), (63, 'Skyline Properties'),
    (64, 'Basecamp Technologies'), (65, 'Lumen AI'), (66, 'Crestview Investments'), (67, 'Polaris Shipping'),
    (68, 'Whiteboard Labs'), (69, 'BlackRock Minerals'), (70, 'Jade Commerce'), (71, 'Ruby Therapeutics'),
    (72, 'Aether Wireless'), (73, 'Bolt Logistics'), (74, 'Canyon Research'), (75, 'Delta Force Security'),
    (76, 'Echo Systems'), (77, 'Fusion Energy'), (78, 'Gateway Retail'), (79, 'Hive Analytics'),
    (80, 'Insight Medical'), (81, 'JetStream Hosting'), (82, 'Kinetic Solutions'), (83, 'Lighthouse Insurance'),
    (84, 'Magnet Data'), (85, 'Nova Financial'), (86, 'Oxide Semiconductors'), (87, 'Pivot Software'),
    (88, 'Quartz Technologies'), (89, 'Ripple Payments'), (90, 'Spark Innovation'), (91, 'Terra Farms'),
    (92, 'Unity Platforms'), (93, 'Vector Graphics'), (94, 'Warp Drive Labs'), (95, 'Xenon Systems'),
    (96, 'Yield Fintech'), (97, 'Zephyr Airlines'), (98, 'Alpine Manufacturing'), (99, 'Birch Consulting'),
    (100, 'Cedar Health'), (101, 'Dune Analytics'), (102, 'Elm Software'), (103, 'Fern Biotech'),
    (104, 'Grove Retail'), (105, 'Harbor Shipping'), (106, 'Ivy League Edu'), (107, 'Juniper Networks'),
    (108, 'Kite Pharma'), (109, 'Laurel Media'), (110, 'Maple Finance'), (111, 'Nettle Security'),
    (112, 'Oak Industries'), (113, 'Pine Solutions'), (114, 'Quill Publishing'), (115, 'Reed Instruments'),
    (116, 'Sage Consulting'), (117, 'Thorn Robotics'), (118, 'Umber Mining'), (119, 'Vine Agriculture'),
    (120, 'Willow Health'), (121, 'Aspen Digital'), (122, 'Bamboo Construction'), (123, 'Coral Marine'),
    (124, 'Drift Marketing'), (125, 'Epoch Technologies'), (126, 'Flux Energy'), (127, 'Glow Cosmetics'),
    (128, 'Halo Defense'), (129, 'Iris Optics'), (130, 'Jade AI'), (131, 'Karma Social'),
    (132, 'Lotus Wellness'), (133, 'Mist Computing'), (134, 'Neon Advertising'), (135, 'Orbit Space'),
    (136, 'Pulse Healthcare'), (137, 'Quest Gaming'), (138, 'Ridge Construction'), (139, 'Slate Media'),
    (140, 'Tide Logistics'), (141, 'Uplift Education'), (142, 'Vortex Engineering'), (143, 'Wave Audio'),
    (144, 'Axiom Research'), (145, 'Blaze Marketing'), (146, 'Clover Organic'), (147, 'Dawn Solar'),
    (148, 'Edge Computing'), (149, 'Forge Manufacturing'), (150, 'Glide Transport'), (151, 'Haven Insurance'),
    (152, 'Icon Design'), (153, 'Jewel Luxury'), (154, 'Knox Security'), (155, 'Link Telecom'),
    (156, 'Mint Fintech'), (157, 'Nest PropTech'), (158, 'Onyx Mining'), (159, 'Pearl Jewelry'),
    (160, 'Quad Robotics'), (161, 'Rune Gaming'), (162, 'Silk Textiles'), (163, 'Trek Outdoors'),
    (164, 'Umbra Analytics'), (165, 'Vale Resources'), (166, 'Whirl Appliances'), (167, 'Xcel Energy'),
    (168, 'Yonder Travel'), (169, 'Zinc Materials'), (170, 'Arch Partners'), (171, 'Brio Software'),
    (172, 'Cipher Security'), (173, 'Deft Automation'), (174, 'Enso Design'), (175, 'Flint Hardware'),
    (176, 'Grit Construction'), (177, 'Helm Navigation'), (178, 'Iota Sensors'), (179, 'Jolt Electric'),
    (180, 'Keen Analytics'), (181, 'Loom Textiles'), (182, 'Moxie Marketing'), (183, 'Niche Retail'),
    (184, 'Opus Music'), (185, 'Plumb HVAC'), (186, 'Quota Sales'), (187, 'Relay Communications'),
    (188, 'Scout Recruiting'), (189, 'Tempo Staffing'), (190, 'Ursa Defense'), (191, 'Vista Realty'),
    (192, 'Wren Architecture'), (193, 'Yarn Craft'), (194, 'Zeal Fitness'), (195, 'Alloy Metals'),
    (196, 'Brisk Delivery'), (197, 'Coda Music Tech'), (198, 'Dash Logistics'), (199, 'Evo Biotech');

-- Industries / countries / plans
CREATE TEMP TABLE _industries (idx INT, name TEXT);
INSERT INTO _industries VALUES (0,'tech'),(1,'healthcare'),(2,'finance'),(3,'retail'),(4,'manufacturing');

CREATE TEMP TABLE _countries (idx INT, code TEXT);
INSERT INTO _countries VALUES (0,'US'),(1,'US'),(2,'US'),(3,'UK'),(4,'DE'),(5,'JP'),(6,'AU'),(7,'CA'),(8,'FR'),(9,'BR');

CREATE TEMP TABLE _plans (idx INT, name TEXT, arr_min INT, arr_max INT);
INSERT INTO _plans VALUES (0,'starter',1000,25000),(1,'professional',25000,120000),(2,'enterprise',120000,500000);

-- Insert 200 customers
INSERT INTO customers (name, plan, arr, industry, employee_count, country, created_at, churned_at, account_manager)
SELECT
    cn.name,
    p.name,
    p.arr_min + (hashtext(cn.name || 'arr') & 32767)::NUMERIC / 32767 * (p.arr_max - p.arr_min),
    ind.name,
    GREATEST(10, (hashtext(cn.name || 'emp') & 16383) % 10000),
    co.code,
    '2022-01-01'::TIMESTAMPTZ + (interval '1 day' * (abs(hashtext(cn.name || 'date')) % 1095)),
    CASE WHEN abs(hashtext(cn.name || 'churn')) % 100 < 15
         THEN '2024-01-01'::TIMESTAMPTZ + (interval '1 day' * (abs(hashtext(cn.name || 'churndt')) % 365))
         ELSE NULL END,
    am.name
FROM _company_names cn
JOIN _plans p ON p.idx = abs(hashtext(cn.name || 'plan')) % 3
JOIN _industries ind ON ind.idx = abs(hashtext(cn.name || 'ind')) % 5
JOIN _countries co ON co.idx = abs(hashtext(cn.name || 'co')) % 10
JOIN _account_managers am ON am.idx = abs(hashtext(cn.name || 'am')) % 10
ORDER BY cn.idx;

-- ---------------------------------------------------------------------------
-- Ticket subjects and categories
-- ---------------------------------------------------------------------------
CREATE TEMP TABLE _ticket_subjects (idx INT, subject TEXT, category TEXT, priority TEXT);
INSERT INTO _ticket_subjects VALUES
    (0, 'Cannot access dashboard after password reset', 'technical', 'high'),
    (1, 'Invoice discrepancy for last quarter', 'billing', 'medium'),
    (2, 'Request for bulk data export feature', 'feature_request', 'low'),
    (3, 'API rate limiting hitting us too aggressively', 'technical', 'high'),
    (4, 'SSO integration failing with Okta', 'bug', 'critical'),
    (5, 'Need help setting up team workspaces', 'onboarding', 'medium'),
    (6, 'Webhook deliveries are delayed by 10+ minutes', 'bug', 'high'),
    (7, 'Upgrade to enterprise plan pricing question', 'billing', 'low'),
    (8, 'Custom field API returns 500 intermittently', 'bug', 'critical'),
    (9, 'How to configure SAML-based authentication?', 'onboarding', 'medium'),
    (10, 'Reports page shows stale data from yesterday', 'bug', 'high'),
    (11, 'Please add dark mode to the web interface', 'feature_request', 'low'),
    (12, 'Contacts import CSV failing on large files', 'technical', 'medium'),
    (13, 'Billing cycle changed without notification', 'billing', 'high'),
    (14, 'Need training session for new sales team', 'onboarding', 'low'),
    (15, 'Search functionality returns no results', 'bug', 'critical'),
    (16, 'Can we get a dedicated account manager?', 'feature_request', 'low'),
    (17, 'Data sync with Salesforce is broken', 'technical', 'critical'),
    (18, 'Refund request for double-charged subscription', 'billing', 'high'),
    (19, 'Mobile app crashes on contact detail view', 'bug', 'high'),
    (20, 'How do I set up automated email sequences?', 'onboarding', 'medium'),
    (21, 'Pipeline view not updating in real-time', 'technical', 'medium'),
    (22, 'Request for HIPAA compliance documentation', 'feature_request', 'medium'),
    (23, 'Audit log shows unauthorized access attempts', 'technical', 'critical'),
    (24, 'Tax calculation incorrect for EU customers', 'billing', 'high'),
    (25, 'Two-factor authentication not sending codes', 'bug', 'critical'),
    (26, 'Want to integrate with our internal tools via API', 'feature_request', 'low'),
    (27, 'Page load times exceeding 10 seconds', 'technical', 'high'),
    (28, 'Need to downgrade plan mid-cycle', 'billing', 'medium'),
    (29, 'Onboarding checklist items are not saving', 'bug', 'medium');

-- Insert 2000 support tickets
INSERT INTO support_tickets (customer_id, subject, priority, status, category, created_at, resolved_at)
SELECT
    1 + (abs(hashtext(i::TEXT || 'cust')) % 200),
    ts.subject,
    ts.priority,
    (ARRAY['open','in_progress','resolved','closed'])[1 + abs(hashtext(i::TEXT || 'st')) % 4],
    ts.category,
    '2023-01-01'::TIMESTAMPTZ + (interval '1 day' * (abs(hashtext(i::TEXT || 'tdate')) % 730)),
    CASE WHEN abs(hashtext(i::TEXT || 'res')) % 100 < 70
         THEN '2023-01-01'::TIMESTAMPTZ + (interval '1 day' * (abs(hashtext(i::TEXT || 'tdate')) % 730))
              + (interval '1 hour' * (1 + abs(hashtext(i::TEXT || 'rtime')) % 168))
         ELSE NULL END
FROM generate_series(1, 2000) AS i
JOIN _ticket_subjects ts ON ts.idx = abs(hashtext(i::TEXT || 'subj')) % 30;

-- ---------------------------------------------------------------------------
-- Ticket messages pool
-- ---------------------------------------------------------------------------
CREATE TEMP TABLE _messages (idx INT, sender_type TEXT, body TEXT);
INSERT INTO _messages VALUES
    -- Customer messages: complaints
    (0, 'customer', 'This is extremely frustrating. We''ve been dealing with this issue for over a week now and it''s impacting our entire sales team. We need this resolved ASAP.'),
    (1, 'customer', 'Hi, we noticed this issue started occurring after your last platform update. Our team can no longer complete their daily workflows. Can someone look into this urgently?'),
    (2, 'customer', 'I''m really disappointed with the service quality lately. We''re paying enterprise rates and getting startup-level support. Please escalate this to your engineering team.'),
    (3, 'customer', 'This bug is causing us to lose deals. Every time our reps try to update a contact, the page freezes. We need a hotfix deployed today.'),
    (4, 'customer', 'We''ve tried all the troubleshooting steps in your docs and nothing works. The error persists across all browsers and devices. Please advise.'),
    -- Customer messages: questions
    (5, 'customer', 'Hey, quick question — is there a way to set up automated follow-up sequences for leads that haven''t responded in 7 days? I can''t find it in the settings.'),
    (6, 'customer', 'We''re evaluating whether to upgrade to the professional plan. Could you provide a detailed comparison of what additional features we''d get?'),
    (7, 'customer', 'Our finance team is asking about the data retention policy. How long do you keep deleted records before they''re permanently purged?'),
    (8, 'customer', 'Is it possible to restrict API access by IP address? We want to lock down our integration endpoints for security compliance.'),
    (9, 'customer', 'We have a new team member starting Monday. What''s the best way to set up their account with the right permissions from day one?'),
    -- Customer messages: positive
    (10, 'customer', 'Just wanted to say thanks — the new reporting dashboard is fantastic. Our management team loves the real-time pipeline visibility.'),
    (11, 'customer', 'The bulk import feature you released last month saved us about 20 hours of manual data entry. Great work!'),
    (12, 'customer', 'I appreciate the quick turnaround on this. Your support team is one of the reasons we renewed our contract.'),
    -- Agent messages: acknowledgments
    (13, 'agent', 'Thank you for reaching out. I understand this is impacting your workflow and I''m prioritizing this with our engineering team. I''ll have an update for you within 2 hours.'),
    (14, 'agent', 'I''ve reproduced the issue on our end and have created an internal ticket (ENG-4521). Our backend team is investigating the root cause now.'),
    (15, 'agent', 'Apologies for the inconvenience. I''ve escalated this to our senior engineering team. In the meantime, here''s a workaround you can try...'),
    -- Agent messages: solutions
    (16, 'agent', 'Good news — we''ve identified the issue. It was caused by a cache invalidation bug in our latest release. A fix has been deployed to production. Could you try again and confirm it''s working?'),
    (17, 'agent', 'I''ve applied a configuration change to your account that should resolve this. Please clear your browser cache and try logging in again. Let me know if the issue persists.'),
    (18, 'agent', 'The feature you''re looking for is available under Settings > Automation > Sequences. I''ve attached a step-by-step guide. Feel free to reach out if you need further help.'),
    (19, 'agent', 'I''ve processed your billing adjustment. You should see the corrected amount on your next invoice. The credit of $450 has been applied to your account.'),
    -- Agent messages: follow-ups
    (20, 'agent', 'Hi, just following up on this ticket. Has the issue been resolved on your end? If everything looks good, I''ll go ahead and close this out.'),
    (21, 'agent', 'Wanted to check in — our engineering team deployed a fix yesterday. Could you verify the functionality is working as expected now?'),
    (22, 'agent', 'I see this ticket has been open for a while. I want to make sure we haven''t missed anything. Are you still experiencing the problem?'),
    -- Customer messages: technical detail
    (23, 'customer', 'Here''s what we''re seeing: POST /api/v2/contacts returns 500 with body {"error":"internal_server_error","request_id":"req_8f3a2b"}. This happens about 30% of the time, seems random.'),
    (24, 'customer', 'We ran a trace on our end. The API call to your webhook endpoint times out after 30 seconds. Our server responds within 200ms so the issue is on your side.'),
    (25, 'customer', 'Attached our HAR file showing the network requests. The /graphql endpoint is returning 429 errors even though we''re well under our rate limit of 1000 req/min.'),
    (26, 'customer', 'The CSV import fails at row 4,521 every time. We''ve verified the data format is correct. File size is 12MB. Smaller files under 5MB work fine.'),
    (27, 'customer', 'Our SSO redirect is failing with error code SAMLResponse_Invalid. We''ve double-checked our IdP configuration against your documentation.'),
    -- Agent messages: technical
    (28, 'agent', 'I''ve checked our logs for your account. The 500 errors correlate with a database connection pool exhaustion we experienced between 14:00-16:00 UTC. This has been patched.'),
    (29, 'agent', 'Looking at your API usage, you''re hitting a secondary rate limit on the /contacts endpoint specifically. I''ve increased your per-endpoint limit to 500 req/min. The global limit remains at 1000.');

-- Insert 5000 ticket messages
INSERT INTO ticket_messages (ticket_id, sender_type, body, created_at)
SELECT
    1 + (abs(hashtext(i::TEXT || 'tid')) % 2000),
    m.sender_type,
    m.body,
    '2023-01-01'::TIMESTAMPTZ + (interval '1 day' * (abs(hashtext(i::TEXT || 'mdate')) % 730))
        + (interval '1 minute' * (abs(hashtext(i::TEXT || 'mmin')) % 1440))
FROM generate_series(1, 5000) AS i
JOIN _messages m ON m.idx = abs(hashtext(i::TEXT || 'msg')) % 30;

-- ---------------------------------------------------------------------------
-- Deploy log (500 rows)
-- ---------------------------------------------------------------------------
CREATE TEMP TABLE _dev_names (idx INT, name TEXT);
INSERT INTO _dev_names VALUES
    (0,'Elena Rodriguez'),(1,'Wei Zhang'),(2,'Alex Thompson'),(3,'Ravi Sharma'),
    (4,'Marie Dubois'),(5,'Kenji Tanaka'),(6,'Olga Petrov'),(7,'Hassan Ali'),
    (8,'Sofia Bergman'),(9,'Chris Okafor');

INSERT INTO deploy_log (service, version, commit_sha, author, deployed_at, environment, rollback)
SELECT
    (ARRAY['api','web','worker','ml-pipeline'])[1 + abs(hashtext(i::TEXT || 'svc')) % 4],
    format('%s.%s.%s',
        1 + abs(hashtext(i::TEXT || 'maj')) % 3,
        abs(hashtext(i::TEXT || 'min')) % 20,
        abs(hashtext(i::TEXT || 'patch')) % 100),
    substr(md5(i::TEXT || 'sha'), 1, 12),
    dn.name,
    '2023-06-01'::TIMESTAMPTZ + (interval '1 day' * (abs(hashtext(i::TEXT || 'ddate')) % 600))
        + (interval '1 minute' * (abs(hashtext(i::TEXT || 'dmin')) % 600)),
    (ARRAY['staging','production'])[1 + abs(hashtext(i::TEXT || 'env')) % 2],
    abs(hashtext(i::TEXT || 'rb')) % 100 < 5
FROM generate_series(1, 500) AS i
JOIN _dev_names dn ON dn.idx = abs(hashtext(i::TEXT || 'dev')) % 10;

-- ---------------------------------------------------------------------------
-- Users — NovaCRM internal employees (50 rows)
-- ---------------------------------------------------------------------------
INSERT INTO users (name, email, role, department, hire_date) VALUES
    ('Alice Chen', 'alice.chen@novacrm.io', 'engineer', 'Backend', '2021-03-15'),
    ('Bob Martinez', 'bob.martinez@novacrm.io', 'engineer', 'Backend', '2021-06-01'),
    ('Carol Williams', 'carol.williams@novacrm.io', 'engineer', 'Frontend', '2021-08-20'),
    ('Daniel Kim', 'daniel.kim@novacrm.io', 'engineer', 'Frontend', '2022-01-10'),
    ('Emily Johnson', 'emily.johnson@novacrm.io', 'engineer', 'Infrastructure', '2020-11-01'),
    ('Frank Okafor', 'frank.okafor@novacrm.io', 'engineer', 'Infrastructure', '2022-04-15'),
    ('Grace Liu', 'grace.liu@novacrm.io', 'engineer', 'Data', '2022-07-01'),
    ('Henry Patel', 'henry.patel@novacrm.io', 'engineer', 'Data', '2023-01-20'),
    ('Irene Dubois', 'irene.dubois@novacrm.io', 'engineer', 'ML', '2022-09-10'),
    ('Jack Thompson', 'jack.thompson@novacrm.io', 'engineer', 'ML', '2023-03-01'),
    ('Karen Yamamoto', 'karen.yamamoto@novacrm.io', 'engineer', 'Backend', '2023-05-15'),
    ('Leo Rossi', 'leo.rossi@novacrm.io', 'engineer', 'Backend', '2023-08-01'),
    ('Maria Santos', 'maria.santos@novacrm.io', 'engineer', 'Frontend', '2023-10-01'),
    ('Nathan Singh', 'nathan.singh@novacrm.io', 'engineer', 'Infrastructure', '2024-01-15'),
    ('Olivia Brown', 'olivia.brown@novacrm.io', 'engineer', 'Security', '2022-02-01'),
    ('Paul Schmidt', 'paul.schmidt@novacrm.io', 'support', 'Customer Success', '2021-04-01'),
    ('Quinn Taylor', 'quinn.taylor@novacrm.io', 'support', 'Customer Success', '2021-09-15'),
    ('Rachel Green', 'rachel.green@novacrm.io', 'support', 'Customer Success', '2022-03-01'),
    ('Sam Wilson', 'sam.wilson@novacrm.io', 'support', 'Customer Success', '2022-06-15'),
    ('Tara Nguyen', 'tara.nguyen@novacrm.io', 'support', 'Customer Success', '2022-11-01'),
    ('Uma Krishnan', 'uma.krishnan@novacrm.io', 'support', 'Customer Success', '2023-02-15'),
    ('Victor Petrov', 'victor.petrov@novacrm.io', 'support', 'Technical Support', '2023-06-01'),
    ('Wendy Chang', 'wendy.chang@novacrm.io', 'support', 'Technical Support', '2023-09-01'),
    ('Xavier Lopez', 'xavier.lopez@novacrm.io', 'support', 'Technical Support', '2024-01-01'),
    ('Yuki Sato', 'yuki.sato@novacrm.io', 'support', 'Technical Support', '2024-03-15'),
    ('Sarah Chen', 'sarah.chen@novacrm.io', 'sales', 'Sales', '2021-01-15'),
    ('Marcus Johnson', 'marcus.johnson@novacrm.io', 'sales', 'Sales', '2021-02-01'),
    ('Priya Patel', 'priya.patel@novacrm.io', 'sales', 'Sales', '2021-05-15'),
    ('David Kim', 'david.kim@novacrm.io', 'sales', 'Sales', '2021-10-01'),
    ('Rachel Torres', 'rachel.torres@novacrm.io', 'sales', 'Sales', '2022-01-15'),
    ('James O''Brien', 'james.obrien@novacrm.io', 'sales', 'Sales', '2022-05-01'),
    ('Aisha Mohammed', 'aisha.mohammed@novacrm.io', 'sales', 'Sales', '2022-08-15'),
    ('Tom Andersson', 'tom.andersson@novacrm.io', 'sales', 'Sales', '2023-01-01'),
    ('Lisa Nakamura', 'lisa.nakamura@novacrm.io', 'sales', 'Sales', '2023-04-15'),
    ('Carlos Rivera', 'carlos.rivera@novacrm.io', 'sales', 'Sales', '2023-07-01'),
    ('Diana Foster', 'diana.foster@novacrm.io', 'sales', 'Partnerships', '2022-03-01'),
    ('Erik Lindberg', 'erik.lindberg@novacrm.io', 'sales', 'Partnerships', '2023-01-15'),
    ('Fatima Al-Rashid', 'fatima.alrashid@novacrm.io', 'sales', 'Partnerships', '2023-09-01'),
    ('George Bennett', 'george.bennett@novacrm.io', 'management', 'Engineering', '2020-06-01'),
    ('Helen Park', 'helen.park@novacrm.io', 'management', 'Engineering', '2020-09-15'),
    ('Ivan Volkov', 'ivan.volkov@novacrm.io', 'management', 'Product', '2020-08-01'),
    ('Julia Adams', 'julia.adams@novacrm.io', 'management', 'Product', '2021-01-01'),
    ('Kevin O''Malley', 'kevin.omalley@novacrm.io', 'management', 'Sales', '2020-04-01'),
    ('Linda Wu', 'linda.wu@novacrm.io', 'management', 'Customer Success', '2020-07-15'),
    ('Michael Brown', 'michael.brown@novacrm.io', 'management', 'Finance', '2020-05-01'),
    ('Nina Johansson', 'nina.johansson@novacrm.io', 'management', 'HR', '2021-03-01'),
    ('Oscar Mendez', 'oscar.mendez@novacrm.io', 'management', 'Marketing', '2021-07-01'),
    ('Patricia Hall', 'patricia.hall@novacrm.io', 'management', 'Legal', '2022-01-01'),
    ('Robert Chen', 'robert.chen@novacrm.io', 'management', 'CEO Office', '2019-01-01'),
    ('Sophia Davis', 'sophia.davis@novacrm.io', 'management', 'CTO Office', '2019-03-01');

-- Clean up temp tables
DROP TABLE _account_managers, _company_names, _industries, _countries, _plans,
    _ticket_subjects, _messages, _dev_names;

COMMIT;
