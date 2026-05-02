import csv
import json
import os
import sys
from datetime import datetime
from typing import Optional

import psycopg2
from psycopg2.extras import RealDictCursor

from connect import get_connection

def clear():
    os.system("cls" if os.name == "nt" else "clear")


def pause():
    input("\nPress Enter to continue…")


def fmt_row(row: dict) -> str:
    phones = row.get("phones") or []
    phone_str = ", ".join(f"{p['phone']} ({p['type']})" for p in phones) if phones else "—"
    return (
        f"  [{row.get('id')}] {row.get('username', '—')}\n"
        f"       Email   : {row.get('email') or '—'}\n"
        f"       Birthday: {row.get('birthday') or '—'}\n"
        f"       Group   : {row.get('group_name') or '—'}\n"
        f"       Phones  : {phone_str}"
    )


def load_phones(conn, contact_id: int) -> list:
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            "SELECT phone, type FROM phones WHERE contact_id = %s ORDER BY id",
            (contact_id,),
        )
        return cur.fetchall()


def enrich_contacts(conn, rows: list) -> list:
    for row in rows:
        row["phones"] = load_phones(conn, row["id"])
    return rows


def get_or_create_group(conn, group_name: str) -> int:
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM groups WHERE name ILIKE %s", (group_name,))
        result = cur.fetchone()
        if result:
            return result[0]
        
        cur.execute(
            "INSERT INTO groups (name) VALUES (%s) RETURNING id",
            (group_name.capitalize(),),
        )
        new_id = cur.fetchone()[0]
    conn.commit()
    return new_id


def list_groups(conn) -> list:
    with conn.cursor() as cur:
        cur.execute("SELECT id, name FROM groups ORDER BY name")
        return cur.fetchall()

def db_add_phone(conn, contact_name: str, phone: str, phone_type: str):
    with conn.cursor() as cur:
        cur.execute("CALL add_phone(%s, %s, %s)", (contact_name, phone, phone_type))
    conn.commit()
    print(f"  ✓ Phone {phone} ({phone_type}) added to '{contact_name}'.")


def db_move_to_group(conn, contact_name: str, group_name: str):
    with conn.cursor() as cur:
        cur.execute("CALL move_to_group(%s, %s)", (contact_name, group_name))
    conn.commit()
    print(f"  ✓ '{contact_name}' moved to group '{group_name}'.")


def db_search_contacts(conn, query: str) -> list:
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM search_contacts(%s)", (query,))
        rows = cur.fetchall()

    enriched = []
    seen = set()
    for r in rows:
        cid = r["contact_id"]
        if cid in seen:
            continue
        seen.add(cid)
        row = {
            "id":         cid,
            "username":   r["username"],
            "email":      r["email"],
            "birthday":   r["birthday"],
            "group_name": r["group_name"],
            "matched":    r["matched_field"],
        }
        row["phones"] = load_phones(conn, cid)
        enriched.append(row)
    return enriched

SORT_MAP = {
    "name":     "c.username",
    "birthday": "c.birthday",
    "date":     "c.id",
}


def fetch_contacts(
    conn,
    group_name: Optional[str] = None,
    email_query: Optional[str] = None,
    sort_by: str = "name",
    limit: int = 5,
    offset: int = 0,
) -> list:
    order_col = SORT_MAP.get(sort_by, "c.username")
    params = []
    where_clauses = []

    if group_name:
        where_clauses.append("g.name ILIKE %s")
        params.append(group_name)
    if email_query:
        where_clauses.append("c.email ILIKE %s")
        params.append(f"%{email_query}%")

    where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

    sql = f"""
        SELECT c.id, c.username, c.email, c.birthday, g.name AS group_name
        FROM contacts c
        LEFT JOIN groups g ON g.id = c.group_id
        {where_sql}
        ORDER BY {order_col} NULLS LAST
        LIMIT %s OFFSET %s
    """
    params += [limit, offset]

    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(sql, params)
        rows = list(cur.fetchall())

    return enrich_contacts(conn, rows)


def count_contacts(
    conn,
    group_name: Optional[str] = None,
    email_query: Optional[str] = None,
) -> int:
    params = []
    where_clauses = []

    if group_name:
        where_clauses.append("g.name ILIKE %s")
        params.append(group_name)
    if email_query:
        where_clauses.append("c.email ILIKE %s")
        params.append(f"%{email_query}%")

    where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

    sql = f"""
        SELECT COUNT(*)
        FROM contacts c
        LEFT JOIN groups g ON g.id = c.group_id
        {where_sql}
    """
    with conn.cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchone()[0]


