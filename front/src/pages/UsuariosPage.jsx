import React, { useEffect, useState } from 'react';
import { getUsuarios, createUsuario, updateUsuario, deleteUsuario } from '../api/usuarios';

export default function UsuariosPage(){
  const [usuarios, setUsuarios] = useState([]);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState({ username:'', nombre:'', apellido:'', email:'', rol:'VOLUNTARIO', activo:true });

  useEffect(()=>{ load(); }, []);

  const load = async () => {
    const data = await getUsuarios();
    setUsuarios(data);
  };

  const save = async () => {
    if (editing) {
      await updateUsuario(editing.id, form);
    } else {
      await createUsuario(form);
    }
    setForm({ username:'', nombre:'', apellido:'', email:'', rol:'VOLUNTARIO', activo:true });
    setEditing(null);
    load();
  };

  const edit = (u) => { setEditing(u); setForm({ username:u.username, nombre:u.nombre, apellido:u.apellido, email:u.email, rol:u.rol, activo: u.activo }); };
  const remove = async (u) => { if (window.confirm('Confirmar baja lógica?')) { await deleteUsuario(u.id); load(); } };

  return (
    <div className="container">
      <h2>Gestión de Usuarios</h2>
      <div style={{marginBottom:12}}>
        <input className="input" placeholder="Usuario" value={form.username} onChange={e=>setForm({...form, username:e.target.value})} />
        <input className="input" placeholder="Nombre" value={form.nombre} onChange={e=>setForm({...form, nombre:e.target.value})} />
        <input className="input" placeholder="Apellido" value={form.apellido} onChange={e=>setForm({...form, apellido:e.target.value})} />
        <input className="input" placeholder="Email" value={form.email} onChange={e=>setForm({...form, email:e.target.value})} />
        <select value={form.rol} onChange={e=>setForm({...form, rol:e.target.value})}>
          <option value="PRESIDENTE">PRESIDENTE</option>
          <option value="VOCAL">VOCAL</option>
          <option value="COORDINADOR">COORDINADOR</option>
          <option value="VOLUNTARIO">VOLUNTARIO</option>
        </select>
        <label><input type="checkbox" checked={form.activo} onChange={e=>setForm({...form, activo:e.target.checked})}/> Activo</label>
        <div style={{marginTop:8}}>
          <button onClick={save}>{editing ? 'Guardar' : 'Crear'}</button>
          {editing && <button onClick={()=>{setEditing(null); setForm({ username:'', nombre:'', apellido:'', email:'', rol:'VOLUNTARIO', activo:true })}}>Cancelar</button>}
        </div>
      </div>

      <table>
        <thead><tr><th>Usuario</th><th>Nombre</th><th>Email</th><th>Rol</th><th>Activo</th><th>Acciones</th></tr></thead>
        <tbody>
          {usuarios.map(u=>(
            <tr key={u.id}>
              <td>{u.username}</td>
              <td>{u.nombre} {u.apellido}</td>
              <td>{u.email}</td>
              <td>{u.rol}</td>
              <td>{u.activo ? 'Sí' : 'No'}</td>
              <td>
                <button onClick={()=>edit(u)}>Editar</button>
                <button onClick={()=>remove(u)}>Baja</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
