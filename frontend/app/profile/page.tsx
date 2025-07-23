"use client";

import React, { useEffect, useState } from "react";
import { useApp } from "@/components/AppContext";
import { useRouter } from "next/navigation";

const API_BASE = "http://localhost:8000/api";

export default function ProfilePage() {
  const { user, setUser } = useApp();
  const router = useRouter();
  const [accounts, setAccounts] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [emailResults, setEmailResults] = useState<any>(null);

  // Fetch connected accounts
  const fetchAccounts = async () => {
    if (!user?.sessionId) return;
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/user-accounts/`, {
        headers: { Authorization: `Bearer ${user.sessionId}` },
      });
      const data = await res.json();
      if (res.ok) {
        setAccounts(data.accounts || []);
      } else {
        setError(data.detail?.message || "Failed to fetch accounts");
      }
    } catch (e: any) {
      setError("Failed to fetch accounts");
    } finally {
      setLoading(false);
    }
  };

  // Add another account
  const addAnotherAccount = async () => {
    if (!user?.sessionId) return setError("No session");
    setLoading(true);
    setError(null);
    setSuccess(null);
    try {
      const res = await fetch(`${API_BASE}/oauth/add-another-account/initiate`, {
        headers: { Authorization: `Bearer ${user.sessionId}` },
      });
      const data = await res.json();
      if (res.ok) {
        setSuccess("Redirecting to Google OAuth...");
        setTimeout(() => {
          window.location.href = data.authorization_url;
        }, 1000);
      } else {
        setError(data.detail?.message || "Failed to initiate add account");
      }
    } catch (e: any) {
      setError("Failed to initiate add account");
    } finally {
      setLoading(false);
    }
  };

  // Logout
  const logout = async () => {
    if (!user?.sessionId) return setError("No session");
    setLoading(true);
    setError(null);
    setSuccess(null);
    try {
      const res = await fetch(`${API_BASE}/auth/logout?session_id=${user.sessionId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      });
      const data = await res.json();
      if (res.ok) {
        setUser(null);
        localStorage.removeItem("user");
        setSuccess("Logged out successfully");
        setTimeout(() => router.replace("/login"), 1000);
      } else {
        setError(data.detail?.message || "Logout failed");
      }
    } catch (e: any) {
      setError("Logout failed");
    } finally {
      setLoading(false);
    }
  };

  // Fetch emails by account
  const fetchEmailsByAccount = async (email: string) => {
    if (!user?.sessionId) return setError("No session");
    setLoading(true);
    setError(null);
    setSuccess(null);
    setEmailResults(null);
    try {
      const res = await fetch(`${API_BASE}/emails/fetch-by-account`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${user.sessionId}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email }),
      });
      const data = await res.json();
      if (res.ok) {
        setEmailResults(data);
        setSuccess(`Fetched ${data.emails?.length || 0} emails for ${email}`);
      } else {
        setError(data.detail?.message || "Failed to fetch emails");
      }
    } catch (e: any) {
      setError("Failed to fetch emails");
    } finally {
      setLoading(false);
    }
  };

  // Handle OAuth callback for add account
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const isAddAccount = params.get("flow") === "add_account" && params.get("code") && params.get("state");
    if (isAddAccount && user?.sessionId) {
        console.log("isAddAccount", isAddAccount);
        console.log("user.sessionId", user.sessionId);
      setLoading(true);
      setError(null);
      setSuccess(null);
      // POST code and state to backend to add the account
      fetch(`${API_BASE}/oauth/add-another-account`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${user.sessionId}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ code: params.get("code"), state: params.get("state") }),
      })
        .then((res) => res.json().then((data) => ({ ok: res.ok, data })))
        .then(({ ok, data }) => {
          if (ok && data.success) {
            let message = `Account added: ${data.account_added?.email}`;
            if (data.email_import && data.email_import.success) {
              message += `\nImported ${data.email_import.emails_imported} emails`;
              if (data.email_import.emails_summarized) {
                message += ` (${data.email_import.emails_summarized} summarized)`;
              }
            }
            setSuccess(message);
            fetchAccounts();
          } else {
            setError(data.message || data.error || "Failed to add account");
          }
        })
        .catch(() => setError("Failed to add account"))
        .finally(() => {
          setLoading(false);
          // Clean up URL after handling
          window.history.replaceState({}, document.title, window.location.pathname);
        });
    }
    // eslint-disable-next-line
  }, [user?.sessionId]);

  useEffect(() => {
    if (user?.sessionId) fetchAccounts();
    // eslint-disable-next-line
  }, [user?.sessionId]);

  if (!user) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen">
        <div className="text-lg font-semibold">You are not logged in.</div>
      </div>
    );
  }

  return (
    <div className="max-w-xl mx-auto mt-10 p-6 bg-white rounded-xl shadow-md border flex flex-col gap-6">
      <h2 className="text-2xl font-bold mb-2">Profile</h2>
      <div className="flex flex-col gap-2">
        <div><b>Name:</b> {user.name}</div>
        <div><b>Email:</b> {user.email}</div>
        <div><b>User ID:</b> {user.userId}</div>
        <div><b>Session ID:</b> {user.sessionId}</div>
        {user.profilePicture && (
          <img src={user.profilePicture} alt="Profile" className="w-20 h-20 rounded-full mt-2" />
        )}
      </div>
      <div>
        <h3 className="font-semibold mb-1">Connected Accounts</h3>
        {accounts.length === 0 ? (
          <div>No connected accounts found.</div>
        ) : (
          <ul className="list-disc ml-6">
            {accounts.map((acc: any) => (
              <li key={acc.email}>
                {acc.email} {acc.is_primary ? "(Primary)" : "(Secondary)"} {acc.is_active ? "- Active" : "- Inactive"}
                <button
                  className="ml-2 text-blue-600 underline text-xs"
                  onClick={() => fetchEmailsByAccount(acc.email)}
                >
                  Fetch Emails
                </button>
              </li>
            ))}
          </ul>
        )}
        <button
          className="mt-3 px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
          onClick={addAnotherAccount}
          disabled={loading}
        >
          Add Another Account
        </button>
      </div>
      <div>
        <button
          className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
          onClick={logout}
          disabled={loading}
        >
          Logout
        </button>
      </div>
      {loading && <div className="text-blue-600">Loading...</div>}
      {error && <div className="text-red-600">{error}</div>}
      {success && <div className="text-green-600 whitespace-pre-line">{success}</div>}
      {emailResults && (
        <div className="mt-4">
          <h4 className="font-semibold">Emails for {emailResults.email}:</h4>
          <div>Total: {emailResults.total_count}</div>
          <ul className="list-disc ml-6">
            {(emailResults.emails || []).slice(0, 5).map((em: any) => (
              <li key={em.id}>{em.subject} ({em.sender})</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
} 