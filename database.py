import sqlite3
import os
from config import Config

def get_db():
    """Returns a SQLite database connection with Row factory enabled."""
    db = sqlite3.connect(Config.DATABASE_PATH, timeout=30.0)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    db.execute("PRAGMA journal_mode = WAL")
    return db

def init_db():
    """Initializes all database tables, foreign keys, indexes, and hierarchical routing schema."""
    os.makedirs(os.path.dirname(Config.DATABASE_PATH), exist_ok=True)
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    
    db = get_db()
    cursor = db.cursor()
    
    cursor.executescript('''
    -- Users Table
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'citizen', -- 'citizen', 'officer', 'admin'
        preferred_lang TEXT NOT NULL DEFAULT 'en', -- 'en', 'te'
        is_approved INTEGER NOT NULL DEFAULT 1, -- 0 for pending officers, 1 for citizens/admin
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Departments Table
    CREATE TABLE IF NOT EXISTS departments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        contact_email TEXT,
        contact_phone TEXT,
        active INTEGER NOT NULL DEFAULT 1
    );

    -- Administrative Jurisdictions Table
    CREATE TABLE IF NOT EXISTS administrative_jurisdictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        type TEXT NOT NULL DEFAULT 'Ward', -- 'Ward', 'Zone', 'District', 'External_Authority'
        parent_id INTEGER,
        contact_officer TEXT,
        helpline TEXT,
        active INTEGER NOT NULL DEFAULT 1,
        FOREIGN KEY (parent_id) REFERENCES administrative_jurisdictions (id)
    );

    -- Authority Profiles Table
    CREATE TABLE IF NOT EXISTS authority_profiles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE NOT NULL,
        department_id INTEGER,
        jurisdiction_id INTEGER,
        hierarchy_tier INTEGER NOT NULL DEFAULT 1, -- 1=Ward Field Officer, 2=Municipal Dept Officer, 3=Dept Head/SE, 4=Commissioner/IAS
        employee_id TEXT,
        designation TEXT,
        approval_status TEXT NOT NULL DEFAULT 'approved', -- 'pending', 'approved', 'rejected'
        approved_by INTEGER,
        approved_at TIMESTAMP,
        rejection_reason TEXT,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
        FOREIGN KEY (department_id) REFERENCES departments (id),
        FOREIGN KEY (jurisdiction_id) REFERENCES administrative_jurisdictions (id)
    );

    -- Hierarchical Routing Rules Table
    CREATE TABLE IF NOT EXISTS hierarchical_routing_rules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL,
        jurisdiction_id INTEGER,
        recommended_dept_id INTEGER,
        primary_handler_tier INTEGER DEFAULT 1, -- 1=Ward Officer, 2=Dept Officer, 3=Dept Head
        is_external_jurisdiction INTEGER DEFAULT 0,
        external_authority_name TEXT,
        escalation_hours_tier_1 INTEGER DEFAULT 4,  -- Hours before moving from Ward to Dept Officer
        escalation_hours_tier_2 INTEGER DEFAULT 12, -- Hours before moving from Dept Officer to Dept Head
        escalation_hours_tier_3 INTEGER DEFAULT 24, -- Hours before moving to Municipal Commissioner
        FOREIGN KEY (jurisdiction_id) REFERENCES administrative_jurisdictions (id),
        FOREIGN KEY (recommended_dept_id) REFERENCES departments (id)
    );

    -- Work Orders Table
    CREATE TABLE IF NOT EXISTS work_orders (
        id TEXT PRIMARY KEY, -- e.g., WO-2026-0001
        department_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        assigned_team TEXT,
        planned_date DATE,
        status TEXT NOT NULL DEFAULT 'Scheduled', -- 'Scheduled', 'In Progress', 'Completed', 'Cancelled'
        estimated_cost REAL DEFAULT 0.0,
        estimated_manpower INTEGER DEFAULT 1,
        materials_required TEXT,
        completion_notes TEXT,
        created_by INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (department_id) REFERENCES departments (id),
        FOREIGN KEY (created_by) REFERENCES users (id)
    );

    -- Complaints Table
    CREATE TABLE IF NOT EXISTS complaints (
        id TEXT PRIMARY KEY, -- e.g., CIVIC-2026-00101
        citizen_id INTEGER NOT NULL,
        category TEXT NOT NULL,
        subcategory TEXT,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        raw_description_te TEXT,
        location_address TEXT NOT NULL,
        latitude REAL NOT NULL,
        longitude REAL NOT NULL,
        ward TEXT DEFAULT 'Ward 12 - Central',
        jurisdiction_id INTEGER,
        status TEXT NOT NULL DEFAULT 'Submitted', -- 'Submitted', 'Under Review', 'Assigned', 'In Progress', 'Resolved', 'Reopened', 'Rejected'
        priority TEXT NOT NULL DEFAULT 'Medium', -- 'Critical', 'High', 'Medium', 'Low'
        department_id INTEGER,
        assigned_officer_id INTEGER,
        work_order_id TEXT,
        current_hierarchy_level INTEGER DEFAULT 1, -- 1=Ward, 2=Dept Officer, 3=Dept Head, 4=Commissioner
        is_external_authority INTEGER DEFAULT 0,
        external_authority_name TEXT,
        acknowledged_at TIMESTAMP,
        acknowledged_by INTEGER,
        citizen_escalation_reason TEXT,
        supervisory_flag INTEGER DEFAULT 0,
        sla_ack_due TIMESTAMP,
        sla_resolve_due TIMESTAMP,
        is_overdue INTEGER DEFAULT 0,
        escalation_level INTEGER DEFAULT 0, -- 0: normal, 1: supervisor, 2: commissioner
        resolution_notes TEXT,
        resolution_photo_hash TEXT,
        citizen_confirmed INTEGER DEFAULT 0,
        citizen_rating INTEGER DEFAULT NULL,
        citizen_feedback TEXT,
        rejection_reason TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (citizen_id) REFERENCES users (id),
        FOREIGN KEY (department_id) REFERENCES departments (id),
        FOREIGN KEY (jurisdiction_id) REFERENCES administrative_jurisdictions (id),
        FOREIGN KEY (assigned_officer_id) REFERENCES users (id),
        FOREIGN KEY (acknowledged_by) REFERENCES users (id),
        FOREIGN KEY (work_order_id) REFERENCES work_orders (id)
    );

    -- Supervisory Instructions & Directives Table
    CREATE TABLE IF NOT EXISTS supervisory_instructions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        complaint_id TEXT NOT NULL,
        supervisor_id INTEGER NOT NULL,
        instruction_type TEXT NOT NULL DEFAULT 'Directive', -- 'Directive', 'Show_Cause_Explanation', 'Expedite_Deadline', 'Field_Inspection_Ordered', 'Return_For_Rework'
        instruction_text TEXT NOT NULL,
        review_deadline TIMESTAMP,
        officer_acknowledged INTEGER DEFAULT 0,
        officer_response TEXT,
        officer_responded_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (complaint_id) REFERENCES complaints (id) ON DELETE CASCADE,
        FOREIGN KEY (supervisor_id) REFERENCES users (id)
    );

    -- Complaint Department Transfers Table
    CREATE TABLE IF NOT EXISTS complaint_transfers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        complaint_id TEXT NOT NULL,
        from_dept_id INTEGER,
        to_dept_id INTEGER NOT NULL,
        transferred_by INTEGER NOT NULL,
        transfer_reason TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'Pending', -- 'Pending', 'Accepted', 'Disputed', 'Resolved_By_Ombudsman'
        dispute_reason TEXT,
        resolved_by INTEGER,
        resolved_notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (complaint_id) REFERENCES complaints (id) ON DELETE CASCADE,
        FOREIGN KEY (from_dept_id) REFERENCES departments (id),
        FOREIGN KEY (to_dept_id) REFERENCES departments (id),
        FOREIGN KEY (transferred_by) REFERENCES users (id),
        FOREIGN KEY (resolved_by) REFERENCES users (id)
    );

    -- Complaint Images Table
    CREATE TABLE IF NOT EXISTS complaint_images (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        complaint_id TEXT NOT NULL,
        filename TEXT NOT NULL,
        file_path TEXT NOT NULL,
        file_hash TEXT NOT NULL,
        image_type TEXT NOT NULL DEFAULT 'evidence', -- 'evidence', 'resolution'
        is_authentic_flag TEXT DEFAULT 'Likely Authentic', -- 'Likely Authentic', 'Possible Synthetic', 'Inconclusive'
        authenticity_confidence REAL DEFAULT 0.90,
        uploaded_by INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (complaint_id) REFERENCES complaints (id) ON DELETE CASCADE,
        FOREIGN KEY (uploaded_by) REFERENCES users (id)
    );

    -- AI Assessments Table
    CREATE TABLE IF NOT EXISTS ai_assessments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        complaint_id TEXT UNIQUE NOT NULL,
        predicted_category TEXT NOT NULL,
        confidence_score REAL NOT NULL,
        risk_score INTEGER NOT NULL, -- 0 to 100
        severity_level TEXT NOT NULL, -- 'Critical', 'High', 'Medium', 'Low'
        recommended_dept_id INTEGER,
        hazard_flags TEXT,
        reasoning TEXT,
        authenticity_assessment TEXT,
        is_overridden INTEGER DEFAULT 0,
        override_by INTEGER,
        override_notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (complaint_id) REFERENCES complaints (id) ON DELETE CASCADE,
        FOREIGN KEY (recommended_dept_id) REFERENCES departments (id)
    );

    -- Status History Table
    CREATE TABLE IF NOT EXISTS status_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        complaint_id TEXT NOT NULL,
        old_status TEXT,
        new_status TEXT NOT NULL,
        changed_by INTEGER,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (complaint_id) REFERENCES complaints (id) ON DELETE CASCADE,
        FOREIGN KEY (changed_by) REFERENCES users (id)
    );

    -- Work Order Tasks Table
    CREATE TABLE IF NOT EXISTS work_order_tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        work_order_id TEXT NOT NULL,
        task_description TEXT NOT NULL,
        is_completed INTEGER DEFAULT 0,
        completed_at TIMESTAMP,
        FOREIGN KEY (work_order_id) REFERENCES work_orders (id) ON DELETE CASCADE
    );

    -- Work Order Complaints Linking Table
    CREATE TABLE IF NOT EXISTS work_order_complaints (
        work_order_id TEXT NOT NULL,
        complaint_id TEXT NOT NULL,
        PRIMARY KEY (work_order_id, complaint_id),
        FOREIGN KEY (work_order_id) REFERENCES work_orders (id) ON DELETE CASCADE,
        FOREIGN KEY (complaint_id) REFERENCES complaints (id) ON DELETE CASCADE
    );

    -- Duplicate Relations Table
    CREATE TABLE IF NOT EXISTS duplicate_relations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        primary_complaint_id TEXT NOT NULL,
        duplicate_complaint_id TEXT NOT NULL,
        similarity_score REAL NOT NULL,
        detection_method TEXT DEFAULT 'proximity_and_text',
        status TEXT DEFAULT 'flagged', -- 'flagged', 'merged', 'dismissed'
        reviewed_by INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (primary_complaint_id) REFERENCES complaints (id),
        FOREIGN KEY (duplicate_complaint_id) REFERENCES complaints (id)
    );

    -- Community Support / Upvotes Table
    CREATE TABLE IF NOT EXISTS community_supports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        complaint_id TEXT NOT NULL,
        user_id INTEGER NOT NULL,
        comment TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE (complaint_id, user_id),
        FOREIGN KEY (complaint_id) REFERENCES complaints (id) ON DELETE CASCADE,
        FOREIGN KEY (user_id) REFERENCES users (id)
    );

    -- Citizen Appeals Table
    CREATE TABLE IF NOT EXISTS appeals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        complaint_id TEXT NOT NULL,
        citizen_id INTEGER NOT NULL,
        appeal_reason TEXT NOT NULL,
        additional_evidence TEXT,
        status TEXT NOT NULL DEFAULT 'Pending Review', -- 'Pending Review', 'Under Investigation', 'Approved', 'Rejected'
        reviewed_by INTEGER,
        reviewer_decision_notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (complaint_id) REFERENCES complaints (id) ON DELETE CASCADE,
        FOREIGN KEY (citizen_id) REFERENCES users (id),
        FOREIGN KEY (reviewed_by) REFERENCES users (id)
    );

    -- Predictive Maintenance Alerts Table
    CREATE TABLE IF NOT EXISTS predictive_alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        category TEXT NOT NULL,
        location_cluster TEXT NOT NULL,
        ward TEXT NOT NULL,
        recurrence_count INTEGER DEFAULT 1,
        risk_level TEXT DEFAULT 'High',
        recommended_action TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'Pending', -- 'Pending', 'Approved', 'Actioned', 'Dismissed'
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Disaster Incidents Table
    CREATE TABLE IF NOT EXISTS disaster_incidents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        incident_name TEXT NOT NULL,
        incident_type TEXT NOT NULL,
        description TEXT,
        severity TEXT NOT NULL DEFAULT 'Severe',
        affected_wards TEXT,
        status TEXT NOT NULL DEFAULT 'Active',
        emergency_hotline TEXT DEFAULT '112 / 1070',
        created_by INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (created_by) REFERENCES users (id)
    );

    -- SLA Escalation Logs Table
    CREATE TABLE IF NOT EXISTS sla_escalation_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        complaint_id TEXT NOT NULL,
        escalation_level INTEGER NOT NULL,
        triggered_reason TEXT NOT NULL,
        escalated_to_role TEXT NOT NULL,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (complaint_id) REFERENCES complaints (id) ON DELETE CASCADE
    );

    -- In-app Notifications Table
    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        message TEXT NOT NULL,
        link TEXT,
        notification_type TEXT DEFAULT 'status_change',
        is_read INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    );

    -- Administrative Jurisdictions Table
    CREATE TABLE IF NOT EXISTS administrative_jurisdictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        type TEXT NOT NULL, -- 'Ward', 'Zone', 'District', 'External_Authority'
        parent_id INTEGER,
        contact_officer TEXT,
        helpline TEXT,
        active INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (parent_id) REFERENCES administrative_jurisdictions (id)
    );

    -- Hierarchical Routing Rules Table
    CREATE TABLE IF NOT EXISTS hierarchical_routing_rules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL,
        jurisdiction_id INTEGER,
        recommended_dept_id INTEGER NOT NULL,
        primary_handler_tier INTEGER DEFAULT 1, -- 1=Ward JE, 2=Dept AEE, 3=Dept Head/SE, 4=Commissioner
        is_external_jurisdiction INTEGER DEFAULT 0,
        external_authority_name TEXT,
        escalation_hours_tier_1 INTEGER DEFAULT 6,
        escalation_hours_tier_2 INTEGER DEFAULT 12,
        escalation_hours_tier_3 INTEGER DEFAULT 24,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (jurisdiction_id) REFERENCES administrative_jurisdictions (id),
        FOREIGN KEY (recommended_dept_id) REFERENCES departments (id)
    );

    -- Supervisory Instructions Table
    CREATE TABLE IF NOT EXISTS supervisory_instructions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        complaint_id TEXT NOT NULL,
        issued_by INTEGER NOT NULL,
        instruction_type TEXT NOT NULL DEFAULT 'Directive', -- 'Directive', 'Show-Cause', 'Field Inspection', 'Reinvestigation', 'Audit Inquiry'
        instruction_text TEXT NOT NULL,
        deadline_at TIMESTAMP,
        is_public_to_citizen INTEGER DEFAULT 1,
        is_responded INTEGER DEFAULT 0,
        compliance_notes TEXT,
        responded_by INTEGER,
        responded_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (complaint_id) REFERENCES complaints (id) ON DELETE CASCADE,
        FOREIGN KEY (issued_by) REFERENCES users (id),
        FOREIGN KEY (responded_by) REFERENCES users (id)
    );

    -- Inter-Department Complaint Transfers Table
    CREATE TABLE IF NOT EXISTS complaint_transfers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        complaint_id TEXT NOT NULL,
        from_department_id INTEGER NOT NULL,
        to_department_id INTEGER NOT NULL,
        initiated_by INTEGER NOT NULL,
        reason TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'Pending', -- 'Pending', 'Accepted', 'Disputed', 'Resolved'
        response_notes TEXT,
        responded_by INTEGER,
        responded_at TIMESTAMP,
        binding_resolution_notes TEXT,
        resolved_by INTEGER,
        resolved_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (complaint_id) REFERENCES complaints (id) ON DELETE CASCADE,
        FOREIGN KEY (from_department_id) REFERENCES departments (id),
        FOREIGN KEY (to_department_id) REFERENCES departments (id),
        FOREIGN KEY (initiated_by) REFERENCES users (id),
        FOREIGN KEY (responded_by) REFERENCES users (id),
        FOREIGN KEY (resolved_by) REFERENCES users (id)
    );

    -- Notification Delivery Logs Table (External & Gov Integration Tracking)
    CREATE TABLE IF NOT EXISTS notification_delivery_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        notification_id INTEGER,
        complaint_id TEXT,
        recipient_id INTEGER,
        channel TEXT NOT NULL DEFAULT 'in_app', -- 'in_app', 'sms', 'email', 'gov_adapter'
        recipient TEXT,
        subject TEXT,
        message_preview TEXT,
        delivery_status TEXT NOT NULL DEFAULT 'delivered', -- 'delivered', 'simulated', 'pending', 'failed'
        status TEXT DEFAULT 'delivered',
        attempt_count INTEGER DEFAULT 1,
        retry_count INTEGER DEFAULT 0,
        last_error TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (notification_id) REFERENCES notifications (id) ON DELETE CASCADE,
        FOREIGN KEY (complaint_id) REFERENCES complaints (id) ON DELETE CASCADE
    );

    -- Audit Logs Table
    CREATE TABLE IF NOT EXISTS audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        action TEXT NOT NULL,
        target_type TEXT NOT NULL,
        target_id TEXT,
        details TEXT,
        ip_address TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    );

    -- System Settings Table
    CREATE TABLE IF NOT EXISTS system_settings (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL
    );

    -- Indexes for performance
    CREATE INDEX IF NOT EXISTS idx_complaints_citizen ON complaints (citizen_id);
    CREATE INDEX IF NOT EXISTS idx_complaints_dept ON complaints (department_id);
    CREATE INDEX IF NOT EXISTS idx_complaints_status ON complaints (status);
    CREATE INDEX IF NOT EXISTS idx_complaints_priority ON complaints (priority);
    CREATE INDEX IF NOT EXISTS idx_complaints_coords ON complaints (latitude, longitude);
    CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications (user_id, is_read);
    CREATE INDEX IF NOT EXISTS idx_work_orders_dept ON work_orders (department_id);
    ''')

    # Apply schema migrations to existing databases
    def add_col_if_missing(table, col, defn):
        cursor.execute(f"PRAGMA table_info({table})")
        existing_cols = [r[1] for r in cursor.fetchall()]
        if col not in existing_cols:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col} {defn}")

    add_col_if_missing('complaints', 'jurisdiction_id', 'INTEGER')
    add_col_if_missing('complaints', 'current_hierarchy_level', 'INTEGER DEFAULT 1')
    add_col_if_missing('complaints', 'is_external_authority', 'INTEGER DEFAULT 0')
    add_col_if_missing('complaints', 'external_authority_name', 'TEXT')
    add_col_if_missing('complaints', 'acknowledged_at', 'TIMESTAMP')
    add_col_if_missing('complaints', 'acknowledged_by', 'INTEGER')
    add_col_if_missing('complaints', 'citizen_escalation_reason', 'TEXT')
    add_col_if_missing('complaints', 'supervisory_flag', 'INTEGER DEFAULT 0')
    add_col_if_missing('authority_profiles', 'hierarchy_tier', 'INTEGER DEFAULT 1')
    add_col_if_missing('authority_profiles', 'jurisdiction_id', 'INTEGER')
    add_col_if_missing('notification_delivery_logs', 'complaint_id', 'TEXT')
    add_col_if_missing('notification_delivery_logs', 'recipient_id', 'INTEGER')
    add_col_if_missing('notification_delivery_logs', 'subject', 'TEXT')
    add_col_if_missing('notification_delivery_logs', 'message_preview', 'TEXT')
    add_col_if_missing('notification_delivery_logs', 'status', 'TEXT DEFAULT "delivered"')
    add_col_if_missing('notification_delivery_logs', 'retry_count', 'INTEGER DEFAULT 0')

    # Media Authenticity and Video Analysis Columns
    add_col_if_missing('complaint_images', 'media_type', "TEXT DEFAULT 'photo'")
    add_col_if_missing('complaint_images', 'video_duration', 'REAL')
    add_col_if_missing('complaint_images', 'video_fps', 'REAL')
    add_col_if_missing('complaint_images', 'frame_count', 'INTEGER')
    add_col_if_missing('complaint_images', 'blur_score', 'REAL')
    add_col_if_missing('complaint_images', 'inconsistencies_detected', 'TEXT')
    add_col_if_missing('complaint_images', 'extracted_keyframes', 'TEXT')
    add_col_if_missing('complaint_images', 'model_name', 'TEXT')
    add_col_if_missing('complaint_images', 'perceptual_hash', 'TEXT')
    add_col_if_missing('complaint_images', 'is_duplicate_flag', 'INTEGER DEFAULT 0')
    add_col_if_missing('complaint_images', 'duplicate_matched_id', 'TEXT')
    add_col_if_missing('complaint_images', 'manual_review_status', "TEXT DEFAULT 'Pending'")
    add_col_if_missing('complaint_images', 'manual_review_notes', 'TEXT')
    add_col_if_missing('complaint_images', 'manual_reviewed_by', 'INTEGER')
    add_col_if_missing('complaint_images', 'manual_reviewed_at', 'TIMESTAMP')

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_complaints_jurisdiction ON complaints (jurisdiction_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_complaints_hierarchy ON complaints (current_hierarchy_level)")

    # Insert default departments if not present
    cursor.execute("SELECT COUNT(*) FROM departments")
    if cursor.fetchone()[0] == 0:
        for dept in Config.DEPARTMENTS:
            cursor.execute('''
                INSERT INTO departments (code, name, description, contact_email, contact_phone, active)
                VALUES (?, ?, ?, ?, ?, 1)
            ''', (dept['code'], dept['name'], f"Responsible for civic issues regarding {', '.join(dept['categories'])}", f"{dept['code'].lower()}@civicshield.gov.in", "+91 40 2345 6789"))

    # Seed default Administrative Jurisdictions
    cursor.execute("SELECT COUNT(*) FROM administrative_jurisdictions")
    if cursor.fetchone()[0] == 0:
        jurisdictions = [
            ("WARD_12", "Ward 12 - Jubilee & Banjara Hills", "Ward", None, "Assistant Engineer Ward 12", "040-23451212"),
            ("WARD_4", "Ward 4 - Begumpet & Secunderabad", "Ward", None, "Assistant Engineer Ward 4", "040-23451414"),
            ("WARD_7", "Ward 7 - Madhapur & Hitec City", "Ward", None, "Assistant Engineer Ward 7", "040-23451717"),
            ("WARD_14", "Ward 14 - Uppal & Dilsukhnagar", "Ward", None, "Assistant Engineer Ward 14", "040-23451919"),
            ("ZONE_CENTRAL", "Greater Central Municipal Zone", "Zone", None, "Zonal Superintending Engineer", "040-23452000"),
            ("EXT_NHAI", "National Highways Authority of India (NHAI)", "External_Authority", None, "Project Director NH-65 / Outer Ring", "1033"),
            ("EXT_TSSPDCL_TRANS", "State Electricity Transmission Grid (TSSPDCL Transco)", "External_Authority", None, "Extra High Tension Grid Officer", "1912"),
            ("EXT_HMRL", "Hyderabad Metro Rail Limited (HMRL)", "External_Authority", None, "Chief Track & Infrastructure Engineer", "040-23332222")
        ]
        for j in jurisdictions:
            cursor.execute('''
                INSERT INTO administrative_jurisdictions (code, name, type, parent_id, contact_officer, helpline, active)
                VALUES (?, ?, ?, ?, ?, ?, 1)
            ''', j)

    # Seed default Hierarchical Routing Rules
    cursor.execute("SELECT COUNT(*) FROM hierarchical_routing_rules")
    if cursor.fetchone()[0] == 0:
        routing_rules = [
            # Potholes -> Roads & Engineering (Dept 1)
            ("Potholes and Damaged Roads", 1, 1, 1, 0, None, 4, 12, 24),
            # Garbage -> Sanitation (Dept 2)
            ("Garbage Accumulation", 1, 2, 1, 0, None, 6, 12, 36),
            # Drainage -> Drainage (Dept 4)
            ("Drainage Blockage", 1, 4, 1, 0, None, 4, 12, 24),
            # Water Leakage -> Water Supply (Dept 3)
            ("Water Leakage", 1, 3, 1, 0, None, 4, 12, 24),
            # Broken Streetlights -> Electricity (Dept 5)
            ("Broken Streetlights", 1, 5, 1, 0, None, 8, 24, 48),
            # Exposed Electrical Wires -> Electricity / Transmission (Dept 5 / External)
            ("Exposed Electrical Wires", 1, 5, 1, 0, None, 2, 6, 12),
            # National Highway Corridors -> External Jurisdiction
            ("National Highway Arterial Damage", 6, 1, 1, 1, "National Highways Authority of India (NHAI)", 2, 6, 12),
            # Metro Rail Corridor Viaduct -> External Jurisdiction
            ("Metro Rail Viaduct / Transit Pillar Hazard", 8, 6, 1, 1, "Hyderabad Metro Rail Limited (HMRL)", 2, 6, 12)
        ]
        for r in routing_rules:
            cursor.execute('''
                INSERT INTO hierarchical_routing_rules (
                    category, jurisdiction_id, recommended_dept_id, primary_handler_tier,
                    is_external_jurisdiction, external_authority_name,
                    escalation_hours_tier_1, escalation_hours_tier_2, escalation_hours_tier_3
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', r)

    # Insert default system settings
    cursor.execute("INSERT OR IGNORE INTO system_settings (key, value) VALUES ('disaster_mode', 'false')")
    cursor.execute("INSERT OR IGNORE INTO system_settings (key, value) VALUES ('portal_version', '2026.2')")
    cursor.execute("INSERT OR IGNORE INTO system_settings (key, value) VALUES ('gov_integration_mode', 'simulated')")
    
    db.commit()
    db.close()

def delete_complaint(complaint_id):
    """
    Safely deletes a complaint and all associated records and evidence files.
    Cleans up dependent tables to satisfy foreign key constraints.
    Returns True if successfully deleted, False if complaint not found or on error.
    """
    db = get_db()
    cursor = db.cursor()
    try:
        # Check if complaint exists
        cursor.execute("SELECT id FROM complaints WHERE id = ?", (complaint_id,))
        if not cursor.fetchone():
            return False

        # Gather image/media files for removal from disk
        cursor.execute("SELECT filename FROM complaint_images WHERE complaint_id = ?", (complaint_id,))
        rows = cursor.fetchall()
        for r in rows:
            fname = r['filename']
            if fname:
                fpath = os.path.join(Config.UPLOAD_FOLDER, fname)
                if os.path.exists(fpath):
                    try:
                        os.remove(fpath)
                    except Exception as e:
                        print(f"Warning: could not delete file {fpath}: {e}")

        # Delete records from dependent tables
        cursor.execute("DELETE FROM duplicate_relations WHERE primary_complaint_id = ? OR duplicate_complaint_id = ?", (complaint_id, complaint_id))
        cursor.execute("DELETE FROM work_order_complaints WHERE complaint_id = ?", (complaint_id,))
        cursor.execute("DELETE FROM supervisory_instructions WHERE complaint_id = ?", (complaint_id,))
        cursor.execute("DELETE FROM complaint_transfers WHERE complaint_id = ?", (complaint_id,))
        cursor.execute("DELETE FROM community_supports WHERE complaint_id = ?", (complaint_id,))
        cursor.execute("DELETE FROM appeals WHERE complaint_id = ?", (complaint_id,))
        cursor.execute("DELETE FROM sla_escalation_logs WHERE complaint_id = ?", (complaint_id,))
        cursor.execute("DELETE FROM notification_delivery_logs WHERE complaint_id = ?", (complaint_id,))
        cursor.execute("DELETE FROM ai_assessments WHERE complaint_id = ?", (complaint_id,))
        cursor.execute("DELETE FROM status_history WHERE complaint_id = ?", (complaint_id,))
        cursor.execute("DELETE FROM complaint_images WHERE complaint_id = ?", (complaint_id,))

        # Delete the complaint record itself
        cursor.execute("DELETE FROM complaints WHERE id = ?", (complaint_id,))
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"Error deleting complaint {complaint_id}: {e}")
        return False
    finally:
        db.close()

if __name__ == '__main__':
    init_db()
    print("CivicShield database initialized with hierarchical authority routing!")
