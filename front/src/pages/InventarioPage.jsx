import React, { useEffect, useState } from 'react';
import { getItems, createItem, updateItem, deleteItem } from '../api/inventario';

export default function InventarioPage(){
  const [items, setItems] = useState([]);
  const [form, setForm] = useState({ categoria:'ROPA', descripcion:'', cantidad:0 });

  useEffect(()=>{ load(); }, []);
  const load = async () => setItems(await getItems());

  const save = async () => {
    if (form.id) await updateItem(form.id, form);
    else await createItem(form);
    setForm({ categoria:'ROPA', descripcion:'', cantidad:0 });
    load();
  };

  const remove = async (it) => { if (window.confirm('Confirmar baja lógica?')) { await deleteItem(it.id); load(); } };

  return (
    <div className="container">
      <h2>Inventario de Donaciones</h2>
      <div style={{marginBottom:12}}>
        <select value={form.categoria} onChange={e=>setForm({...form, categoria:e.target.value})}>
          <option value="ROPA">ROPA</option>
          <option value="ALIMENTOS">ALIMENTOS</option>
          <option value="JUGUETES">JUGUETES</option>
          <option value="UTILES_ESCOLARES">UTILES_ESCOLARES</option>
        </select>
        <input className="input" placeholder="Descripción" value={form.descripcion} onChange={e=>setForm({...form, descripcion:e.target.value})} />
        <input className="input" type="number" value={form.cantidad} onChange={e=>setForm({...form, cantidad: Number(e.target.value)})} />
        <div style={{marginTop:8}}>
          <button onClick={save}>Guardar</button>
        </div>
      </div>

      <table>
        <thead><tr><th>Categoría</th><th>Desc</th><th>Cantidad</th><th>Acciones</th></tr></thead>
        <tbody>
          {items.map(it=>(
            <tr key={it.id}>
              <td>{it.categoria}</td>
              <td>{it.descripcion}</td>
              <td>{it.cantidad}</td>
              <td>
                <button onClick={()=>setForm({ id:it.id, categoria:it.categoria, descripcion:it.descripcion, cantidad:it.cantidad })}>Editar</button>
                <button onClick={()=>remove(it)}>Baja</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
