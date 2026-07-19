import React, { useMemo, useState } from "react";
import { IconPlus, IconSearch, IconTrash, IconUser } from "./Icons";
import EmptyState from "./EmptyState";
import { SkeletonLine } from "./Skeleton";

const emptyRecord = { patient_name: "", age: "", gender: "", medical_history: "" };

export default function PatientsPanel({
  records,
  recordsLoading,
  selectedRecordId,
  onSelectRecord,
  onCreatePatient,
  onUpdatePatient,
  onDeletePatient,
}) {
  const [filter, setFilter] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState(emptyRecord);
  const [editingId, setEditingId] = useState(null);

  const filtered = useMemo(() => {
    const q = filter.trim().toLowerCase();
    if (!q) return records;
    return records.filter((r) => r.patient_name.toLowerCase().includes(q));
  }, [records, filter]);

  function startCreate() {
    setEditingId(null);
    setForm(emptyRecord);
    setShowForm(true);
  }

  function startEdit(record) {
    setEditingId(record.id);
    setForm({
      patient_name: record.patient_name,
      age: record.age,
      gender: record.gender,
      medical_history: record.medical_history,
    });
    setShowForm(true);
  }

  async function submit(event) {
    event.preventDefault();
    const payload = { ...form, age: Number(form.age) };
    if (editingId) {
      await onUpdatePatient(editingId, payload);
    } else {
      await onCreatePatient(payload);
    }
    setShowForm(false);
    setForm(emptyRecord);
    setEditingId(null);
  }

  return (
    <aside className="patients-panel">
      <div className="panel-header">
        <h2>Patients</h2>
        <button className="ghost icon-button" onClick={startCreate}>
          <IconPlus /> Patient
        </button>
      </div>

      <div className="patient-search">
        <IconSearch />
        <input
          value={filter}
          onChange={(event) => setFilter(event.target.value)}
          placeholder="Filter patients"
          aria-label="Filter patients"
        />
      </div>

      {showForm && (
        <form onSubmit={submit} className="stack compact patient-form">
          <input
            placeholder="Patient name"
            value={form.patient_name}
            onChange={(e) => setForm({ ...form, patient_name: e.target.value })}
            required
            autoFocus
          />
          <div className="two-col">
            <input
              placeholder="Age"
              type="number"
              value={form.age}
              onChange={(e) => setForm({ ...form, age: e.target.value })}
              required
            />
            <input
              placeholder="Gender"
              value={form.gender}
              onChange={(e) => setForm({ ...form, gender: e.target.value })}
              required
            />
          </div>
          <textarea
            placeholder="Medical history"
            value={form.medical_history}
            onChange={(e) => setForm({ ...form, medical_history: e.target.value })}
            required
          />
          <div className="patient-card-actions">
            <button className="primary" type="submit">
              {editingId ? "Save changes" : "Add patient"}
            </button>
            <button type="button" onClick={() => setShowForm(false)}>
              Cancel
            </button>
          </div>
        </form>
      )}

      <div className="patient-list">
        {recordsLoading ? (
          <>
            <div className="patient-list-item">
              <SkeletonLine width="60%" />
            </div>
            <div className="patient-list-item">
              <SkeletonLine width="50%" />
            </div>
          </>
        ) : filtered.length === 0 && records.length === 0 ? (
          <div className="first-run">
            <div className="first-run-icon">
              <IconUser />
            </div>
            <p className="first-run-title">Add your first patient</p>
            <p className="muted">
              Each patient gets their own documents, history, and conversation.
            </p>
            <button className="primary" onClick={startCreate}>
              <IconPlus /> Add patient
            </button>
          </div>
        ) : filtered.length === 0 ? (
          <EmptyState icon={<IconUser />} hint="No patients match your filter." />
        ) : (
          filtered.map((record) => (
            <div
              key={record.id}
              className={`patient-list-item${String(record.id) === String(selectedRecordId) ? " active" : ""}`}
            >
              <button className="patient-list-select" onClick={() => onSelectRecord(record.id)}>
                <span className="patient-avatar">{record.patient_name.charAt(0).toUpperCase()}</span>
                <span className="patient-list-text">
                  <span className="patient-list-name">{record.patient_name}</span>
                  <span className="patient-list-meta">
                    {record.age} yrs · {record.gender}
                  </span>
                </span>
              </button>
              <div className="patient-list-actions">
                <button className="ghost icon-button" onClick={() => startEdit(record)} aria-label={`Edit ${record.patient_name}`}>
                  Edit
                </button>
                <button
                  className="ghost icon-button danger"
                  aria-label={`Delete ${record.patient_name}`}
                  onClick={() => {
                    if (window.confirm(`Delete ${record.patient_name}? This cannot be undone.`)) {
                      onDeletePatient(record.id);
                    }
                  }}
                >
                  <IconTrash />
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </aside>
  );
}