def paginated_browse(conn):
    PAGE = 5
    offset = 0

    print("\n── Browse Contacts ──────────────────────────────────")
    print("Leave blank to skip any filter.")

    groups = list_groups(conn)
    print("Available groups:", ", ".join(g[1] for g in groups))
    group_filter = input("Filter by group (or blank): ").strip() or None
    email_filter = input("Search email (or blank): ").strip() or None

    print("Sort by: [1] name  [2] birthday  [3] date added")
    sort_choice = input("Sort choice (default 1): ").strip()
    sort_by = {"1": "name", "2": "birthday", "3": "date"}.get(sort_choice, "name")

    while True:
        clear()
        total = count_contacts(conn, group_filter, email_filter)
        rows = fetch_contacts(conn, group_filter, email_filter, sort_by, PAGE, offset)
        page_num = offset // PAGE + 1
        total_pages = max(1, (total + PAGE - 1) // PAGE)

        print(f"\n── Contacts  (page {page_num}/{total_pages}, total {total}) ─────")
        if not rows:
            print("  (no results)")
        else:
            for r in rows:
                print(fmt_row(r))
                print()

        print("[n] next  [p] prev  [q] quit")
        cmd = input(">> ").strip().lower()

        if cmd == "q":
            break
        elif cmd == "n":
            if offset + PAGE < total:
                offset += PAGE
            else:
                print("  Already on last page.")
                pause()
        elif cmd == "p":
            if offset > 0:
                offset -= PAGE
            else:
                print("  Already on first page.")
                pause()

def export_to_json(conn, filepath: str = "contacts_export.json"):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT c.id, c.username, c.email,
                   c.birthday::TEXT AS birthday,
                   g.name           AS group_name
            FROM contacts c
            LEFT JOIN groups g ON g.id = c.group_id
            ORDER BY c.username
        """)
        rows = list(cur.fetchall())

    for row in rows:
        row["phones"] = [dict(p) for p in load_phones(conn, row["id"])]
        del row["id"]

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2, ensure_ascii=False)

    print(f"  ✓ Exported {len(rows)} contacts to '{filepath}'.")


def import_from_json(conn, filepath: str = "contacts_import.json"):
    if not os.path.exists(filepath):
        print(f"  ✗ File not found: {filepath}")
        return

    with open(filepath, "r", encoding="utf-8") as f:
        records = json.load(f)

    inserted = skipped = overwritten = 0

    for rec in records:
        username = rec.get("username", "").strip()
        if not username:
            print("  ⚠ Skipping record with no username.")
            continue

        email    = rec.get("email") or None
        birthday = rec.get("birthday") or None
        group_nm = rec.get("group_name") or None
        phones   = rec.get("phones", [])

        with conn.cursor() as cur:
            cur.execute("SELECT id FROM contacts WHERE username ILIKE %s", (username,))
            existing = cur.fetchone()

        if existing:
            print(f"\n  Contact '{username}' already exists.")
            action = input("    [s] skip  [o] overwrite: ").strip().lower()
            if action != "o":
                skipped += 1
                continue

            group_id = get_or_create_group(conn, group_nm) if group_nm else None
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE contacts SET email=%s, birthday=%s, group_id=%s WHERE id=%s",
                    (email, birthday, group_id, existing[0]),
                )
                cur.execute("DELETE FROM phones WHERE contact_id=%s", (existing[0],))
                for p in phones:
                    cur.execute(
                        "INSERT INTO phones (contact_id, phone, type) VALUES (%s,%s,%s)",
                        (existing[0], p.get("phone"), p.get("type", "mobile")),
                    )
            conn.commit()
            overwritten += 1

        else:
            group_id = get_or_create_group(conn, group_nm) if group_nm else None
            with conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO contacts (username, email, birthday, group_id)
                       VALUES (%s,%s,%s,%s) RETURNING id""",
                    (username, email, birthday, group_id),
                )
                cid = cur.fetchone()[0]
                for p in phones:
                    cur.execute(
                        "INSERT INTO phones (contact_id, phone, type) VALUES (%s,%s,%s)",
                        (cid, p.get("phone"), p.get("type", "mobile")),
                    )
            conn.commit()
            inserted += 1

    print(f"\n   Import done — inserted: {inserted}, overwritten: {overwritten}, skipped: {skipped}.")

