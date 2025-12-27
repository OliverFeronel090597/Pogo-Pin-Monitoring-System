#!/usr/bin/env python3
"""
MailerTest.py

Relaunches itself as Administrator if needed, then uses local Outlook
(COM) to create or send an email to marfrey.oligario@ams-osram.com.

Usage:
    python MailerTest.py           # opens draft in Outlook (default)
    python MailerTest.py --send    # attempts to send silently
"""

import sys
import os
import ctypes
import argparse
import traceback

# Elevation helper ----------------------------------------------------------
def is_running_as_admin() -> bool:
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False

def relaunch_as_admin():
    """Relaunch the current Python executable with admin privileges and same args."""
    python_exe = sys.executable
    params = " ".join([f'"{arg}"' for arg in sys.argv])
    # ShellExecuteW returns an int > 32 on success. We won't wait for it.
    ctypes.windll.shell32.ShellExecuteW(None, "runas", python_exe, params, None, 1)
    # Exit the current (non-elevated) process so the elevated one takes over.
    sys.exit(0)

# Mailer (runs after elevation) ---------------------------------------------
def send_via_outlook(subject: str, body: str, recipient: str, do_send: bool = False) -> None:
    """
    Use local Outlook to either display (draft) or send the mail.
    Raises Exception on failure.
    """
    try:
        import win32com.client as win32  # import here so earlier failures won't break elevation logic
    except Exception as e:
        raise RuntimeError(f"pywin32 is required (win32com). Install with: pip install pywin32. Error: {e}")

    try:
        outlook = win32.Dispatch("Outlook.Application")
    except Exception as e:
        # Common: Access denied (0x80070005) or CreateObject blocked by policy
        raise RuntimeError(f"Failed to create Outlook COM object: {e}")

    try:
        mail = outlook.CreateItem(0)  # 0 = MailItem
        mail.Subject = subject
        mail.Body = body
        mail.To = recipient

        # Try to resolve recipients (helps catch invalid addresses early)
        resolved = mail.Recipients.ResolveAll()
        if not resolved:
            # collect unresolved names for clarity (may raise on access issues)
            try:
                unresolved = [r.Name for r in mail.Recipients if not r.Resolved]
            except Exception:
                unresolved = ["<couldn't enumerate recipients>"]
            raise RuntimeError(f"Unresolved recipient(s): {unresolved}")

        if do_send:
            mail.Send()
            print("✅ Mail sent successfully via local Outlook (silent send).")
        else:
            mail.Display()  # shows draft
            print("✅ Mail opened in Outlook (draft).")
    except Exception as e:
        # Re-raise as RuntimeError for the caller to print nicely
        raise RuntimeError(f"Outlook action failed: {e}")

# CLI and main logic --------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Send mail via local Outlook (auto-elevates).")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--send", action="store_true", help="Send silently (mail.Send()). Requires permissions.")
    group.add_argument("--display", action="store_true", help="Open draft in Outlook (default).")
    parser.add_argument("--subject", type=str, default="Automated Message", help="Email subject")
    parser.add_argument("--body-file", type=str, help="Path to a text file to use as email body (overrides --body).")
    parser.add_argument("--body", type=str, default="Hello Marfrey,\n\nThis is an automated message.\n", help="Email body text")
    args = parser.parse_args()

    # If not elevated, relaunch elevated (do this before importing COM modules)
    if not is_running_as_admin():
        print("Not running as admin — relaunching with elevated privileges...")
        relaunch_as_admin()

    # Now running elevated.
    subject = args.subject
    body = args.body

    if args.body_file:
        if not os.path.exists(args.body_file):
            print(f"Body file not found: {args.body_file}")
            sys.exit(2)
        with open(args.body_file, "r", encoding="utf-8") as f:
            body = f.read()

    recipient = "marfrey.oligario@ams-osram.com"
    do_send = args.send

    try:
        send_via_outlook(subject, body, recipient, do_send)
    except Exception as exc:
        print("❌ Mail failed.")
        print("Reason:", str(exc))
        # Helpful troubleshooting hints
        print("\nTroubleshooting hints:")
        print("  - Ensure Outlook is installed and configured for your user profile.")
        print("  - Run this script as the same user profile that has Outlook open.")
        print("  - If you still see 'Access is denied' or 'Permission denied: CreateObject',")
        print("    your IT has likely blocked COM automation / VBS. In that case use Microsoft Graph API.")
        print("\nFull traceback (for debugging):")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
