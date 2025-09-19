import React, { useEffect, useState } from 'react';
import { getEventos, createEvento, updateEvento, deleteEvento, toggleParticipation } from '../api/eventos';
import { useAuth } from '../context/AuthContext';

export default function EventosPage(){
  const [eventos, setEventos] = useState([]);
  const [form, setForm] = useState({ nombre:'', descripcion:'', fecha:'' });
  const { user } = useAuth();

  useEffect(()=>{ load(); }, []);
  const load = async () => setEventos(await getEventos());

  const save = async () => {
    if (form.id) await updateEvento(form.id, form);
    else await createEvento(form);
    setForm({ nombre:'', descripcion:'', fecha:'' });
    load();
  };

  const remove = async (ev) => {
    if (new Date(ev.fecha) <= new Date()) { alert('Solo se pueden eliminar eventos a futuro'); return; }
    if (window.confirm('Confirma baja física?')) { await deleteEvento(ev.id); load(); }
  };

  const participate = async (ev) => {
    await toggleParticipation(ev.id);
    load();
  };

  return (
    <div className="container">
      <h2>Eventos Solidarios</h2>
      {(user.rol === 'PRESIDENTE' || user.rol === 'COORDINADOR') && (
        <div style={{marginBottom:12}}>
          <input className="input" placeholder="Nombre" value={form.nombre} onChange={e=>setForm({...form, nombre:e.target.value})}/>
          <input className="input" placeholder="Descripción" value={form.descripcion} onChange={e=>setForm({...form, descripcion:e.target.value})}/>
          <input className="input" type="datetime-local" value={form.fecha} onChange={e=>setForm({...form, fecha:e.target.value})}/>
          <div style={{marginTop:8}}>
            <button onClick={save}>{form.id ? 'Guardar' : 'Crear'}</button>
          </div>
        </div>
      )}

      <table>
        <thead><tr><th>Nombre</th><th>Fecha</th><th>Participantes</th><th>Acciones</th></tr></thead>
        <tbody>
          {eventos.map(ev=>(
            <tr key={ev.id}>
              <td>{ev.nombre}</td>
              <td>{new Date(ev.fecha).toLocaleString()}</td>
              <td>{(ev.participantes || []).length}</td>
              <td>
                {(user.rol === 'PRESIDENTE' || user.rol === 'COORDINADOR') && <button onClick={()=>{ setForm({ id:ev.id, nombre:ev.nombre, descripcion:ev.descripcion, fecha: ev.fecha }); window.scrollTo(0,0); }}>Editar</button>}
                {user.rol === 'VOLUNTARIO' && <button onClick={()=>participate(ev)}>{(ev.participantes||[]).some(p=>p.id===user.id) ? 'Quitarme' : 'Participar'}</button>}
                {(user.rol === 'PRESIDENTE' || user.rol === 'COORDINADOR') && <button onClick={()=>remove(ev)}>Baja</button>}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
