import api from './index';
export const getItems = async () => (await api.get('/inventario')).data;
export const createItem = async (payload) => (await api.post('/inventario', payload)).data;
export const updateItem = async (id, payload) => (await api.put('/inventario/' + id, payload)).data;
export const deleteItem = async (id) => (await api.delete('/inventario/' + id)).data;
