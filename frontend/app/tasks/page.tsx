"use client";

import React, { useCallback, useEffect, useState } from "react";
import { authFetch } from "@/lib/authFetch";

interface Task {
  id: string;
  title: string;
  description?: string;
  status: "todo" | "in_progress" | "done";
  priority: string;
  category: string;
  due_date?: string;
  farmer_name?: string;
  is_overdue?: boolean;
}

export default function TasksPage() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [filter, setFilter] = useState("");
  const [title, setTitle] = useState("");
  const [priority, setPriority] = useState("medium");
  const [dueDate, setDueDate] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      setTasks(await authFetch(`/api/tasks${filter ? `?status=${filter}` : ""}`));
      setError("");
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, [filter]);

  useEffect(() => { load(); }, [load]);

  const add = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;
    try {
      await authFetch("/api/tasks", {
        method: "POST",
        body: JSON.stringify({ title, priority, due_date: dueDate || null }),
      });
      setTitle(""); setDueDate("");
      load();
    } catch (e: any) { setError(e.message); }
  };

  const toggle = async (t: Task) => {
    try {
      await authFetch(`/api/tasks/${t.id}`, {
        method: "PATCH",
        body: JSON.stringify({ status: t.status === "done" ? "todo" : "done" }),
      });
      load();
    } catch (e: any) { setError(e.message); }
  };

  const remove = async (t: Task) => {
    if (!confirm(`Delete "${t.title}"?`)) return;
    try { await authFetch(`/api/tasks/${t.id}`, { method: "DELETE" }); load(); }
    catch (e: any) { setError(e.message); }
  };

  return (
    <div className="space-y-6 p-4">
      <h1 className="text-2xl font-semibold">FPO Tasks</h1>
      <form onSubmit={add} className="flex flex-wrap gap-2">
        <input className="flex-1 rounded border px-3 py-2" placeholder="New task…" value={title} onChange={(e) => setTitle(e.target.value)} />
        <select className="rounded border px-2" value={priority} onChange={(e) => setPriority(e.target.value)}>
          <option value="low">Low</option><option value="medium">Medium</option><option value="high">High</option><option value="urgent">Urgent</option>
        </select>
        <input type="date" className="rounded border px-2" value={dueDate} onChange={(e) => setDueDate(e.target.value)} />
        <button className="rounded bg-green-700 px-4 py-2 text-white">Add</button>
      </form>
      <div className="flex gap-2 text-sm">
        {["", "todo", "in_progress", "done"].map((s) => (
          <button key={s} onClick={() => setFilter(s)} className={`rounded px-3 py-1 border ${filter === s ? "bg-green-700 text-white" : ""}`}>
            {s || "all"}
          </button>
        ))}
      </div>
      {error && <p className="text-red-600">{error}</p>}
      {loading ? <p>Loading…</p> : tasks.length === 0 ? <p className="text-gray-500">No tasks.</p> : (
        <ul className="divide-y rounded border">
          {tasks.map((t) => (
            <li key={t.id} className="flex items-center gap-3 p-3">
              <input type="checkbox" checked={t.status === "done"} onChange={() => toggle(t)} />
              <div className="flex-1">
                <p className={t.status === "done" ? "line-through text-gray-500" : ""}>{t.title}</p>
                <p className="text-xs text-gray-500">
                  {t.priority} · {t.category}{t.due_date ? ` · due ${t.due_date}` : ""}{t.farmer_name ? ` · ${t.farmer_name}` : ""}
                  {t.is_overdue && <span className="ml-1 text-red-600">overdue</span>}
                </p>
              </div>
              <button onClick={() => remove(t)} className="text-sm text-red-600">Delete</button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
