import React, { useState } from "react";
import { IconPlus, IconTrash } from "./Icons";

export default function Sidebar({
  records,
  selectedRecordId,
  selectedRecord,
  onSelectRecord,
  onRefresh,
  recordForm,
  setRecordForm,
  onCreatePatient,
  onUpdatePatient,
  onDeletePatient,
  sessions,
  selectedSessionId,
  selectedSession,
  onSelectSession,
  onCreateSession,
  onDeleteSession,
}) {
  const [editing, setEditing] = useState(false);
  const [editForm, setEditForm] = useState(null);

  function startEdit() {
    setEditForm({
      patient_name: selectedRecord.patient_name,
      age: selectedRecord.age,
      gender: selectedRecord.gender,
      medical_history: selectedRecord.medical_history,
    });
    setEditing(true);
  }

  async function saveEdit(event) {
    event.preventDefault();
    await onUpdatePatient(selectedRecord.id, {
      ...editForm,
      age: Number(editForm.age),
    });
    setEditing(false);
  }

  return (
    <aside className="sidebar">
      <section className="panel">
        <div className="panel-header">
          <h2>Patients</h2>
          <button onClick={onRefresh}>Refresh</button>
        </div>

        <select
          aria-label="Select patient"
          value={selectedRecordId}
          onChange={(event) => {
            onSelectRecord(event.target.value);
            setEditing(false);
          }}
        >
          <option value="">Select patient</option>
          {records.map((record) => (
            <option key={record.id} value={record.id}>
              {record.patient_name}
            </option>
          ))}
        </select>

        {selectedRecord && !editing && (
          <div className="patient-card">
            <strong>{selectedRecord.patient_name}</strong>
            <span>
              {selectedRecord.age} yrs · {selectedRecord.gender}
            </span>
            <p>{selectedRecord.medical_history}</p>
            <div className="patient-card-actions">
              <button onClick={startEdit}>Edit</button>
              <button
                className="danger"
                onClick={() => {
                  if (window.confirm(`Delete ${selectedRecord.patient_name}? This cannot be undone.`)) {
                    onDeletePatient(selectedRecord.id);
                  }
                }}
              >
                <IconTrash /> Delete
              </button>
            </div>
          </div>
        )}

        {selectedRecord && editing && (
          <form onSubmit={saveEdit} className="stack compact patient-card">
            <input
              value={editForm.patient_name}
              onChange={(e) => setEditForm({ ...editForm, patient_name: e.target.value })}
              placeholder="Patient name"
              required
            />
            <div className="two-col">
              <input
                type="number"
                value={editForm.age}
                onChange={(e) => setEditForm({ ...editForm, age: e.target.value })}
                placeholder="Age"
                required
              />
              <input
                value={editForm.gender}
                onChange={(e) => setEditForm({ ...editForm, gender: e.target.value })}
                placeholder="Gender"
                required
              />
            </div>
            <textarea
              value={editForm.medical_history}
              onChange={(e) => setEditForm({ ...editForm, medical_history: e.target.value })}
              placeholder="Medical history"
              required
            />
            <div className="patient-card-actions">
              <button className="primary" type="submit">Save changes</button>
              <button type="button" onClick={() => setEditing(false)}>Cancel</button>
            </div>
          </form>
        )}

        <form onSubmit={onCreatePatient} className="stack compact">
          <input
            placeholder="New patient name"
            value={recordForm.patient_name}
            onChange={(event) =>
              setRecordForm({ ...recordForm, patient_name: event.target.value })
            }
            required
          />
          <div className="two-col">
            <input
              placeholder="Age"
              type="number"
              value={recordForm.age}
              onChange={(event) =>
                setRecordForm({ ...recordForm, age: event.target.value })
              }
              required
            />
            <input
              placeholder="Gender"
              value={recordForm.gender}
              onChange={(event) =>
                setRecordForm({ ...recordForm, gender: event.target.value })
              }
              required
            />
          </div>
          <textarea
            placeholder="Medical history"
            value={recordForm.medical_history}
            onChange={(event) =>
              setRecordForm({
                ...recordForm,
                medical_history: event.target.value,
              })
            }
            required
          />
          <button className="primary" type="submit">
            <IconPlus /> Add patient
          </button>
        </form>
      </section>

      <section className="panel">
        <div className="panel-header">
          <h2>Sessions</h2>
          <button onClick={onCreateSession} disabled={!selectedRecordId}>
            <IconPlus /> New
          </button>
        </div>
        <select
          aria-label="Select chat session"
          value={selectedSessionId}
          onChange={(event) => onSelectSession(event.target.value)}
        >
          <option value="">Select session</option>
          {sessions
            .filter(
              (session) =>
                String(session.medical_record_id) === String(selectedRecordId)
            )
            .map((session) => (
              <option key={session.id} value={session.id}>
                {session.title}
              </option>
            ))}
        </select>
        {selectedSession && (
          <div className="patient-card-actions">
            <span className="muted" style={{ fontFamily: "var(--font-mono)", fontSize: 12 }}>
              Session #{selectedSession.id}
            </span>
            <button
              className="danger"
              onClick={() => {
                if (window.confirm("Delete this chat session?")) {
                  onDeleteSession(selectedSession.id);
                }
              }}
            >
              <IconTrash /> Delete
            </button>
          </div>
        )}
      </section>
    </aside>
  );
}