def import_from_csv(conn, filepath: str = "contacts.csv"):
    if not os.path.exists(filepath):
        print(f"   File not found: {filepath}")
        return

    inserted = skipped = errors = 0

    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            username   = row.get("username", "").strip()
            phone      = row.get("phone", "").strip()
            phone_type = row.get("phone_type", "mobile").strip().lower()
            email      = row.get("email", "").strip() or None
            birthday   = row.get("birthday", "").strip() or None
            group_nm   = row.get("group", "").strip() or None

            if not username:
                errors += 1
                continue

            if phone_type not in ("home", "work", "mobile"):
                print(f"  ⚠ '{username}': invalid phone_type '{phone_type}', defaulting to mobile.")
                phone_type = "mobile"

            if birthday:
                try:
                    datetime.strptime(birthday, "%Y-%m-%d")
                except ValueError:
                    print(f"  ⚠ '{username}': invalid birthday '{birthday}', skipping field.")
                    birthday = None

            with conn.cursor() as cur:
                cur.execute("SELECT id FROM contacts WHERE username ILIKE %s", (username,))
                existing = cur.fetchone()

            if existing:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT id FROM phones WHERE contact_id=%s AND phone=%s",
                        (existing[0], phone),
                    )
                    if not cur.fetchone() and phone:
                        cur.execute(
                            "INSERT INTO phones (contact_id, phone, type) VALUES (%s,%s,%s)",
                            (existing[0], phone, phone_type),
                        )
                conn.commit()
                skipped += 1
                continue

            try:
                group_id = get_or_create_group(conn, group_nm) if group_nm else None
                with conn.cursor() as cur:
                    cur.execute(
                        """INSERT INTO contacts (username, email, birthday, group_id)
                           VALUES (%s,%s,%s,%s) RETURNING id""",
                        (username, email, birthday, group_id),
                    )
                    cid = cur.fetchone()[0]
                    if phone:
                        cur.execute(
                            "INSERT INTO phones (contact_id, phone, type) VALUES (%s,%s,%s)",
                            (cid, phone, phone_type),
                        )
                conn.commit()
                inserted += 1
            except Exception as e:
                conn.rollback()
                print(f"  Error inserting '{username}': {e}")
                errors += 1

    print(f"\n   CSV import done — inserted: {inserted}, skipped: {skipped}, errors: {errors}.")

def menu_search(conn):
    print("\n── Search Contacts ───────────────────────────────────")
    query = input("Enter search term (name / email / phone): ").strip()
    if not query:
        return
    results = db_search_contacts(conn, query)
    if not results:
        print("  No contacts found.")
    else:
        print(f"\n  Found {len(results)} contact(s):\n")
        for r in results:
            matched = r.pop("matched", "?")
            print(fmt_row(r) + f"\n       Matched  : {matched}")
            print()
    pause()


def menu_add_phone(conn):
    print("\n── Add Phone Number ──────────────────────────────────")
    name  = input("Contact name: ").strip()
    phone = input("Phone number: ").strip()
    print("Type: [1] mobile  [2] home  [3] work")
    t = {"1": "mobile", "2": "home", "3": "work"}.get(input(">> ").strip(), "mobile")
    try:
        db_add_phone(conn, name, phone, t)
    except psycopg2.Error as e:
        conn.rollback()
        print(f"   {e.pgerror or e}")
    pause()


def menu_move_group(conn):
    print("\n── Move Contact to Group ─────────────────────────────")
    name   = input("Contact name: ").strip()
    groups = list_groups(conn)
    print("Available groups:", ", ".join(g[1] for g in groups))
    group  = input("Group name (or new name): ").strip()
    try:
        db_move_to_group(conn, name, group)
    except psycopg2.Error as e:
        conn.rollback()
        print(f"  {e.pgerror or e}")
    pause()


def menu_export_json(conn):
    print("\n── Export to JSON ────────────────────────────────────")
    path = input("Output file (default: contacts_export.json): ").strip()
    export_to_json(conn, path or "contacts_export.json")
    pause()


def menu_import_json(conn):
    print("\n── Import from JSON ──────────────────────────────────")
    path = input("Input file (default: contacts_import.json): ").strip()
    import_from_json(conn, path or "contacts_import.json")
    pause()


def menu_import_csv(conn):
    print("\n── Import from CSV ───────────────────────────────────")
    path = input("CSV file (default: contacts.csv): ").strip()
    import_from_csv(conn, path or "contacts.csv")
    pause()


MENU = {
    "1": "Browse / filter / paginate",
    "2": "Search  (name / email / phone)",
    "3": "Add phone number to contact",
    "4": "Move contact to group",
    "5": "Export contacts → JSON",
    "6": "Import contacts ← JSON",
    "7": "Import contacts ← CSV",
    "0": "Exit",
}

HANDLERS = {
    "1": paginated_browse,
    "2": menu_search,
    "3": menu_add_phone,
    "4": menu_move_group,
    "5": menu_export_json,
    "6": menu_import_json,
    "7": menu_import_csv,
}

def main():
    try:
        conn = get_connection()
    except psycopg2.OperationalError as e:
        print(f"Could not connect to database: {e}")
        sys.exit(1)

    print("  ✓ Connected to PostgreSQL.")

    while True:
        clear()
        print("\n=== PhoneBook Extended (TSIS 1) ===")
        for key, desc in MENU.items():
            print(f"  [{key}]  {desc}")
        print("===================================")

        choice = input(">> ").strip()

        if choice == "0":
            print("Goodbye!")
            break

        handler = HANDLERS.get(choice)
        if handler:
            try:
                handler(conn)
            except Exception as e:
                print(f"\n  Unexpected error: {e}")
                conn.rollback()
                pause()
        else:
            print("  Invalid choice.")
            pause()

    conn.close()


if __name__ == "__main__":
    main()
